# Model Context Protocol (MCP) Python Server Implementation Guide

## Introduction

This guide focuses on how to implement an MCP server in Python, allowing you to expose tools, resources, and prompts to AI models and clients.

## Prerequisites

- Python 3.10+
- MCP SDK installed:
  ```bash
  pip install "mcp[cli]"
  # or
  uv add "mcp[cli]"
  ```

## Server Implementation Approaches

The MCP Python SDK offers two main approaches to implementing a server:

1. **High-level API (FastMCP)**: Simplified, decorator-based approach
2. **Low-level API (Server)**: More control but requires more detailed implementation

## Quick Start with FastMCP

The FastMCP class provides a simpler way to create servers with decorators:

```python
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Calculator")

# Add a tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Run the server
if __name__ == "__main__":
    mcp.run()
```

## Core Server Components

### Tools

Tools are functions that perform operations on behalf of clients:

```python
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My App")

# Synchronous tool
@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m**2)

# Asynchronous tool
@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.weather.com/{city}")
        return response.text
```

### Resources

Resources are static or dynamic data exposed by servers:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My App")

# Static resource
@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "App configuration here"

# Dynamic resource with path parameters
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Dynamic user data"""
    return f"Profile data for user {user_id}"
```

### Prompts

Prompts are templates for generating text that can be customized with arguments:

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("My App")

# Simple string prompt
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"

# Multi-message prompt
@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]
```

## Advanced Server Features

### Using Context for Enhanced Capabilities

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("My App")

@mcp.tool()
async def long_task(files: list[str], ctx: Context) -> str:
    """Process multiple files with progress tracking"""
    for i, file in enumerate(files):
        # Log messages to client
        ctx.info(f"Processing {file}")
        
        # Report progress
        await ctx.report_progress(i, len(files))
        
        # Access resources directly from context
        data, mime_type = await ctx.read_resource(f"file://{file}")
        
    return "Processing complete"
```

### Working with Images

```python
from mcp.server.fastmcp import FastMCP, Image
from PIL import Image as PILImage

mcp = FastMCP("My App")

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")
```

### Error Handling

```python
from mcp import types
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My App")

@mcp.tool()
def division_tool(a: float, b: float) -> types.CallToolResult:
    """Divide two numbers"""
    try:
        if b == 0:
            raise ValueError("Cannot divide by zero")
            
        result = a / b
        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"Result: {result}"
                )
            ]
        )
    except Exception as error:
        return types.CallToolResult(
            isError=True,
            content=[
                types.TextContent(
                    type="text",
                    text=f"Error: {str(error)}"
                )
            ]
        )
```

### Lifespan Management for Resources

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP

@dataclass
class AppContext:
    db: object  # Replace with your database type
    api_client: object  # Replace with your API client type

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    print("Starting up server resources...")
    
    # Initialize resources on startup
    db = await connect_database()
    api_client = initialize_api_client()
    
    try:
        # Provide context to server
        yield AppContext(db=db, api_client=api_client)
    finally:
        # Clean up on shutdown
        print("Shutting down server resources...")
        await db.disconnect()
        await api_client.close()

# Pass lifespan to server
mcp = FastMCP("My App", lifespan=app_lifespan)

# Access lifespan context in tools
@mcp.tool()
def query_db(query: str, ctx: Context) -> str:
    """Execute database query"""
    db = ctx.request_context.lifespan_context.db
    result = db.execute(query)
    return str(result)
```

## Low-Level Server Implementation

For more control, you can use the low-level Server class:

```python
import asyncio
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("example-server")

@app.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri="example://resource",
            name="Example Resource"
        )
    ]

@app.read_resource()
async def read_resource(uri: types.AnyUrl) -> str:
    if str(uri) == "example://resource":
        return "Resource content here"
    raise ValueError("Resource not found")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="example-tool",
            description="An example tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                },
                "required": ["param"]
            }
        )
    ]

@app.call_tool()
async def call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if name == "example-tool":
        param = arguments["param"]
        return [types.TextContent(type="text", text=f"Result: {param}")]
    raise ValueError(f"Tool not found: {name}")

async def main():
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## Server Transport Options

### Stdio Transport (Default)

The stdio transport communicates through standard input and output streams:

```python
from mcp.server.stdio import stdio_server

async with stdio_server() as streams:
    await app.run(
        streams[0],
        streams[1],
        app.create_initialization_options()
    )
```

### SSE Transport (HTTP-based)

Server-Sent Events transport provides HTTP-based communication:

```python
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route

app = Server("example-server")
sse = SseServerTransport("/messages")

async def handle_sse(scope, receive, send):
    async with sse.connect_sse(scope, receive, send) as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options())

async def handle_messages(scope, receive, send):
    await sse.handle_post_message(scope, receive, send)

starlette_app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
    ]
)
```

### Mounting to Existing ASGI Server

You can mount an MCP server to an existing ASGI server:

```python
from starlette.applications import Starlette
from starlette.routing import Mount, Host
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My App")

# Mount the SSE server to the existing ASGI server
app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app()),
    ]
)

# or dynamically mount as host
app.router.routes.append(Host('mcp.acme.corp', app=mcp.sse_app()))
```

## Development and Deployment

### Development Mode

```bash
# Basic development mode
mcp dev server.py

# Add dependencies
mcp dev server.py --with pandas --with numpy

# Mount local code
mcp dev server.py --with-editable .
```

### Installing in Claude Desktop

```bash
# Basic install
mcp install server.py

# Custom name
mcp install server.py --name "My Analytics Server"

# Environment variables
mcp install server.py -v API_KEY=abc123 -v DB_URL=postgres://...
mcp install server.py -f .env
```

### Running a Server

```bash
# Direct execution
python server.py

# Using MCP CLI
mcp run server.py

# Using stdio transport (default)
uv run my-mcp-server

# Using SSE transport on custom port
uv run my-mcp-server --transport sse --port 8000
```

### Testing with Inspector

```bash
# For Python servers
mcp dev server.py

# Using npx with uv
npx @modelcontextprotocol/inspector \
  uv \
  --directory path/to/server \
  run \
  package-name \
  args...
```

## Example Implementations

### Complete Echo Server

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Echo")

@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"

@mcp.tool()
def echo_tool(message: str) -> str:
    """Echo a message as a tool"""
    return f"Tool echo: {message}"

@mcp.prompt()
def echo_prompt(message: str) -> str:
    """Create an echo prompt"""
    return f"Please process this message: {message}"

if __name__ == "__main__":
    mcp.run()
```

### SQLite Explorer

```python
import sqlite3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SQLite Explorer")

@mcp.resource("schema://main")
def get_schema() -> str:
    """Provide the database schema as a resource"""
    conn = sqlite3.connect("database.db")
    schema = conn.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall()
    return "\n".join(sql[0] for sql in schema if sql[0])

@mcp.tool()
def query_data(sql: str) -> str:
    """Execute SQL queries safely"""
    conn = sqlite3.connect("database.db")
    try:
        result = conn.execute(sql).fetchall()
        return "\n".join(str(row) for row in result)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
```

## Best Practices

1. **Use Type Hints**: Always use proper type hints for better IDE support and validation
2. **Document Everything**: Provide clear descriptions for tools, resources, and prompts
3. **Input Validation**: Validate all inputs to prevent runtime errors
4. **Error Handling**: Implement comprehensive error handling for all operations
5. **Resource Management**: Use lifespans to properly manage external resources
6. **Progress Reporting**: For long-running tasks, provide progress updates
7. **Logging**: Implement proper logging for debugging and monitoring
8. **Security**: Never expose sensitive operations without proper validation
9. **Performance**: For expensive operations, consider caching strategies
10. **Testability**: Design your server to be easily testable

## Troubleshooting

Common issues and solutions:

1. **Transport Errors**:
   - Verify the transport configuration is correct
   - Check for port conflicts with SSE transport
   - Ensure proper permissions for stdio

2. **Serialization Errors**:
   - Ensure all returned types are compatible with MCP
   - Check for circular references in returned objects
   - Verify all objects are JSON-serializable

3. **Resource Errors**:
   - Verify resource paths are correctly formatted
   - Ensure resources are accessible from server
   - Check permissions for file resources

4. **Tool Execution Errors**:
   - Validate input parameters before execution
   - Provide clear error messages
   - Implement proper exception handling
