import time
import xml.etree.ElementTree as ET

import requests

ARXIV_API_URL = "https://export.arxiv.org/api/query"
XML_NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}
REQUEST_HEADERS = {"User-Agent": "ResearchAgent/0.1 (learning project)"}

SECONDS_BETWEEN_REQUESTS = 3
MAX_SUMMARY_CHARS = 1500

_last_request_time = 0.0


def _clean_text(text: str) -> str:
    """Collapse line breaks and repeated spaces into single spaces."""
    return " ".join(text.split())


def _wait_for_rate_limit() -> None:
    """Sleep just long enough to keep 3 seconds between arXiv requests."""
    global _last_request_time
    seconds_since_last_request = time.time() - _last_request_time
    if seconds_since_last_request < SECONDS_BETWEEN_REQUESTS:
        time.sleep(SECONDS_BETWEEN_REQUESTS - seconds_since_last_request)
    _last_request_time = time.time()


def arxiv_search_tool(query: str, max_results: int = 3) -> list[dict]:
    """Search arXiv for academic preprints and return title, authors, date, links and abstract.

    Only useful for computer science, math, physics, statistics, quantitative biology,
    quantitative finance, electrical engineering and economics. Do not use it for
    history, health policy, news or general topics; use tavily_search_tool instead.

    Args:
        query: Keywords describing the papers to find (e.g. "retrieval augmented generation evaluation").
        max_results: Number of papers to return, between 1 and 10. Defaults to 3.
    """
    try:
        if not isinstance(query, str) or not query.strip():
            return [{"error": "Query is empty!"}]
        query = query.strip()

        max_results = max(1, min(int(max_results), 10))

        search_expression = " AND ".join(f"all:{word}" for word in query.split())

        _wait_for_rate_limit()
        response = requests.get(
            ARXIV_API_URL,
            params={
                "search_query": search_expression,
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
            },
            headers=REQUEST_HEADERS,
            timeout=20,
        )
        response.raise_for_status()

        feed = ET.fromstring(response.content)

        papers = []
        for paper_entry in feed.findall("atom:entry", XML_NAMESPACES):
            title = _clean_text(paper_entry.findtext("atom:title", "", XML_NAMESPACES))

            if title == "Error":
                error_message = _clean_text(paper_entry.findtext("atom:summary", "", XML_NAMESPACES))
                return [{"error": f"arXiv rejected the query: {error_message}"}]

            author_names = [
                author.findtext("atom:name", "", XML_NAMESPACES)
                for author in paper_entry.findall("atom:author", XML_NAMESPACES)
            ]

            pdf_url = ""
            for link in paper_entry.findall("atom:link", XML_NAMESPACES):
                if link.get("title") == "pdf":
                    pdf_url = link.get("href", "")

            abstract = _clean_text(paper_entry.findtext("atom:summary", "", XML_NAMESPACES))

            papers.append({
                "title": title,
                "authors": author_names,
                "published": paper_entry.findtext("atom:published", "", XML_NAMESPACES)[:10],
                "url": paper_entry.findtext("atom:id", "", XML_NAMESPACES),
                "pdf_url": pdf_url,
                "summary": abstract[:MAX_SUMMARY_CHARS],
            })

        return papers

    except Exception as error:
        return [{"error": f"arXiv search failed: {error}"}]
