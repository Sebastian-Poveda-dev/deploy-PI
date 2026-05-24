import os
import subprocess
import shutil
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


TESTS_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = TESTS_DIR.parent
CHROMEDRIVER_PATH = TESTS_DIR / "chromedriver.exe"
BACKEND_PYTHON = PROJECT_DIR / "backend" / "venv" / "Scripts" / "python.exe"


def before_all(context):
    os.environ.setdefault("SE_CACHE_PATH", str(TESTS_DIR / ".selenium-cache"))

    if os.getenv("SEED_DEMO_BEFORE_TESTS", "").lower() in {"1", "true", "yes"}:
        env = os.environ.copy()
        env.setdefault("PYTHONIOENCODING", "utf-8")
        subprocess.run(
            [str(BACKEND_PYTHON), "manage.py", "seed_demo", "--flush"],
            cwd=PROJECT_DIR / "backend",
            env=env,
            check=True,
        )

    options = webdriver.ChromeOptions()
    if os.getenv("SELENIUM_HEADLESS", "1").lower() in {"1", "true", "yes"}:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=0")
    chrome_profile_dir = TESTS_DIR / ".chrome-profile"
    if chrome_profile_dir.exists():
        shutil.rmtree(chrome_profile_dir, ignore_errors=True)
    options.add_argument(f"--user-data-dir={chrome_profile_dir}")

    service = Service(str(CHROMEDRIVER_PATH)) if CHROMEDRIVER_PATH.exists() else Service()
    context.driver = webdriver.Chrome(service=service, options=options)
    context.driver.implicitly_wait(2)


def before_scenario(context, scenario):
    context.driver.delete_all_cookies()
    context.created_registration = {}


def after_all(context):
    if getattr(context, "driver", None):
        context.driver.quit()
