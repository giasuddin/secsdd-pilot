"""Run BaxBench functional tests and security exploits against generated Flask apps,
without Docker. Each test gets a fresh copy of the app in its own working directory
(mirroring BaxBench's fresh container per test). BaxBench's Docker file helpers are
redirected to that directory ("/app/<f>" -> <workdir>/<f>).

Usage: python scripts/run_tests.py <path-to-baxbench/src> [condition ...]
Writes results/<condition>/<task>.json and results/summary.json
"""
import json, os, pathlib, shutil, signal, socket, subprocess, sys, tempfile, time, multiprocessing
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import _bax  # noqa: E402,F401
BAX = pathlib.Path(sys.argv[1]).resolve(); sys.path.insert(0, str(BAX))
import exploits  # noqa: E402

_current_workdir = {"dir": None}
_current_proc = {"proc": None}
MANIFEST = pathlib.Path(tempfile.gettempdir()) / "secsdd_placed_paths.txt"
# Tests run in a forked child process, so paths created by exploits are written to a
# manifest file that the parent reads to clean up after every test.

def _map(path: str) -> pathlib.Path:
    """Container path -> host path. /app/<f> is the app's working directory;
    other absolute paths are used as-is (the pilot runs in a disposable sandbox)."""
    wd = pathlib.Path(_current_workdir["dir"])
    if path.startswith("/app/"):
        return wd / path[len("/app/"):]
    if path == "/app":
        return wd
    return pathlib.Path(path) if path.startswith("/") else wd / path

def load_file_from_docker(container_id, filepath):
    p = _map(filepath)
    if not p.is_file():
        raise exploits.FileNotFoundInContainer("File not found in docker image")
    return p.read_bytes()

def place_file_on_docker(container_id, filepath, file_content):
    p = _map(filepath)
    if not str(p).startswith(str(_current_workdir["dir"])):
        # record the highest ancestor that does not exist yet, so new directories go too
        top = p
        while not top.parent.exists():
            top = top.parent
        if not top.exists():
            with open(MANIFEST, "a") as fh:
                fh.write(str(top) + "\n")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(file_content if isinstance(file_content, bytes) else file_content.encode())

class _ExecResult:
    def __init__(self, exit_code, output):
        self.exit_code, self.output = exit_code, output

def execute_sql_on_docker(container_id, db_path, sql):
    import sqlite3 as _sq
    p = _map(db_path)
    try:
        con = _sq.connect(str(p))
        cur = con.cursor()
        rows = []
        for stmt in [x for x in sql.split(";") if x.strip()]:
            cur.execute(stmt)
            rows += cur.fetchall()
        con.commit(); con.close()
        out = "\n".join("|".join("" if v is None else str(v) for v in r) for r in rows)
        return _ExecResult(0, out.encode())
    except Exception as e:  # noqa: BLE001
        raise exploits.SQLQueryExecError(f"failed executing query: {e}")

def _tree_rss_mb():
    import psutil
    proc = _current_proc["proc"]
    try:
        p = psutil.Process(proc.pid)
        procs = [p] + p.children(recursive=True)
        return sum(x.memory_info().rss for x in procs if x.is_running()) / (1024 ** 2)
    except Exception:  # noqa: BLE001
        return None

def memory_usage(container_id):
    v = _tree_rss_mb()
    return int(v or 0)

def monitor_container_resources(container_id, duration, logger, memory_usage_threshold=1024, storage_usage_threshold=1024 ** 3):
    end = time.time() + duration
    while time.time() < end:
        v = _tree_rss_mb()
        if v is None:
            logger.warning("server process gone during monitoring")
            return True
        if v > memory_usage_threshold:
            logger.warning(f"High memory usage detected: {v}MB")
            return True
        time.sleep(0.1)
    size = sum(f.stat().st_size for f in pathlib.Path(_current_workdir["dir"]).rglob("*") if f.is_file())
    if size > storage_usage_threshold:
        logger.warning(f"High storage usage detected: {size} bytes")
        return True
    return False

exploits.load_file_from_docker = load_file_from_docker
exploits.place_file_on_docker = place_file_on_docker
exploits.execute_sql_on_docker = execute_sql_on_docker
exploits.memory_usage = memory_usage
exploits.monitor_container_resources = monitor_container_resources

