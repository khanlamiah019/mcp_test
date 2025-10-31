"""
Toy MCP Client Example

This demonstrates how an AI model (or client) would interact with an MCP server.
The client requests tools to be executed and processes the results.
"""

from mcp_server import MCPServer, calculator_tool, memory_tool, weather_tool
import json


class MCPClient:
    """
    A simple MCP client that simulates how an AI model would interact
    with an MCP server.
    """
    
    def __init__(self, server: MCPServer):
        self.server = server
        
    def process_user_request(self, user_input: str):
        """
        Simulates how an AI model would interpret user input and decide
        which tools to call.
        """
        print(f"\nUser says: {user_input}")
        print("-" * 50)
        
        # Simulate AI understanding the intent and calling appropriate tools
        user_lower = user_input.lower()
        
        # Example 1: Calculator requests
        if "add" in user_lower or "+" in user_lower:
            # Extract numbers (simplified - in reality, AI would parse this better)
            if "10" in user_input and "5" in user_input:
                result = self.server.call_tool("calculator", {
                    "operation": "add",
                    "a": 10,
                    "b": 5
                })
                print(f"AI decided to use: calculator tool")
                print(f"Tool response: {result['result']}")
                return result['result']
        
        elif "multiply" in user_lower or "*" in user_lower or "times" in user_lower:
            if "7" in user_input and "8" in user_input:
                result = self.server.call_tool("calculator", {
                    "operation": "multiply",
                    "a": 7,
                    "b": 8
                })
                print(f"AI decided to use: calculator tool")
                print(f"Tool response: {result['result']}")
                return result['result']
        
        # Example 2: Weather requests
        elif "weather" in user_lower:
            # Extract city name (simplified)
            cities = ["Beijing", "Shanghai", "New York", "London"]
            for city in cities:
                if city.lower() in user_lower:
                    result = self.server.call_tool("weather", {
                        "city": city
                    })
                    print(f"AI decided to use: weather tool")
                    print(f"Tool response: {result['result']}")
                    return result['result']
        
        # Example 3: Memory operations
        elif "remember" in user_lower or "store" in user_lower:
            # Simplified: would parse the actual key-value from user input
            if "alice" in user_lower or "name" in user_lower:
                result = self.server.call_tool("memory", {
                    "action": "store",
                    "key": "user_name",
                    "value": "Alice"
                })
                print(f"AI decided to use: memory tool")
                print(f"Tool response: {result['result']}")
                return result['result']
        
        elif "what is my name" in user_lower or "my name" in user_lower:
            result = self.server.call_tool("memory", {
                "action": "retrieve",
                "key": "user_name"
            })
            print(f"AI decided to use: memory tool")
            print(f"Tool response: {result['result']}")
            return result['result']
        
        else:
            print("AI: I don't understand or don't have a tool for that.")
            return "No suitable tool found"


# Main execution example
if __name__ == "__main__":
    print("=" * 50)
    print("Toy MCP Client Example")
    print("=" * 50)
    print("\nThis simulates how an AI model would use MCP tools")
    print("to fulfill user requests.\n")
    
    # Create server and client
    server = MCPServer()
    server.register_tool("calculator", calculator_tool)
    server.register_tool("memory", memory_tool)
    server.register_tool("weather", weather_tool)
    
    client = MCPClient(server)
    
    # Simulate conversation
    print("\n" + "=" * 50)
    print("Simulated Conversation")
    print("=" * 50)
    
    client.process_user_request("What is 10 + 5?")
    client.process_user_request("What is 7 times 8?")
    client.process_user_request("What's the weather in Beijing?")
    client.process_user_request("Remember that my name is Alice")
    client.process_user_request("What is my name?")
    
    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)

