import getpass
import os

from competitor_intel import MAX_COMPETITORS, IntelError, analyze_competitors, fetch_page


def main():
    print("=== Competitor Intel: public-page comparison ===")
    urls = [
        line.strip()
        for line in input("Enter competitor URLs, separated by commas: ").split(",")
        if line.strip()
    ]
    if not urls:
        print("Enter at least one HTTP or HTTPS URL.")
        return
    if len(urls) > MAX_COMPETITORS:
        print(f"Enter no more than {MAX_COMPETITORS} competitor URLs.")
        return

    api_key = os.getenv("GEMINI_API_KEY") or getpass.getpass("Gemini API key: ").strip()
    if not api_key:
        print("A Gemini API key is required.")
        return

    try:
        pages = []
        for url in urls:
            print(f"Fetching {url}...")
            pages.append(fetch_page(url))
        report = analyze_competitors(
            pages,
            api_key,
            os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        )
    except IntelError as exc:
        print(f"Could not complete the comparison: {exc}")
        return

    import json

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
