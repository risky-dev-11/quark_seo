import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def format_url(url: str) -> str:
    url = url.replace("https://", "http://").replace("www.", "")
    if not url.startswith("http://"):
        url = "http://" + url
    if not url.endswith("/"):
        url = url + "/"
    return url

def get_driver():
    service = Service()
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def fetch_website_content(url: str):
    """
    Fetch website content using both requests and Selenium.
    Returns a tuple: (response, page_source, screenshot).
    """
    # Get the static response first
    response = requests.get(url, allow_redirects=True)
    
    driver = get_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.XPATH, "//*"))
        )
        page_source = driver.page_source
        screenshot = driver.get_screenshot_as_png()
    except Exception as e:
        # Log or handle error as needed.
        raise requests.exceptions.RequestException(
            'Unser Server konnte die Webseite nicht erreichen. Bitte überprüfen Sie die URL und versuchen Sie es erneut.'
        ) from e
    finally:
        driver.quit()
    
    return response, page_source, screenshot
