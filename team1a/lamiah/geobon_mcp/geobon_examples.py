"""
Test Script - GEO BON ACTUAL DATA Retrieval

This script demonstrates the difference between:
- ❌ OLD: Just showing coverage area (bounding box)
- ✅ NEW: Actually retrieving and processing real data from STAC assets

The improved tools now:
1. Download/read actual GeoTIFF raster data
2. Calculate real statistics (hectares, percentages)
3. Show actual forest loss values by year
4. Provide ESG-relevant metrics
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import the improved version
from geobon_stac_tools import GEOBON_TOOLS


class SimpleMCPServer:
    """Minimal MCP server for testing"""
    def __init__(self):
        self.tools = {}
        self.context = {}  # Shared context between tools
    
    def register_tool(self, name, func):
        self.tools[name] = func
    
    def call_tool(self, name, args):
        if name not in self.tools:
            return {"error": f"Tool '{name}' not found"}
        try:
            result = self.tools[name](args, self.context)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


def test_coverage_vs_actual_data():
    """
    Demonstrate the difference between coverage area and actual data retrieval.
    """
    
    print("\n" + "=" * 70)
    print("GEO BON STAC: Coverage Area vs ACTUAL DATA")
    print("=" * 70)
    
    server = SimpleMCPServer()
    
    # Register all tools
    for tool_name, tool_func in GEOBON_TOOLS.items():
        server.register_tool(tool_name, tool_func)
    
    print("\n📋 Available tools:")
    for name in GEOBON_TOOLS.keys():
        print(f"   • {name}")
    
    # Step 1: Search for forest loss data
    print("\n" + "-" * 70)
    print("STEP 1: Search for forest loss collection")
    print("-" * 70)
    
    result = server.call_tool("geobon_search_collection", {
        "collection_id": "gfw-lossyear",
        "limit": 2
    })
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        print("\nTrying alternative collection...")
        result = server.call_tool("geobon_list_collections", {"limit": 5})
        print(result.get("result", result.get("error")))
        return
    
    print(result["result"][:1500] + "...")  # Truncate long output
    
    # Step 2: Get detailed asset information
    print("\n" + "-" * 70)
    print("STEP 2: Examine asset details (data URLs)")
    print("-" * 70)
    
    result = server.call_tool("geobon_get_asset_info", {"item_index": 0})
    print(result.get("result", result.get("error")))
    
    # Step 3: OLD WAY - Just visualize coverage (what you had before)
    print("\n" + "-" * 70)
    print("STEP 3a: OLD WAY - Coverage Area Only (what you had)")
    print("-" * 70)
    
    result = server.call_tool("geobon_visualize_forest_loss", {
        "item_index": 0,
        "output_file": "OLD_coverage_only.html",
        "region_name": "Test Region"
    })
    print(result.get("result", result.get("error")))
    
    # Step 4: NEW WAY - Get ACTUAL DATA
    print("\n" + "-" * 70)
    print("STEP 3b: NEW WAY - Retrieve ACTUAL DATA!")
    print("-" * 70)
    
    # This is the key new functionality!
    result = server.call_tool("geobon_get_raster_data", {
        "item_index": 0,
        "calculate_stats": True
    })
    
    if "error" in result:
        print(f"❌ Error retrieving actual data: {result['error']}")
        print("\nThis typically means:")
        print("  1. rasterio is not installed (pip install rasterio)")
        print("  2. The asset URL is not publicly accessible")
        print("  3. Network connectivity issues")
    else:
        print("✅ ACTUAL DATA Retrieved!")
        print(result["result"])
    
    # Step 5: Calculate detailed forest loss statistics
    print("\n" + "-" * 70)
    print("STEP 4: Calculate Forest Loss Statistics (ESG metrics)")
    print("-" * 70)
    
    # For a specific region (example: part of Brazil's Amazon)
    amazon_bbox = [-65, -10, -55, 0]  # West Amazon region
    
    result = server.call_tool("geobon_calculate_forest_loss_stats", {
        "item_index": 0,
        "bbox": amazon_bbox,
        "start_year": 2015,
        "end_year": 2023
    })
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(result["result"])
    
    # Step 6: Create visualization WITH actual data
    print("\n" + "-" * 70)
    print("STEP 5: Create Map WITH Actual Data")
    print("-" * 70)
    
    result = server.call_tool("geobon_visualize_forest_loss", {
        "item_index": 0,
        "output_file": "NEW_with_actual_data.html",
        "region_name": "Amazon Region"
    })
    print(result.get("result", result.get("error")))
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: What Changed")
    print("=" * 70)
    print("""
❌ OLD APPROACH (what you had):
   - Searched STAC catalog
   - Got bounding box coordinates
   - Drew a red box on map showing WHERE data exists
   - But never actually READ the data!

✅ NEW APPROACH (fixed version):
   - Search STAC catalog ✓
   - Get asset URLs (actual data files) ✓
   - READ the GeoTIFF raster data ✓
   - Calculate statistics (pixels, hectares, years) ✓
   - Show ACTUAL VALUES on the map ✓
   - Provide ESG-relevant metrics ✓

Key New Tools:
   • geobon_get_asset_info - See what data files are available
   • geobon_get_raster_data - Read and analyze actual GeoTIFF data
   • geobon_calculate_forest_loss_stats - Get detailed loss statistics

Dependencies needed:
   pip install rasterio numpy folium requests
""")


def test_simple_search():
    """Quick test to just list available collections"""
    server = SimpleMCPServer()
    
    for tool_name, tool_func in GEOBON_TOOLS.items():
        server.register_tool(tool_name, tool_func)
    
    print("\n📋 Listing GEO BON Collections...")
    result = server.call_tool("geobon_list_collections", {"limit": 10})
    print(result.get("result", result.get("error")))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test GEO BON STAC Tools")
    parser.add_argument("--simple", action="store_true", help="Just list collections")
    args = parser.parse_args()
    
    if args.simple:
        test_simple_search()
    else:
        try:
            test_coverage_vs_actual_data()
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("\nRunning simple test instead...")
            test_simple_search()
