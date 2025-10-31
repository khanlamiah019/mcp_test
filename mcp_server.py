"""
Toy MCP Server Example

This demonstrates a simple MCP (Model Context Protocol) server that:
1. Provides tools that AI models can call
2. Handles requests and returns responses
3. Maintains context across interactions
"""

import json
from typing import Dict, Any, List


class MCPServer:
    """
    A simple MCP server that provides tools and resources.
    
    MCP (Model Context Protocol) allows AI models to:
    - Call tools (functions) to perform actions
    - Access resources (data) for context
    - Interact with external systems
    """
    
    def __init__(self):
        self.tools = {}
        self.context = {}  # Store context/session data
        
    def register_tool(self, name: str, tool_func):
        """Register a tool that can be called by the AI model."""
        self.tools[name] = tool_func
        print(f"✓ Registered tool: {name}")
        
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a registered tool with given arguments."""
        if tool_name not in self.tools:
            return {
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tools.keys())
            }
        
        try:
            tool_func = self.tools[tool_name]
            result = tool_func(arguments, self.context)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}
    
    def set_context(self, key: str, value: Any):
        """Store data in the server context (like session storage)."""
        self.context[key] = value
        
    def get_context(self, key: str, default=None):
        """Retrieve data from the server context."""
        return self.context.get(key, default)


# Example Tools
def calculator_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """A simple calculator tool."""
    operation = args.get("operation")
    a = float(args.get("a", 0))
    b = float(args.get("b", 0))
    
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Cannot divide by zero"
    }
    
    if operation not in operations:
        return f"Unknown operation: {operation}. Available: {list(operations.keys())}"
    
    result = operations[operation](a, b)
    return f"{a} {operation} {b} = {result}"


def memory_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """A tool that stores and retrieves memories."""
    action = args.get("action")
    key = args.get("key")
    
    if action == "store":
        value = args.get("value")
        context[f"memory_{key}"] = value
        return f"Stored '{value}' with key '{key}'"
    
    elif action == "retrieve":
        value = context.get(f"memory_{key}", None)
        if value is None:
            return f"No memory found for key '{key}'"
        return f"Retrieved: {value}"
    
    else:
        return f"Unknown action: {action}. Use 'store' or 'retrieve'"


def weather_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """A mock weather tool."""
    city = args.get("city", "Unknown")
    # This is a toy example, so we return mock data
    mock_weather = {
        "Beijing": "Sunny, 25°C",
        "Shanghai": "Cloudy, 22°C",
        "New York": "Rainy, 18°C",
        "London": "Foggy, 15°C"
    }
    
    weather = mock_weather.get(city, f"Unknown city: {city}")
    return f"Weather in {city}: {weather}"


# Main execution example
if __name__ == "__main__":
    print("=" * 50)
    print("Toy MCP Server Example")
    print("=" * 50)
    
    # Create server instance
    server = MCPServer()
    
    # Register tools
    server.register_tool("calculator", calculator_tool)
    server.register_tool("memory", memory_tool)
    server.register_tool("weather", weather_tool)
    
    print("\n" + "=" * 50)
    print("Example: Using the calculator tool")
    print("=" * 50)
    
    # Example 1: Use calculator
    result1 = server.call_tool("calculator", {
        "operation": "add",
        "a": 10,
        "b": 5
    })
    print(f"Request: Calculate 10 + 5")
    print(f"Response: {json.dumps(result1, indent=2)}")
    
    print("\n" + "=" * 50)
    print("Example: Using the memory tool")
    print("=" * 50)
    
    # Example 2: Store a memory
    result2 = server.call_tool("memory", {
        "action": "store",
        "key": "user_name",
        "value": "Alice"
    })
    print(f"Request: Store memory")
    print(f"Response: {json.dumps(result2, indent=2)}")
    
    # Retrieve the memory
    result3 = server.call_tool("memory", {
        "action": "retrieve",
        "key": "user_name"
    })
    print(f"Request: Retrieve memory")
    print(f"Response: {json.dumps(result3, indent=2)}")
    
    print("\n" + "=" * 50)
    print("Example: Using the weather tool")
    print("=" * 50)
    
    # Example 3: Get weather
    result4 = server.call_tool("weather", {
        "city": "Beijing"
    })
    print(f"Request: Get weather for Beijing")
    print(f"Response: {json.dumps(result4, indent=2)}")
    
    print("\n" + "=" * 50)
    print("Example: Error handling")
    print("=" * 50)
    
    # Example 4: Error - unknown tool
    result5 = server.call_tool("unknown_tool", {})
    print(f"Request: Call unknown tool")
    print(f"Response: {json.dumps(result5, indent=2)}")
    
    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)

