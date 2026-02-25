import os
from typing import Optional

import httpx
from fastmcp import FastMCP

API_BASE_URL = os.getenv("API_BASE_URL", "https://uksponsorsearch.co.uk")

mcp = FastMCP(
    "UK Visa Sponsor Search",
    instructions=(
        "Search the UK Register of Licensed Visa Sponsors (125,000+ companies). "
        "Use check_sponsor to verify if a specific company sponsors UK visas. "
        "Use search_sponsors to find sponsors by city, county, visa route, or rating. "
        "Use get_sponsor_details to get full information about a sponsor. "
        "Use get_stats for an overview of the register."
    ),
)


async def _api_get(path: str, params: Optional[dict] = None) -> dict:
    """Make a GET request to the UK Visa Sponsor Search API."""
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        response = await client.get(path, params=params)
        response.raise_for_status()
        return response.json()


def _format_sponsor(sponsor: dict) -> str:
    """Format a sponsor record into readable text."""
    lines = [f"**{sponsor.get('organisationName', 'Unknown')}**"]

    location_parts = [sponsor.get("townCity", ""), sponsor.get("county", "")]
    location = ", ".join(p for p in location_parts if p)
    if location:
        lines.append(f"Location: {location}")

    if sponsor.get("rating"):
        lines.append(f"Rating: {sponsor['rating']}")

    if sponsor.get("sponsorType"):
        lines.append(f"Type: {sponsor['sponsorType']}")

    if sponsor.get("routes"):
        routes = sponsor["routes"]
        if isinstance(routes, list):
            lines.append(f"Visa Routes: {', '.join(routes)}")

    if sponsor.get("slug"):
        lines.append(f"Details: https://uksponsorsearch.co.uk/sponsors/{sponsor['slug']}")

    return "\n".join(lines)


@mcp.tool()
async def check_sponsor(company_name: str) -> str:
    """Check if a specific company is a licensed UK visa sponsor.

    Args:
        company_name: The company name to check (minimum 3 characters).
    """
    if len(company_name.strip()) < 3:
        return "Please provide at least 3 characters for the company name."

    try:
        data = await _api_get("/api/check", {"q": company_name.strip()})
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            return "Please provide at least 3 characters for the company name."
        return f"Error checking sponsor: {e.response.status_code}"

    if not data.get("found"):
        return f'No UK visa sponsor found matching "{company_name}". The company may not hold a sponsor licence, or the name may be spelled differently.'

    result = [f'Yes, a match was found for "{company_name}":\n']
    result.append(_format_sponsor(data["sponsor"]))

    suggestions = data.get("suggestions", [])
    if len(suggestions) > 1:
        result.append("\nOther possible matches:")
        for s in suggestions[1:]:
            city = f" ({s['townCity']})" if s.get("townCity") else ""
            result.append(f"- {s['name']}{city}")

    return "\n".join(result)


@mcp.tool()
async def search_sponsors(
    query: Optional[str] = None,
    city: Optional[str] = None,
    county: Optional[str] = None,
    route: Optional[str] = None,
    rating: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> str:
    """Search and filter UK visa sponsors.

    Args:
        query: Search by organisation name.
        city: Filter by city (e.g. "London", "Manchester").
        county: Filter by county (e.g. "Greater London", "West Midlands").
        route: Filter by visa route (e.g. "Skilled Worker", "Health and Care Worker").
        rating: Filter by rating ("A rating" or "B rating").
        page: Page number (default 1).
        page_size: Results per page (default 10, max 100).
    """
    params: dict = {"page": str(page), "pageSize": str(min(page_size, 100))}
    if query:
        params["q"] = query.strip()
    if city:
        params["city"] = city.strip()
    if county:
        params["county"] = county.strip()
    if route:
        params["route"] = route.strip()
    if rating:
        params["rating"] = rating.strip()

    try:
        data = await _api_get("/api/search", params)
    except httpx.HTTPStatusError as e:
        return f"Error searching sponsors: {e.response.status_code}"

    total = data.get("total", 0)
    total_pages = data.get("totalPages", 0)
    sponsors = data.get("sponsors", [])

    if total == 0:
        filters = []
        if query:
            filters.append(f'name="{query}"')
        if city:
            filters.append(f"city={city}")
        if county:
            filters.append(f"county={county}")
        if route:
            filters.append(f"route={route}")
        if rating:
            filters.append(f"rating={rating}")
        filter_str = ", ".join(filters) if filters else "the given criteria"
        return f"No sponsors found matching {filter_str}."

    result = [f"Found {total:,} sponsors (page {page} of {total_pages}):\n"]
    for sponsor in sponsors:
        result.append(_format_sponsor(sponsor))
        result.append("")

    if page < total_pages:
        result.append(f"Use page={page + 1} to see more results.")

    return "\n".join(result)


@mcp.tool()
async def get_sponsor_details(slug: str) -> str:
    """Get full details for a specific UK visa sponsor.

    Args:
        slug: The sponsor's URL slug (e.g. "deloitte-llp-london"). You can find this from search results.
    """
    try:
        data = await _api_get(f"/api/sponsors/{slug.strip()}")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f'No sponsor found with slug "{slug}". Try using search_sponsors to find the correct slug.'
        return f"Error fetching sponsor: {e.response.status_code}"

    result = [_format_sponsor(data)]

    if data.get("lastSeenAt"):
        result.append(f"Last Verified: {data['lastSeenAt'][:10]}")

    if data.get("createdAt"):
        result.append(f"First Added: {data['createdAt'][:10]}")

    return "\n".join(result)


@mcp.tool()
async def get_stats() -> str:
    """Get overall statistics about the UK Register of Licensed Visa Sponsors."""
    try:
        data = await _api_get("/api/stats")
    except httpx.HTTPStatusError as e:
        return f"Error fetching stats: {e.response.status_code}"

    result = [
        "## UK Visa Sponsor Register Statistics\n",
        f"Total Licensed Sponsors: {data.get('totalSponsors', 0):,}",
        f"A Rated: {data.get('aRated', 0):,}",
        f"B Rated: {data.get('bRated', 0):,}",
        f"Recently Added (last 30 days): {data.get('recentlyAdded', 0):,}",
    ]

    if data.get("lastUpdated"):
        result.append(f"Last Updated: {data['lastUpdated'][:10]}")

    by_route = data.get("byRoute", {})
    if by_route:
        result.append("\n### Sponsors by Visa Route")
        for route, count in sorted(by_route.items(), key=lambda x: x[1], reverse=True):
            result.append(f"- {route}: {count:,}")

    top_cities = data.get("topCities", [])
    if top_cities:
        result.append("\n### Top Cities")
        for city in top_cities[:10]:
            result.append(f"- {city['city']}: {city['count']:,}")

    return "\n".join(result)


if __name__ == "__main__":
    mcp.run()
