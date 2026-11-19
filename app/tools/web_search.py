from tavily import TavilyClient

from app import config


def tavily_search_tool(query: str, max_results: int = 5) -> list[dict]:
    """Search the web with Tavily for recent articles, news, docs and general web sources.

    Use this for current events, industry or product information, blog posts and
    anything recent. For academic papers prefer arxiv_search_tool; for background
    definitions prefer wikipedia_search_tool.

    Args:
        query: The search query, written like a short web search (e.g. "retrieval-augmented generation 2026 survey").
        max_results: Number of results to return, between 1 and 10. Defaults to 5.
    """
    if not config.TAVILY_API_KEY:
        return [{"error": "TAVILY_API_KEY is not set"}]

    try:
        if not isinstance(query, str) or not query.strip():
            return [{"error": "Query is empty!"}]
        query = query.strip()

        max_results = max(1, min(int(max_results), 10))

        client = TavilyClient(api_key=config.TAVILY_API_KEY)
        response = client.search(query, max_results=max_results, timeout=30)

        final_results = []
        for result in response.get("results", []):
            final_results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
            })
        return final_results

    except Exception as e:
        return [{"error": f"Tavily search failed: {e}"}]
