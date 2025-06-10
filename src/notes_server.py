#!/usr/bin/env python3
"""
Simple MCP Server for managing notes
Provides basic note storage and retrieval functionality
"""

import asyncio
import json
from typing import Dict, List, Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

# In-memory storage for notes
notes_storage: Dict[str, str] = {}

# Create server instance
server = Server("notes-server")

@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """List all available note resources"""
    resources = []
    for note_id in notes_storage.keys():
        resources.append(
            types.Resource(
                uri=f"note://{note_id}",
                name=f"Note: {note_id}",
                description=f"A note with ID {note_id}",
                mimeType="text/plain"
            )
        )
    return resources

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific note resource"""
    if not uri.startswith("note://"):
        raise ValueError(f"Unsupported URI scheme: {uri}")
    
    note_id = uri[7:]  # Remove "note://" prefix
    if note_id not in notes_storage:
        raise ValueError(f"Note not found: {note_id}")
    
    return notes_storage[note_id]

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="create_note",
            description="Create a new note with an ID and content",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "string",
                        "description": "Unique identifier for the note"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content of the note"
                    }
                },
                "required": ["note_id", "content"]
            }
        ),
        types.Tool(
            name="get_note",
            description="Retrieve a note by its ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "string",
                        "description": "The ID of the note to retrieve"
                    }
                },
                "required": ["note_id"]
            }
        ),
        types.Tool(
            name="list_notes",
            description="List all available notes",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="delete_note",
            description="Delete a note by its ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "string",
                        "description": "The ID of the note to delete"
                    }
                },
                "required": ["note_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls"""
    
    if name == "create_note":
        note_id = arguments.get("note_id")
        content = arguments.get("content")
        
        if not note_id or not content:
            return [types.TextContent(
                type="text",
                text="Error: Both note_id and content are required"
            )]
        
        notes_storage[note_id] = content
        return [types.TextContent(
            type="text",
            text=f"Note '{note_id}' created successfully"
        )]
    
    elif name == "get_note":
        note_id = arguments.get("note_id")
        
        if not note_id:
            return [types.TextContent(
                type="text",
                text="Error: note_id is required"
            )]
        
        if note_id not in notes_storage:
            return [types.TextContent(
                type="text",
                text=f"Error: Note '{note_id}' not found"
            )]
        
        return [types.TextContent(
            type="text",
            text=f"Note '{note_id}':\n{notes_storage[note_id]}"
        )]
    
    elif name == "list_notes":
        if not notes_storage:
            return [types.TextContent(
                type="text",
                text="No notes available"
            )]
        
        note_list = "\n".join([f"- {note_id}" for note_id in notes_storage.keys()])
        return [types.TextContent(
            type="text",
            text=f"Available notes:\n{note_list}"
        )]
    
    elif name == "delete_note":
        note_id = arguments.get("note_id")
        
        if not note_id:
            return [types.TextContent(
                type="text",
                text="Error: note_id is required"
            )]
        
        if note_id not in notes_storage:
            return [types.TextContent(
                type="text",
                text=f"Error: Note '{note_id}' not found"
            )]
        
        del notes_storage[note_id]
        return [types.TextContent(
            type="text",
            text=f"Note '{note_id}' deleted successfully"
        )]
    
    else:
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown tool '{name}'"
        )]

async def main():
    # Import here to avoid issues if mcp package is not available
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="notes-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())