# Model Context Protocol (MCP) Python Client Implementation Guide

## Introduction

This guide focuses on implementing a Python client for the Model Context Protocol (MCP), which enables AI models to interact with external tools, resources, and services.

## Prerequisites

Before using the MCP client, make sure you have:

- Python 3.10+
- The MCP SDK installed:
  ```bash
  pip install "mcp[cli]"
  # or
  uv add "mcp[cli]"
  ```

## Basic Client Implementation

### Setting Up a Client Connection

Here's a simple implementation to connect to an MCP server using stdio transport:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    async with stdio_client(
        StdioServerParameters(
            command="python",
            args=["server.py"],
            env=None
        )
    ) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # Now you can interact with the server
            # ...

if __name__ == "__main__":
    asyncio.run(run())
```

### Listing Available Server Capabilities

Once connected, you can discover what the server offers:

```python
# List available prompts
prompts = await session.list_prompts()
print(f"Available prompts: {[p.name for p in prompts.prompts]}")

# List available resources
resources = await session.list_resources()
print(f"Available resources: {[r.uri for r in resources.resources]}")

# List available tools
tools = await session.list_tools()
print(f"Available tools: {[t.name for t in tools.tools]}")
```

## Working with Server Components

### Using Prompts

Prompts are templates that can be populated with arguments to create messages for AI models:

```python
# Get a prompt with arguments
prompt_result = await session.get_prompt(
    "code-review",
    arguments={
        "code": "def hello():\n    print('Hello, world!')",
        "language": "python"
    }
)

# Access the prompt messages
for message in prompt_result.messages:
    print(f"{message.role}: {message.content.text}")
```

### Reading Resources

Resources are data objects exposed by the server that clients can access:

```python
from mcp.types import AnyUrl

# Read a resource using its URI
content, mime_type = await session.read_resource(
    AnyUrl("file:///example.txt")
)
print(f"Resource content ({mime_type}): {content}")
```

### Calling Tools

Tools are functions on the server that clients can invoke:

```python
# Call a tool with arguments
result = await session.call_tool(
    "calculate",
    arguments={
        "operation": "add",
        "a": 5,
        "b": 3
    }
)

# Process the tool result
for content in result.content:
    if content.type == "text":
        print(f"Result: {content.text}")
    elif content.type == "image":
        print(f"Received image content")
```

## Advanced Client Implementation

### Custom Sampling Callback

You can implement a custom sampling callback to handle message creation:

```python
from mcp import types

async def handle_sampling_message(
    message: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Custom response from sampling callback",
        ),
        model="custom-model",
        stopReason="endTurn",
    )

async with ClientSession(
    read, write, sampling_callback=handle_sampling_message
) as session:
    # ... your client code
```

### Error Handling

Implement proper error handling in your client:

```python
try:
    result = await session.call_tool("example", {"arg": "value"})
    # Process successful result
except Exception as e:
    print(f"Tool call failed: {str(e)}")
    # Handle the error appropriately
```

### Lifecycle Management with Context Managers

Use context managers to properly manage resources:

```python
from contextlib import AsyncExitStack

async def run_client():
    exit_stack = AsyncExitStack()
    try:
        # Set up connections with proper cleanup
        stdio_transport = await exit_stack.enter_async_context(
            stdio_client(StdioServerParameters(command="python", args=["server.py"]))
        )
        session = await exit_stack.enter_async_context(
            ClientSession(stdio_transport[0], stdio_transport[1])
        )
        
        # Use the session
        await session.initialize()
        # ... more code ...
        
    finally:
        # This ensures all resources are cleaned up
        await exit_stack.aclose()
```

## Complete MCP Client Example

Here's a more comprehensive example that integrates with the Anthropic API to create an interactive client:

```python
import asyncio
import sys
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
    
    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server"""
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
    
    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        final_text = []

        assistant_message_content = []
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                assistant_message_content.append(content)
                messages.append({
                    "role": "assistant",
                    "content": assistant_message_content
                })
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content
                        }
                    ]
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)
    
    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## Alternative Transport: SSE

While stdio is the default transport, you can also use Server-Sent Events (SSE) for HTTP-based communication:

```python
from mcp.client.sse import sse_client

async def run():
    async with sse_client("http://localhost:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # ... client code ...
```

## Best Practices

1. **Resource Management**: Always use context managers to ensure proper cleanup
2. **Error Handling**: Implement robust error handling for all server interactions
3. **Validation**: Validate server responses to handle unexpected data
4. **Timeouts**: Add appropriate timeouts for server operations
5. **Logging**: Implement logging to track client-server communications
6. **Graceful Degradation**: Handle server disconnections gracefully

## Troubleshooting

Common issues and solutions:

1. **Connection Failures**: 
   - Verify the server is running
   - Check if the command and arguments are correct
   - Ensure environment variables are properly set

2. **Tool Call Failures**:
   - Verify the tool exists using `list_tools()`
   - Ensure arguments match the expected schema
   - Check server logs for details on failures

3. **Resource Not Found**:
   - Verify the URI is correct and supported
   - Check if the resource is listed in `list_resources()`

4. **Initialization Errors**:
   - Make sure the server is compatible with the client version
   - Check if the server implements required capabilities
