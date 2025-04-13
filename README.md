# rssmcp MCP server

Simple RSS MCP Server

## Components

### Tools

The server implements one tool:
- get_rss: Fetches RSS feeds and returns entries as formatted text
  - Takes "feed_name" and "since" as required string arguments
  - "export_result" as an optional boolean parameter (defaults to false)
  - Returns formatted feed entries as text and optionally exports to a file

## Quickstart

### Install

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "rssmcp": {
      "command": "uvx",
      "args": [
        "rssmcp"
      ]
    }
  }
  ```
</details>
