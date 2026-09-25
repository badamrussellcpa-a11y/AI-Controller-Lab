
def scrape_page(page):
    headings = page.locator("h2").all_inner_texts()

    jobs = []

    for heading in headings[:5]:
        jobs.append({
            "title": heading.strip(),
            "company": "Company pending extraction"
        })

    return jobs
