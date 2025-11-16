# Contributing Guide

Welcome to the MCP Framework project! This guide will help you get started.

## Project Structure

```
├── README.md              # Project documentation
├── CONTRIBUTING.md        # This file - contribution guidelines
├── mcp_framework.py       # Core framework
├── examples.py            # Usage examples
├── requirements.txt       # Python dependencies
├── tools/                 # Tool modules
│   ├── basic_tools.py     # Basic tool examples
│   └── stac_tools.py      # STAC API tools (geospatial data)
├── team1a/                # Team 1A workspace
│   ├── victor/            # Victor's working directory
│   ├── lamiah/            # Lamiah's working directory
│   ├── jessica/           # Jessica's working directory
│   └── karina/            # Karina's working directory
└── team1b/                # Team 1B workspace
    ├── joey/              # Joey's working directory
    ├── furkan/            # Furkan's working directory
    ├── ashleigh/          # Ashleigh's working directory
    └── neeti/             # Neeti's working directory
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Examples

```bash
python examples.py
```

This will show you how to use the framework and tools.

### 3. Work in Your Directory

Each student has their own directory (e.g., `team1a/victor/`). In this directory:
- Create your own scripts
- Test new tools
- Develop your features

## Creating New Tools

### Tool Format

All tools should follow this format:

```python
def my_tool(args, context):
    """
    Tool description
    
    args: Dictionary with parameters, e.g., {"param1": "value1"}
    context: Shared context (can store data between tool calls)
    
    Returns: String result
    """
    # Your tool logic
    return "Result"
```

### Example: Creating a LULC Analysis Tool

Let's create a tool to analyze Land Use/Land Cover (LULC) data. Create a file in your directory:

```python
# team1a/victor/lulc_tools.py
from typing import Dict, Any

def lulc_analyze_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Tool to analyze LULC data
    
    Parameters:
        args: {
            "collection": "io-lulc-annual-v02",  # LULC dataset
            "bbox": [-122.5, 37.7, -122.3, 37.8],  # Area bounds [min_lon, min_lat, max_lon, max_lat] (California)
            "year": "2023"  # Year
        }
        context: Shared context (can store search results)
    
    Returns: Analysis result string
    """
    # 1. Get information from parameters
    collection = args.get("collection", "io-lulc-annual-v02")
    bbox = args.get("bbox", [-122.5, 37.7, -122.3, 37.8])  # California area
    year = args.get("year", "2023")
    
    # 2. Use existing STAC search tool (get from context or call directly)
    # Assume you've already run a search, results are in context
    last_search = context.get("last_search", {})
    items = last_search.get("items", [])
    
    if not items:
        return "Error: No data found. Please run a search first."
    
    # 3. Analyze data (example logic)
    item_count = len(items)
    result = f"Found {item_count} LULC data items\n"
    result += f"Area: {bbox}\n"
    result += f"Year: {year}\n"
    result += f"Dataset: {collection}\n"
    
    # Add more analysis logic here...
    
    return result

# Test the tool
if __name__ == "__main__":
    from mcp_framework import MCPServer
    from tools import stac_search_tool
    
    # Create server
    server = MCPServer()
    
    # First, register search tool and search for LULC data
    server.register_tool("stac_search", stac_search_tool)
    server.call_tool("stac_search", {
        "collection": "io-lulc-annual-v02",
        "bbox": [-122.5, 37.7, -122.3, 37.8],  # California area
        "date_start": "2023-01-01",
        "date_end": "2023-12-31"
    })
    
    # Register and test your new tool
    server.register_tool("lulc_analyze", lulc_analyze_tool)
    result = server.call_tool("lulc_analyze", {
        "collection": "io-lulc-annual-v02",
        "bbox": [-122.5, 37.7, -122.3, 37.8],  # California area
        "year": "2023"
    })
    print(result)
```

### Steps to Use

1. **Create a file in your directory**: e.g., `team1a/victor/lulc_tools.py`
2. **Define your tool function**: Follow the format above
3. **Test your tool**: Run the file to see if it works
4. **Share with team**: If the tool is useful, share it with your team

## Workflow

1. **Read documentation**: Start with `README.md` to understand the project
2. **Run examples**: Run `python examples.py` to see how it works
3. **Study existing tools**: Check `tools/basic_tools.py` and `tools/stac_tools.py`
4. **Create your tools**: Develop in your directory
5. **Test**: Make sure your code runs without errors

## Best Practices

- **Write clear code**: Make it easy to understand, add comments when needed
- **Test your code**: Run it to make sure there are no errors
- **Organize files**: Keep your work in your own directory
- **Use clear names**: Use meaningful file and variable names

## Team Collaboration

- Communicate with team members
- Share ideas and solutions
- Help each other solve problems
- Ask questions when needed

## Need Help?

1. Check `README.md` to understand the project
2. Run `examples.py` to see examples
3. Look at tool code in the `tools/` directory
4. Ask team members or instructor

## Tips

1. **Start small**: Begin with simple tools, then add more features
2. **Experiment**: Try different approaches, learn from mistakes
3. **Read code**: Study how existing tools are implemented
4. **Ask questions**: Don't hesitate to ask for help

Happy coding! 🚀

