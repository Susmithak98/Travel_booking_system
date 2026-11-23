"""Start the MCP tool server over streamable HTTP at http://127.0.0.1:8000/mcp"""
from mcp_tools import MCP_HOST, MCP_PORT, mcp

if __name__ == "__main__":
    print(f"🧰 MCP travel tools running at http://{MCP_HOST}:{MCP_PORT}/mcp")
    mcp.run(transport="streamable-http")
