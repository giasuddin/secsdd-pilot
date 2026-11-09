"""Import BaxBench without a running Docker daemon.
BaxBench's env module calls docker.from_env() at import time; the pilot never
uses Docker, so we stub it out before importing BaxBench modules."""
import pathlib, sys
import docker
docker.from_env = lambda *a, **k: None
def add_path(p):
    sys.path.insert(0, str(pathlib.Path(p).resolve()))
