import json
import os
import subprocess
import time
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[3]
BACKEND_PYTHON = PROJECT_DIR / "backend" / "venv" / "Scripts" / "python.exe"


def unique_suffix():
    return str(int(time.time() * 1000))[-9:]


def run_django_shell(code):
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    result = subprocess.run(
        [str(BACKEND_PYTHON), "manage.py", "shell", "-c", code],
        cwd=PROJECT_DIR / "backend",
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def run_django_shell_json(code):
    output = run_django_shell(code)
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return json.loads(lines[-1]) if lines else None
