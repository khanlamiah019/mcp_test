"""
MCP Framework Examples

This file demonstrates how to use the MCP framework with various tools.
Students can use this as a reference for creating their own tools and examples.
"""

from mcp_framework import MCPServer
from tools import (
    calculator_tool,
    memory_tool,
    weather_tool,
    stac_list_collections_tool,
    stac_search_tool,
    stac_download_tool,
    stac_visualize_tool
)


def example_basic_tools():
    """Example: Using basic tools (calculator, memory, weather)"""
    print("=" * 70)
    print("Example 1: Basic Tools")
    print("=" * 70)
    
    server = MCPServer()
    
    # Register basic tools
    server.register_tool("calculator", calculator_tool)
    server.register_tool("memory", memory_tool)
    server.register_tool("weather", weather_tool)
    
    # Example 1: Calculator
    result = server.call_tool("calculator", {"operation": "add", "a": 10, "b": 5})
    print(f"\nCalculator: 10 + 5")
    print(f"Result: {result['result']}")
    
    # Example 2: Memory
    server.call_tool("memory", {"action": "store", "key": "user_name", "value": "Alice"})
    result = server.call_tool("memory", {"action": "retrieve", "key": "user_name"})
    print(f"\nMemory: Retrieve stored name")
    print(f"Result: {result['result']}")
    
    # Example 3: Weather
    result = server.call_tool("weather", {"city": "Beijing"})
    print(f"\nWeather: Beijing")
    print(f"Result: {result['result']}")


def example_stac_tools():
    """Example: Using STAC API tools for geospatial data"""
    print("\n" + "=" * 70)
    print("Example 2: STAC API Tools (Land Use/Land Cover)")
    print("=" * 70)
    
    server = MCPServer()
    
    # Register STAC tools
    server.register_tool("stac_list_collections", stac_list_collections_tool)
    server.register_tool("stac_search", stac_search_tool)
    server.register_tool("stac_download", stac_download_tool)
    server.register_tool("stac_visualize", stac_visualize_tool)
    
    # Example 1: List collections
    print("\n1. Listing available collections...")
    result = server.call_tool("stac_list_collections", {})
    print(result.get("result", "Error")[:500] + "...")  # Show first part
    
    # Example 2: Search for LULC data
    print("\n2. Searching for Land Use/Land Cover data (Beijing area)...")
    result = server.call_tool("stac_search", {
        "collection": "io-lulc-annual-v02",
        "bbox": [116.2, 39.8, 116.5, 40.0],  # Beijing
        "date_start": "2023-01-01",
        "date_end": "2023-12-31",
        "limit": 3
    })
    print(result.get("result", "Error"))
    
    # Example 3: Download data
    print("\n3. Downloading land cover classification raster...")
    result = server.call_tool("stac_download", {
        "item_index": 0,
        "asset_type": "data",
        "output_dir": "downloads"
    })
    print(result.get("result", "Error"))
    
    # Example 4: Visualize on map
    print("\n4. Creating map visualization...")
    result = server.call_tool("stac_visualize", {
        "item_index": 0,
        "zoom": 10,
        "output_file": "lulc_map.html"
    })
    print(result.get("result", "Error"))
    print("\nOpen 'lulc_map.html' in your browser to view the map!")


def example_custom_tool():
    """Example: Creating and using a custom tool"""
    print("\n" + "=" * 70)
    print("Example 3: Creating a Custom Tool")
    print("=" * 70)
    
    # Define a custom tool
    def greeting_tool(args: dict, context: dict) -> str:
        """A simple custom tool that greets users."""
        name = args.get("name", "Guest")
        return f"Hello, {name}! Welcome to the MCP framework."
    
    # Use the custom tool
    server = MCPServer()
    server.register_tool("greeting", greeting_tool)
    
    result = server.call_tool("greeting", {"name": "Student"})
    print(f"\nCustom Tool Result: {result['result']}")
    
    print("\nTo create your own tool:")
    print("1. Define a function with signature: func(args: Dict, context: Dict) -> str")
    print("2. Register it with: server.register_tool('tool_name', your_function)")
    print("3. Call it with: server.call_tool('tool_name', {'param': 'value'})")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("MCP Framework Examples")
    print("Model Context Protocol - Educational Framework")
    print("=" * 70)
    
    # Run examples
    example_basic_tools()
    example_stac_tools()
    example_custom_tool()
    
    print("\n" + "=" * 70)
    print("All Examples Complete!")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. Read mcp_framework.py to understand the framework")
    print("2. Study tools/basic_tools.py and tools/stac_tools.py for examples")
    print("3. Create your own tools in tools/your_tools.py")
    print("4. Register and use them in your own scripts")


if __name__ == "__main__":
    main()

