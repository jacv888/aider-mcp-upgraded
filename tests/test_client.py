import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main():
    # Connect to the MCP server using stdio transport
    async with stdio_client(
        StdioServerParameters(command="python", args=["aider_mcp.py"])
    ) as (read, write):
        # Create a client session
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools_result = await session.list_tools()
            print("\nAvailable tools:")
            for tool in tools_result.tools:
                print(f"- {tool.name}: {tool.description}")
            
            # Call the hello tool
            hello_result = await session.call_tool("hello", {"name": "MCP User"})
            print(f"\nHello tool result: {hello_result.content[0].text}")
            
            # Call the calculate tool
            calc_result = await session.call_tool(
                "calculate", 
                {"operation": "add", "a": 5, "b": 7}
            )
            print(f"Calculate tool result: {calc_result.content[0].text}")
            
            # List available resources
            resources_result = await session.list_resources()
            print("\nAvailable resources:")
            for resource in resources_result.resources:
                print(f"- {resource.uri_template}")
            
            # Read a resource
            resource_result = await session.read_resource("greeting://Friend")
            print(f"\nResource content: {resource_result.contents[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
