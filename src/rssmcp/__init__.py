from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

from mcp.server.fastmcp import FastMCP

from rssmcp.server import RssCollector
from rssmcp.utils import load_yaml

config = load_yaml()

mcp = FastMCP("rssmcp")


@mcp.tool()
def get_rss(feed_name: str, since: str, export_result: bool = False) -> List[str]:
    """
    Fetch RSS feeds
    Args:
        feed_name: Feed name (e.g. "Example")
        since: Get feeds after this date (e.g. "2025-04-13")
        export_result: Whether to export the result to a text file
    Returns:
        Fetched text
    """
    since_dt = datetime.strptime(since, "%Y-%m-%d").replace(tzinfo=ZoneInfo(config["timezone"]))
    text = RssCollector(feed_name, since_dt, export_result).run()

    return text


def main():
    """Main entry point for the package."""
    mcp.run(transport="stdio")
