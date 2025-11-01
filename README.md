# MCP Framework - Model Context Protocol

A simple, educational framework for creating MCP (Model Context Protocol) tools. This framework allows AI models to interact with external tools and resources through a clean, extensible interface.

## What is MCP?

**Model Context Protocol (MCP)** enables AI models to:
- **Call tools**: Execute functions to perform actions (calculations, API calls, etc.)
- **Access resources**: Retrieve data or information when needed
- **Maintain context**: Remember information across interactions

Think of it as giving an AI assistant the ability to:
- Use a calculator (tool)
- Check the weather (tool)
- Remember your name (context/memory)
- Access geospatial data (STAC API tool)

## Project Structure

```
├── mcp_framework.py       # Core framework (MCPServer class)
├── tools/                  # Tool modules
│   ├── __init__.py        # Tool exports
│   ├── basic_tools.py      # Example tools (calculator, memory, weather)
│   └── stac_tools.py      # STAC API tools (geospatial data)
├── examples.py            # Comprehensive examples
├── requirements.txt       # Python dependencies
└── README.md              # This file
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

This demonstrates:
- Basic tools (calculator, memory, weather)
- STAC API tools (geospatial data access)
- Creating custom tools

## Framework Usage

### Basic Usage

```python
from mcp_framework import MCPServer
from tools import calculator_tool, memory_tool

# Create server
server = MCPServer()

# Register tools
server.register_tool("calculator", calculator_tool)
server.register_tool("memory", memory_tool)

# Use tools
result = server.call_tool("calculator", {
    "operation": "add",
    "a": 10,
    "b": 5
})
print(result["result"])  # "10 add 5 = 15"
```

### Creating Your Own Tool

```python
from mcp_framework import MCPServer
from typing import Dict, Any

def my_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """My custom tool."""
    name = args.get("name", "World")
    return f"Hello, {name}!"

# Register and use
server = MCPServer()
server.register_tool("greeting", my_tool)
result = server.call_tool("greeting", {"name": "Student"})
```

## Example Tools Included

### Basic Tools (`tools/basic_tools.py`)

1. **`calculator_tool`**: Simple arithmetic operations
   - Operations: add, subtract, multiply, divide
   - Args: `operation`, `a`, `b`

2. **`memory_tool`**: Store and retrieve data (context persistence example)
   - Actions: store, retrieve
   - Args: `action`, `key`, `value` (for store)

3. **`weather_tool`**: Mock weather data (API simulation example)
   - Args: `city`

### STAC API Tools (`tools/stac_tools.py`)

4. **`stac_list_collections_tool`**: List available geospatial datasets

5. **`stac_search_tool`**: Search for geospatial data
   - Args: `collection`, `bbox`, `date_start`, `date_end`, `limit`
   - Example: `{"collection": "io-lulc-annual-v02", "bbox": [116.2, 39.8, 116.5, 40.0]}`

6. **`stac_download_tool`**: Download geospatial data files
   - Args: `item_index`, `asset_type`, `output_dir`

7. **`stac_visualize_tool`**: Create interactive maps
   - Args: `item_index`, `zoom`, `output_file`, `image_path` (optional)

## STAC API Example

```python
from mcp_framework import MCPServer
from tools import (
    stac_search_tool,
    stac_download_tool,
    stac_visualize_tool
)

server = MCPServer()
server.register_tool("stac_search", stac_search_tool)
server.register_tool("stac_download", stac_download_tool)
server.register_tool("stac_visualize", stac_visualize_tool)

# Search for Land Use/Land Cover data
result = server.call_tool("stac_search", {
    "collection": "io-lulc-annual-v02",
    "bbox": [116.2, 39.8, 116.5, 40.0],  # Beijing
    "date_start": "2023-01-01",
    "date_end": "2023-12-31"
})

# Download the data
result = server.call_tool("stac_download", {
    "item_index": 0,
    "asset_type": "data"
})

# Visualize on map
result = server.call_tool("stac_visualize", {
    "item_index": 0,
    "output_file": "map.html"
})
```

## Popular STAC Collections

- **`io-lulc-annual-v02`**: 10m Annual Land Use/Land Cover (9 classes)
- **`sentinel-2-l2a`**: Sentinel-2 satellite imagery (10m resolution)
- **`landsat-c2-l2`**: Landsat satellite imagery (30m resolution)
- **`modis-09a1`**: MODIS surface reflectance data
- **`naip`**: National Agriculture Imagery Program

### Understanding Bounding Boxes

Bounding boxes use: `[min_longitude, min_latitude, max_longitude, max_latitude]`

Example (Beijing):
- Longitude: 116.2°E to 116.5°E
- Latitude: 39.8°N to 40.0°N
- Bbox: `[116.2, 39.8, 116.5, 40.0]`

## Key Concepts

### 1. Tools
Tools are functions with signature: `func(args: Dict[str, Any], context: Dict[str, Any]) -> str`

### 2. Server
The MCPServer class:
- Registers tools
- Executes tools
- Maintains context across calls

### 3. Context
Shared data that persists across tool calls:
```python
server.set_context("key", "value")
value = server.get_context("key")
```

## Extending the Framework

### Adding New Tools

1. Create a new file in `tools/` directory (e.g., `tools/my_tools.py`)
2. Define your tool functions following the signature pattern
3. Export them in `tools/__init__.py`
4. Import and register in your code

Example:
```python
# tools/my_tools.py
def my_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    param = args.get("param", "default")
    return f"Result: {param}"
```

## Requirements

Core dependencies:
- Python 3.7+

For STAC tools:
- `requests` - HTTP requests
- `planetary-computer` - URL signing for Microsoft Planetary Computer
- `rasterio` - Geospatial raster I/O
- `folium` - Interactive maps
- `numpy` - Numerical operations

## Authentication

Microsoft Planetary Computer requires URL signing to access data files. The `planetary-computer` package handles this automatically - no account needed for basic usage.

## Learning Path

1. **Start Simple**: Run `examples.py` to see basic tools in action
2. **Study Examples**: Read `tools/basic_tools.py` to understand tool structure
3. **Explore STAC**: Try the STAC tools with different collections
4. **Create Your Own**: Add new tools to the `tools/` directory
5. **Extend Framework**: Modify `mcp_framework.py` if needed

## Next Steps

- Read through `mcp_framework.py` to understand the core framework
- Study `tools/basic_tools.py` for simple tool examples
- Examine `tools/stac_tools.py` for API integration examples
- Create your own tools following the patterns
- Experiment with different STAC collections and regions

## License

Educational use - designed for learning and teaching MCP concepts.
