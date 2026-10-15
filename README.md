# Competitor Intel

Competitor Intel is an early-stage research tool for small marketing agencies. It fetches public landing pages, compares the competitors' stated positioning and offers with Gemini, and saves dated local snapshots so an analyst can revisit and compare changes.

This is a **manual research MVP**, not an automatic monitoring service: it does not run on a schedule, send alerts, crawl whole sites, or provide user accounts and billing. Treat findings as research hypotheses and verify them against the cited page excerpts.

## Run locally

Requires Python 3.9 or newer.

```powershell
git clone https://github.com/Bharath-AI-Modules/ai-competitor-intel.git
cd ai-competitor-intel
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:GEMINI_API_KEY = "your-key-from-google-ai-studio"
streamlit run app.py
```

Alternatively, leave `GEMINI_API_KEY` unset and enter your own key in the app sidebar. A key may also be configured in Streamlit secrets. Never commit a key or put one in a URL. `GEMINI_MODEL` optionally selects a model (defaults to `gemini-2.5-flash`).

Enter one to five public HTTP(S) landing-page URLs, one per line, and run a comparison. Reports include cited page excerpts and cross-competitor themes. Download the JSON report or revisit a snapshot in **Saved snapshots**. Local history uses SQLite in `competitor_intel.db` by default; set `COMPETITOR_INTEL_DB` to choose another path.

```powershell
python -m unittest discover -s tests -v
```

## Fetching and data handling

The fetcher rejects non-HTTP(S) URLs, credentials in URLs, non-standard ports, localhost/private/non-public IPs (including DNS results and redirects), non-HTML responses, and responses larger than 1 MB. It pins each request to the validated public address, uses a timeout, and revalidates redirects. Only public pages are fetched; site access policies and applicable laws still apply. The page text is sent to Google Gemini when analysis runs. Do not submit confidential client material. Keep server-side Gemini keys behind access control: this app has no sign-in, quota, or abuse prevention.

SQLite snapshots and reports stay on the machine/container running the app. They are not encrypted or shared between users. On ephemeral hosting such as Streamlit Community Cloud, local files may be reset, so this is not durable production storage.

## Launch and monetization

See [LAUNCH_GUIDE.md](LAUNCH_GUIDE.md) for the target-customer hypothesis, pricing experiments, a practical first-customer plan, deployment/account setup, public-listing checklist, and the human work still required before charging customers.
