import argparse
from typing import List

from mcp.server.fastmcp import FastMCP

from rssmcp.server import RssCollector

mcp = FastMCP("rssmcp")
rss_collector = None


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
    text = rss_collector.run(feed_name, since, export_result)

    return text


def main():
    parser = argparse.ArgumentParser(description="RSS MCP Server")
    parser.add_argument("--config", help="Path to config file", default="config.yaml")
    parser.add_argument("--opml", help="Path to opml file", default="feeds.opml")
    args = parser.parse_args()

    global rss_collector
    rss_collector = RssCollector(args.config, args.opml)

    mcp.run(transport="stdio")
