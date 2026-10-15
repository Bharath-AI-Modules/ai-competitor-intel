import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from competitor_intel import (
    IntelError,
    _PinnedAddressAdapter,
    _validated_url,
    analyze_competitors,
    compare_runs,
    fetch_page,
    save_run,
)


class FakeResponse:
    def __init__(self, status_code=200, headers=None, chunks=None):
        self.status_code = status_code
        self.headers = headers or {"Content-Type": "text/html"}
        self.chunks = chunks or []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def iter_content(self, chunk_size):
        return iter(self.chunks)


class UrlValidationTests(unittest.TestCase):
    def test_rejects_non_http_schemes_and_local_addresses(self):
        for url in (
            "file:///C:/Windows/win.ini",
            "ftp://example.com/page",
            "http://localhost/",
            "http://127.0.0.1/",
            "http://[::1]/",
            "http://192.168.1.1/",
            "http://example.com:8080/",
            "http://user:pass@example.com/",
        ):
            with self.subTest(url=url), self.assertRaises(IntelError):
                _validated_url(url)

    @patch("competitor_intel.socket.getaddrinfo")
    def test_rejects_hostname_resolving_to_private_address(self, getaddrinfo):
        getaddrinfo.return_value = [(2, 1, 6, "", ("10.0.0.8", 443))]
        with self.assertRaisesRegex(IntelError, "private or non-public"):
            _validated_url("https://internal.example")

    @patch("competitor_intel.socket.getaddrinfo")
    def test_accepts_public_address_and_strips_fragment(self, getaddrinfo):
        getaddrinfo.return_value = [(2, 1, 6, "", ("93.184.216.34", 443))]
        self.assertEqual(
            _validated_url("https://example.com/products#pricing"),
            "https://example.com/products",
        )

    def test_http_adapter_connects_to_the_validated_address(self):
        adapter = _PinnedAddressAdapter("example.com", "93.184.216.34")
        pool = Mock()
        adapter.poolmanager.connection_from_host = Mock(return_value=pool)

        self.assertIs(adapter.get_connection("https://example.com/products"), pool)
        adapter.poolmanager.connection_from_host.assert_called_once_with(
            "93.184.216.34",
            port=443,
            scheme="https",
            pool_kwargs={
                "assert_hostname": "example.com",
                "server_hostname": "example.com",
            },
        )
        adapter.close()


class FetchTests(unittest.TestCase):
    @patch("competitor_intel.requests.Session")
    def test_redirect_to_private_address_is_rejected_before_second_request(self, session_factory):
        session = Mock()
        session_factory.return_value = session
        session.get.return_value = FakeResponse(
            status_code=302,
            headers={"Location": "http://127.0.0.1/admin"},
        )
        with self.assertRaisesRegex(IntelError, "private or non-public"):
            fetch_page("https://8.8.8.8/")
        session.get.assert_called_once()
        session.close.assert_called_once()

    @patch("competitor_intel.requests.Session")
    def test_rejects_response_over_size_limit(self, session_factory):
        session = Mock()
        session_factory.return_value = session
        session.get.return_value = FakeResponse(
            chunks=[b"x" * 1_000_001],
        )
        with self.assertRaisesRegex(IntelError, "1 MB"):
            fetch_page("https://8.8.8.8/")

    @patch("competitor_intel.requests.Session")
    def test_extracts_page_title_and_visible_text(self, session_factory):
        session = Mock()
        session_factory.return_value = session
        html = (
            "<html><head><title>Example platform</title></head><body>"
            "<h1>Grow your team with better analytics</h1>"
            "<p>We help every sales team find more opportunities through useful insights and reports.</p>"
            "</body></html>"
        )
        session.get.return_value = FakeResponse(chunks=[html.encode()])
        page = fetch_page("https://8.8.8.8/")
        self.assertEqual(page["title"], "Example platform")
        self.assertIn("Grow your team", page["text"])
        self.assertEqual(len(page["content_hash"]), 64)

    @patch("competitor_intel.requests.Session")
    def test_reports_non_success_http_status(self, session_factory):
        session = Mock()
        session_factory.return_value = session
        session.get.return_value = FakeResponse(status_code=503)
        with self.assertRaisesRegex(IntelError, "HTTP 503"):
            fetch_page("https://8.8.8.8/")


class SnapshotTests(unittest.TestCase):
    def test_compares_saved_snapshot_text(self):
        with tempfile.TemporaryDirectory() as directory:
            database = os.path.join(directory, "history.db")
            with patch.dict(os.environ, {"COMPETITOR_INTEL_DB": database}):
                report = {"competitors": []}
                old_page = {
                    "url": "https://example.com/",
                    "title": "Example",
                    "text": "Old positioning message.",
                    "content_hash": "old",
                }
                new_page = {
                    "url": "https://example.com/",
                    "title": "Example",
                    "text": "New positioning message.",
                    "content_hash": "new",
                }
                old_id = save_run(report, [old_page], "pilot")
                new_id = save_run(report, [new_page], "pilot")
                changes = compare_runs(old_id, new_id)

        self.assertEqual(changes[0]["status"], "Extracted text changed")
        self.assertIn("-Old positioning message.", changes[0]["diff"])
        self.assertIn("+New positioning message.", changes[0]["diff"])


class AnalysisTests(unittest.TestCase):
    @patch("google.genai.Client")
    def test_accepts_only_evidence_quotes_found_in_source_text(self, client_class):
        page = {
            "url": "https://example.com/",
            "title": "Example",
            "text": "We help teams improve their sales workflow with clear reporting.",
        }
        client = client_class.return_value
        client.models.generate_content.return_value.text = (
            '{"competitors":[{"evidence":[{"claim":"Positioning","quote":"We help teams improve"}]}],'
            '"comparison":{"market_pattern":"Sales tools"}}'
        )

        report = analyze_competitors([page], "test-key")

        self.assertEqual(report["competitors"][0]["url"], page["url"])
        self.assertEqual(report["competitors"][0]["evidence"][0]["quote"], "We help teams improve")

        client.models.generate_content.return_value.text = (
            '{"competitors":[{"evidence":[{"claim":"Unsupported","quote":"We are the market leader"}]}]}'
        )
        with self.assertRaisesRegex(IntelError, "exact source quote"):
            analyze_competitors([page], "test-key")


if __name__ == "__main__":
    unittest.main()
