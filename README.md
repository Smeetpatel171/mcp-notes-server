# MCP Notes Server

A simple Model Context Protocol (MCP) server for managing text notes.

## Features
- Create notes with unique IDs
- Retrieve notes by ID
- List all available notes
- Delete notes
- MCP-compliant resource and tool interfaces

## Installation

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`

## Usage

### Running the Server
```bash
python src/notes_server.py