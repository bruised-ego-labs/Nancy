#!/usr/bin/env python3
"""
Simple test MCP server to verify Claude Code MCP integration
"""
import logging
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test-mcp-server")

# Create server
server = Server("test-mcp")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="test_echo",
            description="Simple echo test tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to echo back"
                    }
                },
                "required": ["message"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls."""
    if name == "test_echo":
        message = arguments.get("message", "")
        return [
            types.TextContent(
                type="text",
                text=f"Echo: {message}"
            )
        ]
    else:
        raise ValueError(f"Unknown tool: {name}")

if __name__ == "__main__":
    logger.info("Starting Test MCP Server...")
    stdio_server(server)