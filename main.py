import base64
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
from webdriver_manager.chrome import ChromeDriverManager
from PyPDF2 import PdfMerger
import os
from utils import BASE_URL, ENDPOINT, TOTAL_PAGES, EXAM_TYPES, EXAM_NAME

SESSION_ID = os.environ.get("SESSION_ID")
CSRF_TOKEN = os.environ.get("CSRF_TOKEN")




def use_existing_session_and_print_all(exam_name:str, base_url: str, endpoint: str, sessionid, csrftoken, total_pages=21, reveal_solutions=True, only_solutions=False):
    if not reveal_solutions and only_solutions:
        raise ValueError("Param `reveal_solutions` can't be false while param `only_solutions` is True")
    
    if not sessionid or not csrftoken:
        raise ValueError("You MUST provide sessionid and csrftoken params. This can be found as cookies on examtopics")

    if only_solutions:
        exam_type = EXAM_TYPES[0]
    elif reveal_solutions:
        exam_type = EXAM_TYPES[1]
    else:
        exam_type = EXAM_TYPES[2]

    exam_full_pathname = f"exams/examtopics_{exam_name}_{exam_type}.pdf"

    # Ex.
    # domain = .examtopics.com
    domain = base_url.split("www")[1]

    # url_endpoint = "https://www.examtopics.com/exams/amazon/aws-certified-solutions-architect-associate-saa-c03/view"
    url_endpoint = base_url + endpoint
    
    temp_files = []

    # Setup Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Load domain to set cookies
        driver.get(base_url)
        time.sleep(2)

        # Add cookies for session
        driver.delete_all_cookies()
        driver.add_cookie({"name": "sessionid", "value": sessionid, "domain": domain, "path": "/"})
        driver.add_cookie({"name": "csrftoken", "value": csrftoken, "domain": domain, "path": "/"})

        # Loop through pages
        for i in range(1, total_pages + 1):
            url = url_endpoint if i == 1 else f"{url_endpoint}/{i}/"
            print(f"📄 Loading page {i}: {url}")
            driver.get(url)
            time.sleep(4)  # wait for JS and lazy loading

            # Scroll down slowly to load everything
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Delete wrong answers
            if only_solutions:
                driver.execute_script("""
                    document.querySelectorAll('ul li.multi-choice-item').forEach(el => {
                        if (!el.classList.contains('correct-hidden')) {
                            el.remove();
                        }
                    });
                """)

            # Click DOM buttons to reveal solutions
            if reveal_solutions:
                driver.execute_script("""
                    document.querySelectorAll('a.reveal-solution').forEach(btn => btn.click());
                """)
                time.sleep(2)  # wait until all solutions are revealed

            # Print pages as temp PDF
            print_options = PrintOptions()
            print_options.orientation = "portrait"
            print_options.background = True
            pdf_data = driver.print_page(print_options)
            pdf_bytes = base64.b64decode(pdf_data)

            temp_file = f"temp_page_{i}.pdf"
            with open(temp_file, "wb") as f:
                f.write(pdf_bytes)
            temp_files.append(temp_file)
            print(f"✅ Saved {temp_file}")

        # Merge all PDFs into a single one
        print("📚 Merging pages...")
        merger = PdfMerger()
        for temp_file in temp_files:
            merger.append(temp_file)
        merger.write(exam_full_pathname)
        merger.close()
        print(f"🎉 File was created and saved on: {exam_full_pathname}")

    finally:
        driver.quit()
        for f in temp_files:
            os.remove(f)


# JUST RUN EVERYTHING WHY BOTHER LOL
use_existing_session_and_print_all(
    exam_name=EXAM_NAME,
    base_url=BASE_URL,
    endpoint=ENDPOINT,
    sessionid=SESSION_ID,
    csrftoken=CSRF_TOKEN,
    total_pages=TOTAL_PAGES,
    reveal_solutions=False,
    only_solutions=False
)

use_existing_session_and_print_all(
    exam_name=EXAM_NAME,
    base_url=BASE_URL,
    endpoint=ENDPOINT,
    sessionid=SESSION_ID,
    csrftoken=CSRF_TOKEN,
    total_pages=TOTAL_PAGES,
    reveal_solutions=True,
    only_solutions=False
)

use_existing_session_and_print_all(
    exam_name=EXAM_NAME,
    base_url=BASE_URL,
    endpoint=ENDPOINT,
    sessionid=SESSION_ID,
    csrftoken=CSRF_TOKEN,
    total_pages=TOTAL_PAGES,
    reveal_solutions=True,
    only_solutions=True
)