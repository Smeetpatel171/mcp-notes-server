#!/usr/bin/env python3
"""
Simple test client for the MCP notes server
This demonstrates how to interact with the server programmatically
"""

import asyncio
import json
import subprocess
import sys

async def test_server():
    """Test the notes server functionality"""
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, "src/notes_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Initialize the server
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send initialize request
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print("Server initialized:", response.strip())
        
    except Exception as e:
        print(f"Error testing server: {e}")
    finally:
        process.terminate()

if __name__ == "__main__":
    asyncio.run(test_server())