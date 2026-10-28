"""Isolate legacy relative-path tests from repository-local experiment artifacts."""
from pathlib import Path
import shutil
import tempfile
import os
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
import pytest

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture(scope="session", autouse=True)
def release_test_workspace():
    # A short standard temporary path avoids Windows' nested filename limit.
    with tempfile.TemporaryDirectory(prefix="gb-", ignore_cleanup_errors=True) as name:
        workspace = Path(name)
        for relative in ("configs", "scripts", "docs", "src", "tests/fixtures"):
            source = ROOT / relative
            if source.is_dir():
                shutil.copytree(source, workspace / relative)
        for source in ROOT.glob("requirements*.txt"):
            shutil.copy2(source, workspace / source.name)
        yield workspace

@pytest.fixture(autouse=True)
def isolate_relative_artifacts(monkeypatch, release_test_workspace):
    monkeypatch.chdir(release_test_workspace)
