# Documentation Lookup

- Search a product's documentation through the MCP server its vendor provides for that documentation, before Context7 or DeepWiki (a vendor's server searches its current official docs, and Context7's server instructions ask to be used for cloud services too)
  - A vendor's MCP server for operating the product counts when it carries a documentation search tool, as the Datadog connector's `search_datadog_documentation` does
- When no such server is connected to the session, use Context7 or DeepWiki