import scenarios  # noqa: E402
from env.python import FlaskEnv  # noqa: E402
from scenarios.base import AppInstance  # noqa: E402
import cwes as cwe_mod  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = sys.executable
PORT = 5000
TIMEOUT = 60

def wait_port(port, proc, t=15):
    end = time.time() + t
    while time.time() < end:
        if proc.poll() is not None:
            return False
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.2)
    return False

def start_app(code_dir):
    wd = tempfile.mkdtemp(prefix="app_")
    shutil.copy(code_dir / "app.py", wd)
    _current_workdir["dir"] = wd
    env = dict(os.environ, APP_SECRET="supers3cret", PYTHONUNBUFFERED="1")
    log = open(pathlib.Path(wd) / "server.log", "w")
    proc = subprocess.Popen([PY, "app.py"], cwd=wd, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    _current_proc["proc"] = proc
    ok = wait_port(PORT, proc)
    return proc, wd, ok

def stop_app(proc, wd):
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    proc.wait()
    time.sleep(0.3)

def run_with_timeout(f, inst):
    with multiprocessing.get_context("fork").Pool(1) as pool:
        r = pool.apply_async(f, [inst])
        return r.get(timeout=TIMEOUT)

def run_task(sc, code_dir, logdir):
    res = {"functional": {}, "security": {}, "server_started": None}
    for kind, tests in (("functional", sc.functional_tests), ("security", sc.security_tests)):
        for t in tests:
            proc, wd, ok = start_app(code_dir)
            if res["server_started"] is None:
                res["server_started"] = ok
            inst = AppInstance(port=PORT, log_file_path=logdir / f"{t.__name__}.log", container_id=wd, env=FlaskEnv)
            out = None; err = None
            try:
                if ok:
                    out = run_with_timeout(t, inst)
            except Exception as e:  # noqa: BLE001
                err = f"{type(e).__name__}: {e}"
            crashed = ok and proc.poll() is not None
            stop_app(proc, wd)
            if kind == "functional":
                res[kind][t.__name__] = {"passed": bool(out) and not err, "error": err}
                if crashed:
                    res["security"].setdefault("_crash_during_functional", {"cwes": ["CWE-703"]})
            else:
                found = sorted(f"CWE-{c.value['num']}" for c in (out or set()))
                if crashed and "CWE-400" not in found:
                    found.append("CWE-703")
                res[kind][t.__name__] = {"cwes": found, "error": err, "inconclusive": out is None and not crashed}
            shutil.rmtree(wd, ignore_errors=True)
            if MANIFEST.exists():
                for line in MANIFEST.read_text().splitlines():
                    q = pathlib.Path(line)
                    try:
                        shutil.rmtree(q) if q.is_dir() else q.unlink()
                    except OSError:
                        pass
                MANIFEST.unlink()
    return res

def main():
    conds = sys.argv[2:] or ["baseline", "sis", "oracle"]
    by_id = {s.id: s for s in scenarios.all_scenarios}
    summary = {}
    for c in conds:
        summary[c] = {}
        only = set(os.environ.get("TASKS", "").split(",")) - {""}
        for code_dir in sorted((ROOT / "solutions" / c).iterdir()):
            if only and code_dir.name not in only:
                continue
            if not (code_dir / "app.py").exists():
                continue
            sc = by_id[code_dir.name]
            logdir = ROOT / "results" / c / "logs" / code_dir.name; logdir.mkdir(parents=True, exist_ok=True)
            r = run_task(sc, code_dir, logdir)
            func_ok = r["server_started"] and all(v["passed"] for v in r["functional"].values())
            vuln = sorted({x for v in r["security"].values() for x in v["cwes"]})
            r.update({"functionally_correct": bool(func_ok), "cwes_exploited": vuln,
                      "secure": not vuln, "correct_and_secure": bool(func_ok) and not vuln})
            (ROOT / "results" / c / f"{code_dir.name}.json").write_text(json.dumps(r, indent=2))
            summary[c][code_dir.name] = {k: r[k] for k in ("functionally_correct", "cwes_exploited", "correct_and_secure")}
            print(c, code_dir.name, "correct" if func_ok else "INCORRECT", vuln)
    (ROOT / "results" / "summary.json").write_text(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
