import csv
import sys
import requests

CSV_FILE = "datasets/datasets.csv"
TIMEOUT = 15
FAIL_THRESHOLD = 0.30  # 30%

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; dataset-link-checker/1.0)"
}

failed = []
total = 0


def check_url(url):
    try:
        # Try HEAD first (fast)
        r = requests.head(
            url,
            allow_redirects=True,
            timeout=TIMEOUT,
            headers=headers,
        )
        if r.status_code < 400:
            return True, r.status_code

        # Fallback to GET (for Drive, Kaggle, gated sites)
        r = requests.get(
            url,
            stream=True,
            allow_redirects=True,
            timeout=TIMEOUT,
            headers=headers,
        )
        if r.status_code < 400:
            return True, r.status_code

        return False, r.status_code

    except requests.RequestException as e:
        return False, str(e)


print("Starting dataset link integrity check...\n")

with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        total += 1
        name = row["NAME"]
        url = row["MAIN_LINK"]

        ok, status = check_url(url)

        if ok:
            print(f" {name}: OK ({status})")
        else:
            print(f"  {name}: No Longer Available ({status})")
            failed.append((name, url, status))

print("\n--- SUMMARY ---")
failed_count = len(failed)
failure_ratio = failed_count / total if total else 0

print(f"Total links checked : {total}")
print(f"Broken links       : {failed_count} ({failure_ratio:.0%})\n")

for f in failed:
    print(f" - {f[0]} → {f[1]} ({f[2]})")

if failure_ratio >= FAIL_THRESHOLD:
    print("\n FAILURE: Broken links exceed 30% threshold")
    sys.exit(1)
else:
    print("\n SUCCESS: Check completed successfully.")
    sys.exit(0)
