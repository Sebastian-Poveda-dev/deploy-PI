import os
import subprocess
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


TESTS_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = TESTS_DIR.parent
CHROMEDRIVER_PATH = TESTS_DIR / "chromedriver.exe"


def before_all(context):
    if os.getenv("SEED_DEMO_BEFORE_TESTS", "").lower() in {"1", "true", "yes"}:
        subprocess.run(
            ["python", "manage.py", "seed_demo", "--flush"],
            cwd=PROJECT_DIR / "backend",
            check=True,
        )

    options = webdriver.ChromeOptions()
    if os.getenv("SELENIUM_HEADLESS", "").lower() in {"1", "true", "yes"}:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")

    service = Service(str(CHROMEDRIVER_PATH)) if CHROMEDRIVER_PATH.exists() else Service()
    context.driver = webdriver.Chrome(service=service, options=options)
    context.driver.implicitly_wait(2)


def before_scenario(context, scenario):
    context.driver.delete_all_cookies()
    context.created_registration = {}


def after_all(context):
    if getattr(context, "driver", None):
        context.driver.quit()
