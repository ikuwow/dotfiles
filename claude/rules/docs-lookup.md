# Documentation Lookup

- Search a vendor's own docs MCP server before Context7 or DeepWiki when the question is about that vendor's product (a vendor's server searches its current official docs, and Context7's server instructions ask to be used for cloud services too)
  - AWS: `aws-knowledge`
  - Google Cloud and other Google developer products, Go included: `google-developer-knowledge`
  - Datadog: the Datadog connector's `search_datadog_documentation`
- When the product has no such server, or the server is absent from the session, use Context7 or DeepWiki
