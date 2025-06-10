#!/usr/bin/env python3
"""
Enhanced test client for the MCP notes server
Tests all functionality with proper MCP protocol
"""

import asyncio
import json
import subprocess
import sys
import os

class MCPTestClient:
    def __init__(self):
        self.process = None
        self.request_id = 1
    
    async def start_server(self):
        """Start the MCP server process"""
        # Get the path to the server file
        server_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'notes_server.py')
        
        self.process = subprocess.Popen(
            [sys.executable, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        print("🚀 Server process started")
    
    def send_request(self, method, params=None):
        """Send a JSON-RPC request to the server"""
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }
        if params:
            request["params"] = params
        
        request_json = json.dumps(request)
        print(f"📤 Sending: {method}")
        print(f"   Request: {request_json}")
        
        self.process.stdin.write(request_json + "\n")
        self.process.stdin.flush()
        
        # Read response
        try:
            response_line = self.process.stdout.readline()
            if response_line.strip():
                response = json.loads(response_line.strip())
                print(f"📥 Response: {json.dumps(response, indent=2)}")
                return response
            else:
                print("📥 Empty response")
                return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"   Raw response: {response_line}")
            return None
        except Exception as e:
            print(f"❌ Error reading response: {e}")
            return None
        
        self.request_id += 1
    
    async def test_full_workflow(self):
        """Test the complete MCP workflow"""
        print("=" * 50)
        print("🧪 TESTING MCP NOTES SERVER")
        print("=" * 50)
        
        try:
            # 1. Initialize the server
            print("\n1️⃣ INITIALIZING SERVER")
            init_response = self.send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            })
            
            if not init_response or "error" in init_response:
                print("❌ Initialization failed")
                return
            
            # 2. Send initialized notification
            print("\n2️⃣ SENDING INITIALIZED NOTIFICATION")
            self.send_request("notifications/initialized")
            
            # 3. List available tools
            print("\n3️⃣ LISTING AVAILABLE TOOLS")
            tools_response = self.send_request("tools/list")
            
            # 4. Test creating a note
            print("\n4️⃣ CREATING A NOTE")
            create_response = self.send_request("tools/call", {
                "name": "create_note",
                "arguments": {
                    "note_id": "test-note-1",
                    "content": "This is my first test note!"
                }
            })
            
            # 5. List all notes
            print("\n5️⃣ LISTING ALL NOTES")
            list_response = self.send_request("tools/call", {
                "name": "list_notes",
                "arguments": {}
            })
            
            # 6. Get specific note
            print("\n6️⃣ RETRIEVING SPECIFIC NOTE")
            get_response = self.send_request("tools/call", {
                "name": "get_note",
                "arguments": {
                    "note_id": "test-note-1"
                }
            })
            
            # 7. Create another note
            print("\n7️⃣ CREATING ANOTHER NOTE")
            create_response2 = self.send_request("tools/call", {
                "name": "create_note",
                "arguments": {
                    "note_id": "meeting-notes",
                    "content": "Meeting with team tomorrow at 2 PM"
                }
            })
            
            # 8. List resources
            print("\n8️⃣ LISTING RESOURCES")
            resources_response = self.send_request("resources/list")
            
            # 9. Read a resource
            print("\n9️⃣ READING A RESOURCE")
            read_response = self.send_request("resources/read", {
                "uri": "note://test-note-1"
            })
            
            # 10. Delete a note
            print("\n🔟 DELETING A NOTE")
            delete_response = self.send_request("tools/call", {
                "name": "delete_note",
                "arguments": {
                    "note_id": "test-note-1"
                }
            })
            
            # 11. List notes again to confirm deletion
            print("\n1️⃣1️⃣ LISTING NOTES AFTER DELETION")
            final_list_response = self.send_request("tools/call", {
                "name": "list_notes",
                "arguments": {}
            })
            
            print("\n" + "=" * 50)
            print("✅ ALL TESTS COMPLETED!")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
        finally:
            if self.process:
                self.process.terminate()
                print("\n🛑 Server process terminated")

async def main():
    """Main test function"""
    client = MCPTestClient()
    await client.start_server()
    await asyncio.sleep(0.1)  # Give server time to start
    await client.test_full_workflow()

if __name__ == "__main__":
    asyncio.run(main())