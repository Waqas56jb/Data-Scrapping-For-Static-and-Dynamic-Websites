import re
import csv
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

OUTPUT_CSV = "contacts.csv"

# Contact URLs to scrape (each is a single page)
CONTACT_URLS = [
    "https://www.commerce.gov.pk/contact-us/",
    "https://webhoster.pk/contact-us/",
    "https://phonecovers.pk/pages/contact",
    "https://www.webs.com.pk/contactus.php",
    "https://madeinpakistan.online/contact-us/",
    "https://www.pksoftwares.com/contact-us/",
    "https://www.websolpro.com/contact-us.html",
    "https://www.businessonline.pk/Home/Contactus",
    "https://sospakistan.com/contact-us/",
    "https://www.webdesigncompany.com.pk/contact-us/",
]


def create_driver() -> webdriver.Chrome:
    options = Options()
    # Visible Chrome window (not headless)
    # options.add_argument("--headless=new")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def extract_contact_from_url(driver: webdriver.Chrome, url: str) -> dict:
    driver.get(url)
    time.sleep(4)

    try:
        site_name = driver.title.strip()
    except Exception:
        site_name = ""

    body_text = driver.find_element(By.TAG_NAME, "body").text
    hrefs = " ".join(
        (a.get_attribute("href") or "").strip()
        for a in driver.find_elements(By.XPATH, "//a[@href]")
    )
    full_text = body_text + " " + hrefs

    email_pattern = re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    )
    phone_pattern = re.compile(
        r"\+92[0-9\-\s()]{7,15}"
    )

    emails_found = {e for e in re.findall(email_pattern, full_text)}
    phones_found = {" ".join(p.split()) for p in re.findall(phone_pattern, full_text)}

    return {
        "site": site_name,
        "url": url,
        "emails": ";".join(sorted(emails_found)),
        "phones": ";".join(sorted(phones_found)),
    }


def scrape_all_contacts() -> list:
    driver = create_driver()
    try:
        contacts = []
        for i, url in enumerate(CONTACT_URLS, start=1):
            print(f"[{i}/{len(CONTACT_URLS)}] Scraping {url}")
            info = extract_contact_from_url(driver, url)
            contacts.append(info)
        return contacts
    finally:
        driver.quit()


def save_to_csv(contacts: list, filename: str) -> None:
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["site", "url", "emails", "phones"])
        for c in contacts:
            writer.writerow([c["site"], c["url"], c["emails"], c["phones"]])


def main() -> None:
    contacts = scrape_all_contacts()
    save_to_csv(contacts, OUTPUT_CSV)
    print(f"Saved {len(contacts)} sites to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()