
from browser import open_browser
from scraper import scrape_page

playwright, browser, page = open_browser()

page.goto("https://www.indeed.com/jobs?q=controller&l=Los+Angeles%2C+CA")
page.wait_for_timeout(5000)

jobs = scrape_page(page)

print("\n=== Live Job Scout ===\n")

for i, job in enumerate(jobs, start=1):
    print(f"{i}. {job['title']}")
    print(f"   Company: {job['company']}\n")

page.wait_for_timeout(15000)

browser.close()
playwright.stop()
