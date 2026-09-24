import csv

print("\n=== Job Scout Report ===\n")

with open("job_tracker.csv", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for job in reader:
        score = 0
        notes = job["Notes"].lower()

        if "month-end close" in notes:
            score += 10

        if "general ledger" in notes:
            score += 10

        if "audit" in notes:
            score += 8

        if "balance sheet" in notes:
            score += 9

        if "journal entries" in notes:
            score += 8

        print(job["Company"])
        print(f"Role: {job['Job Title']}")
        print(f"Salary: ${int(job['Salary']):,}")
        print(f"Match Score: {score}")
        print("-" * 25)