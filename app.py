import json
import os

import streamlit as st

from competitor_intel import (
    MAX_COMPETITORS,
    IntelError,
    analyze_competitors,
    compare_runs,
    fetch_page,
    get_run,
    list_runs,
    save_run,
)


def _configured_api_key():
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key
    try:
        return st.secrets["GEMINI_API_KEY"].strip()
    except (KeyError, FileNotFoundError):
        return ""


def _render_report(report):
    for competitor in report.get("competitors", []):
        url = competitor.get("url", "Competitor")
        with st.expander(url, expanded=True):
            st.subheader(competitor.get("company_or_product", "Competitor"))
            st.markdown(f"**Positioning:** {competitor.get('positioning', 'Not identified')}")
            st.markdown(f"**Likely customer:** {competitor.get('target_customer', 'Not identified')}")
            st.markdown(f"**Offer and pricing cues:** {competitor.get('offer_and_pricing', 'Not identified')}")
            st.markdown(f"**Differentiators:** {competitor.get('differentiators', 'Not identified')}")

            angles = competitor.get("messaging_angles", [])
            if angles:
                st.markdown("**Messaging angles**")
                st.write(", ".join(angles))

            evidence = competitor.get("evidence", [])
            if evidence:
                st.markdown("**Evidence from the page**")
                for item in evidence:
                    st.markdown(f"- {item.get('claim', 'Finding')}: “{item.get('quote', '')}”")

            opportunities = competitor.get("opportunities", [])
            if opportunities:
                st.markdown("**Questions and opportunities for your client**")
                for opportunity in opportunities:
                    st.markdown(f"- {opportunity}")

    comparison = report.get("comparison", {})
    if comparison:
        st.subheader("Cross-competitor comparison")
        st.markdown(f"**Market pattern:** {comparison.get('market_pattern', 'Not identified')}")
        st.markdown(f"**Positioning differences:** {comparison.get('positioning_differences', 'Not identified')}")
        whitespace = comparison.get("whitespace", [])
        if whitespace:
            st.markdown("**Potential positioning whitespace**")
            for item in whitespace:
                st.markdown(f"- {item}")
        st.caption("AI-generated interpretations should be checked against the cited page evidence.")


st.set_page_config(page_title="Competitor Intel", page_icon="📊", layout="wide")
st.title("📊 Competitor Intel")
st.caption("Evidence-backed competitor comparisons and saved snapshots for agency research.")

with st.sidebar:
    st.header("AI configuration")
    api_key = st.text_input(
        "Gemini API key",
        type="password",
        help="Used only for this analysis. Or configure GEMINI_API_KEY in your environment or Streamlit secrets.",
    )
    if _configured_api_key():
        st.caption("A server-side Gemini key is configured.")
        st.warning("On a public app, visitors could consume this key's quota. Keep this app restricted or remove the shared key.")
    st.caption("Page text is sent to Google Gemini when you run an analysis. Review its terms before processing client data.")
    st.divider()
    st.markdown("**Manual research tool:** pages are fetched only when you click the button. No background monitoring or alerts run.")

tab_analyze, tab_history = st.tabs(["New comparison", "Saved snapshots"])

with tab_analyze:
    st.write(
        "Compare the public positioning, offers, and messaging of up to "
        f"{MAX_COMPETITORS} competitor pages in one report."
    )
    with st.form("competitor-analysis"):
        urls_text = st.text_area(
            "Competitor landing-page URLs (one per line)",
            placeholder="https://competitor-one.example\nhttps://competitor-two.example",
            height=120,
        )
        run_label = st.text_input("Client or project label (optional)", max_chars=80)
        submitted = st.form_submit_button("Fetch pages and generate comparison", type="primary")

    if submitted:
        urls = [line.strip() for line in urls_text.splitlines() if line.strip()]
        effective_key = api_key.strip() or _configured_api_key()
        if not effective_key:
            st.error("Enter a Gemini API key or configure GEMINI_API_KEY in the app environment/secrets.")
        elif not urls:
            st.warning("Add at least one competitor URL.")
        elif len(urls) > MAX_COMPETITORS:
            st.error(f"Use no more than {MAX_COMPETITORS} URLs per comparison.")
        else:
            with st.spinner("Fetching and checking the competitor pages..."):
                try:
                    pages = [fetch_page(url) for url in urls]
                except IntelError as exc:
                    st.error(str(exc))
                    pages = None

            if pages:
                with st.spinner("Building the evidence-backed comparison..."):
                    try:
                        report = analyze_competitors(
                            pages,
                            effective_key,
                            os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                        )
                        run_id = save_run(
                            report,
                            pages,
                            run_label.strip(),
                        )
                        st.session_state["latest_run_id"] = run_id
                    except IntelError as exc:
                        st.error(str(exc))
                        report = None

                if report:
                    st.success("Comparison saved to local snapshot history.")
                    _render_report(report)
                    st.download_button(
                        "Download report JSON",
                        data=json.dumps(report, ensure_ascii=False, indent=2),
                        file_name=f"competitor-intel-{run_id}.json",
                        mime="application/json",
                    )

with tab_history:
    st.write("Saved snapshots are stored in a local SQLite database. Re-run a comparison when you want a fresh snapshot.")
    try:
        runs = list_runs(limit=30)
    except IntelError as exc:
        st.error(f"Could not load snapshot history: {exc}")
        runs = []

    if not runs:
        st.info("No saved snapshots yet. Run a comparison to start a history.")
    else:
        run_options = {run["id"]: run for run in runs}
        labels = {
            run_id: (
                f"#{run_id} · {run['created_at']} · "
                f"{run['label'] or ', '.join(run['urls'])}"
            )
            for run_id, run in run_options.items()
        }
        selected_id = st.selectbox(
            "Open a saved report",
            options=list(run_options),
            format_func=lambda run_id: labels[run_id],
        )
        selected_run = get_run(selected_id)
        if selected_run:
            _render_report(selected_run["report"])
            st.download_button(
                "Download selected report JSON",
                data=json.dumps(selected_run["report"], ensure_ascii=False, indent=2),
                file_name=f"competitor-intel-{selected_id}.json",
                mime="application/json",
                key=f"download-{selected_id}",
            )

        if len(runs) > 1:
            st.subheader("Compare saved snapshots")
            run_ids = list(run_options)
            left, right = st.columns(2)
            old_id = left.selectbox(
                "Earlier snapshot",
                options=run_ids,
                index=min(1, len(run_ids) - 1),
                format_func=lambda run_id: labels[run_id],
                key="old-snapshot",
            )
            new_id = right.selectbox(
                "Later snapshot",
                options=run_ids,
                index=0,
                format_func=lambda run_id: labels[run_id],
                key="new-snapshot",
            )
            if old_id != new_id:
                try:
                    changes = compare_runs(old_id, new_id)
                    if not changes:
                        st.info("The saved snapshots have no matching competitor URLs.")
                    for change in changes:
                        st.markdown(f"**{change['url']}** — {change['status']}")
                        if change["diff"]:
                            st.code(change["diff"], language="diff")
                except IntelError as exc:
                    st.error(str(exc))
