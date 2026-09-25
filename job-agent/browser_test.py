
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://www.indeed.com/jobs?q=controller&l=Los+Angeles%2C+CA")

    page.wait_for_timeout(5000)

    print("Job Scout opened Indeed.\n")

    # Save a screenshot of exactly what Job Scout sees.
    page.screenshot(path="debug_page.png", full_page=True)
    print("Saved screenshot: debug_page.png")

    # Count possible job titles using a few different selectors.
    selectors = [
        "h2.jobTitle",
        "h2.jobTitle span[title]",
        "[data-testid='job-title']",
        "h2"
    ]

    print("\nSelector test:\n")

    for selector in selectors:
        count = page.locator(selector).count()
        print(f"{selector}: {count}")

    page.wait_for_timeout(15000)
    browser.close()

