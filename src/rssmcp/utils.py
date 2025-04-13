import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List

import yaml

config_path = Path(__file__).parent / "config.yaml"
opml_path = Path(__file__).parent / "feeds.opml"


def load_yaml() -> Dict:
    """
    Load YAML file and return its content as a dictionary
    Args:
        file_path: Path to the YAML file
    Returns:
        Dictionary with the content of the YAML file
    """
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_opml() -> Dict[str, List[str]]:
    """
    Parse OPML file and extract RSS feeds grouped by category
    Args:
        opml_path: Path to the OPML file
    Returns:
        Dictionary with categories as keys and lists of feed URLs as values
    """
    feeds: dict[str, list[str]] = {}
    root = ET.parse(opml_path).getroot()

    for category in root.findall(".//outline[@title]"):
        category_name = category.attrib.get("text")
        if category_name:
            feeds[category_name] = []
            for feed in category.findall("./outline[@xmlUrl]"):
                feed_url = feed.attrib.get("xmlUrl")
                if feed_url:
                    feeds[category_name].append(feed_url)

    return feeds
