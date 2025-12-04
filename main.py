from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo", json_response=True)


# Add an addition tool，工具调用
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# 读取文件内容
@mcp.tool()
def read_file(file_path: str) -> str:
    """Read the content of a file"""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Add a dynamic greeting resource，提供资源
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Add a prompt， 提供回复格式
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."


# Run with streamable HTTP transport
if __name__ == "__main__":
    mcp.run(transport="stdio")
