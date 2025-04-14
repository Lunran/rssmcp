import logging
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from zoneinfo import ZoneInfo

import feedparser

from rssmcp.utils import load_opml, load_yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RssCollector:

    def __init__(self, config_filename: str, opml_filename: str):
        """
        Initialize the RSS collector with config and OPML filenames
        Args:
            config_filename: Name of the config file
            opml_filename: Name of the OPML file
        """
        self.config = load_yaml(config_filename)
        self.feeds = load_opml(opml_filename)

    def run(self, feed_name: str, since: str, export_result=False):
        try:
            feed_urls = self.feeds[feed_name]
        except KeyError:
            logger.error(f"Feed name '{feed_name}' not found. Available feed names: {', '.join(self.feeds.keys())}")
            raise

        if export_result:
            export_dir = Path(__file__).parent.parent.parent / "output"
            os.makedirs(export_dir, exist_ok=True)
            today = datetime.now().strftime("%Y-%m-%d")
            export_path = f"{export_dir}/rss-{feed_name}-{today}.mdx"
        else:
            export_path = ""

        entries = self._fetch_all_entries(feed_urls, since)
        text = self._format_entries_to_markdown(entries)

        if export_path:
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(text)

        return text

    def _fetch_all_entries(self, feed_urls: list[str], since: str) -> List[tuple]:
        """
        Fetch entries from all feeds and filter by date
        Returns:
            Feed elements
        """
        entries = []
        for feed_url in feed_urls:
            try:
                feed = feedparser.parse(feed_url)
                feed_title = feed.feed.title if hasattr(feed.feed, "title") else "Unknown Feed"
                for entry in feed.entries[: self.config["max_entries_per_feed"]]:
                    title = entry.title if hasattr(entry, "title") else "Unknown Title"
                    summary = re.sub(r"<.*?>", "", entry.summary) if hasattr(entry, "summary") else "No Summary"
                    link = entry.link if hasattr(entry, "link") else "No Link"
                    entry_date = self._get_entry_date(entry)
                    since_dt = datetime.strptime(since, "%Y-%m-%d").replace(tzinfo=ZoneInfo(self.config["timezone"]))
                    if entry_date >= since_dt:
                        date_display = entry_date.strftime("%Y-%m-%d %H:%M")
                        entries.append((feed_title, date_display, title, summary, link))
            except Exception as e:
                logger.info(f"Error fetching {feed_url}: {str(e)}")

        return sorted(entries, key=lambda x: x[1], reverse=True)  # Sorted by newest date first

    def _get_entry_date(self, entry) -> datetime:
        """
        Extract date from entry and convert to timezone from config
        """
        if hasattr(entry, "published"):
            dt = self._parse_date(entry.published)
        elif hasattr(entry, "updated"):
            dt = self._parse_date(entry.updated)
        else:
            logger.info("Could not get entry date, returning current date")
            dt = datetime.now(ZoneInfo("UTC"))

        return dt.astimezone(ZoneInfo(self.config["timezone"]))

    def _parse_date(self, date: str) -> datetime:
        """
        Convert RSS feed date string to datetime object
        """
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",  # RFC 822 format
            "%a, %d %b %Y %H:%M:%S %Z",  # RFC 822 with timezone name
            "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601
            "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601 UTC
            "%Y-%m-%d %H:%M:%S",  # Simple format
            "%d %b %Y %H:%M %z",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date, fmt)
            except ValueError:
                continue
            if fmt.endswith("Z"):  # Z means UTC
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            else:
                dt = dt.replace(tzinfo=ZoneInfo(self.config["timezone"]))
            return dt

        # If it doesn't match any format, return Unix epoch
        logger.info(f"Could not parse date '{date}', returning Unix epoch")
        return datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC"))

    def _format_entries_to_markdown(self, entries) -> str:
        """
        Convert entries to text in markdown format
        """
        texts = []
        current_feed = ""

        for feed_title, date_display, title, summary, link in entries:
            if current_feed != feed_title:
                current_feed = feed_title
                texts.append(f"# {feed_title}\n")
            line = f"## {title} ({date_display})"
            texts.append(line)
            logger.info(line)
            texts.append(summary)
            texts.append(f"{link}\n")

        return "\n".join(texts)


if __name__ == "__main__":
    # Debug
    since = (datetime.now(ZoneInfo("Asia/Tokyo")) - timedelta(hours=24)).strftime("%Y-%m-%d")
    rss_collector = RssCollector("config.yaml", "feeds.opml")
    text = rss_collector.run("Example", since)
    logger.info(text)
