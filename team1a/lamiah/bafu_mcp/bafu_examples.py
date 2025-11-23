"""
BAFU STAC Tools Enhanced - Usage Examples

This file demonstrates how to properly fetch and visualize ACTUAL geospatial 
data from BAFU - not just coverage areas/bounding boxes.

Key Difference from Original:
- Original: Shows WHERE data exists (bounding box)
- Enhanced: Shows WHAT the data contains (actual flood zones, hazard areas, etc.)
"""

from bafu_stac_tools import BAFU_TOOLS


class SimpleContext:
    """Simple context manager for storing data between tool calls."""
    def __init__(self):
        self._data = {}
    
    def __getitem__(self, key):
        return self._data.get(key)
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def get(self, key, default=None):
        return self._data.get(key, default)


def example_flood_hazard_actual_data():
    """
    Example: Visualizing ACTUAL flood hazard data from BAFU.
    
    This demonstrates the correct approach: fetching and rendering
    real geospatial features, not just coverage areas.
    """
    print("=" * 70)
    print("Example: ACTUAL Flood Hazard Data Visualization")
    print("=" * 70)
    
    context = SimpleContext()
    
    # Step 1: List collections to find flood-related data
    print("\n1. Searching for flood-related collections...")
    result = BAFU_TOOLS["bafu_list_collections"](
        {"search_term": "flood", "limit": 5},
        context
    )
    print(result)
    
    # Step 2: Search for items in the overland flow collection
    print("\n2. Searching for items in overland flow hazard collection...")
    collection_id = "ch.bafu.gefaehrdungskarte-oberflaechenabfluss"
    result = BAFU_TOOLS["bafu_search_collection"](
        {"collection_id": collection_id, "limit": 3},
        context
    )
    print(result)
    
    # Step 3: Fetch ACTUAL data (not just bbox!)
    print("\n3. Fetching ACTUAL geospatial data...")
    result = BAFU_TOOLS["bafu_get_actual_data"](
        {"item_index": 0, "max_features": 100},
        context
    )
    print(result)
    
    # Step 4: Visualize the ACTUAL data on a map
    print("\n4. Creating map with ACTUAL flood hazard features...")
    
    # Check if we have data to visualize
    if context.get("bafu_geojson_data"):
        # Try to color by a risk-related field if available
        geojson = context.get("bafu_geojson_data", {})
        features = geojson.get("features", [])
        
        if features:
            props = features[0].get("properties", {})
            # Look for a good field to color by
            color_field = None
            for key in props.keys():
                if any(term in key.lower() for term in ['class', 'level', 'category', 'type', 'intensity']):
                    color_field = key
                    break
            
            result = BAFU_TOOLS["bafu_visualize_actual_data"](
                {
                    "output_file": "flood_hazard_actual_map.html",
                    "color_by": color_field,
                    "zoom": 10
                },
                context
            )
            print(result)
        else:
            print("No features available to visualize")
    else:
        # Fallback to WMS visualization
        print("Vector data not available, trying WMS visualization...")
        result = BAFU_TOOLS["bafu_visualize_wms"](
            {
                "layer_name": collection_id,
                "output_file": "flood_hazard_wms_map.html"
            },
            context
        )
        print(result)
    
    print("\n" + "=" * 70)
    print("Example complete!")
    print("=" * 70)


def example_risk_at_location():
    """
    Example: Analyzing environmental risk at a specific location.
    
    This demonstrates querying actual data for risk assessment.
    """
    print("\n" + "=" * 70)
    print("Example: Location-Based Risk Analysis")
    print("=" * 70)
    
    context = SimpleContext()
    
    # First, load some data
    print("\n1. Loading environmental data...")
    
    # Search for items
    result = BAFU_TOOLS["bafu_search_collection"](
        {"collection_id": "ch.bafu.gefaehrdungskarte-oberflaechenabfluss", "limit": 1},
        context
    )
    print("Search complete.")
    
    # Fetch actual data
    result = BAFU_TOOLS["bafu_get_actual_data"](
        {"item_index": 0},
        context
    )
    print("Data loaded.")
    
    # Now analyze risk at a location (example: Zurich area)
    print("\n2. Analyzing risk at Zurich coordinates...")
    result = BAFU_TOOLS["bafu_analyze_risk_at_location"](
        {
            "lat": 47.3769,
            "lon": 8.5417,
            "radius_m": 500
        },
        context
    )
    print(result)
    
    # Try another location (Bern)
    print("\n3. Analyzing risk at Bern coordinates...")
    result = BAFU_TOOLS["bafu_analyze_risk_at_location"](
        {
            "lat": 46.9480,
            "lon": 7.4474,
            "radius_m": 500
        },
        context
    )
    print(result)


def example_compare_coverage_vs_actual():
    """
    Example: Demonstrate the difference between coverage area and actual data.
    
    This clearly shows why getting actual data matters.
    """
    print("\n" + "=" * 70)
    print("Example: Coverage Area vs Actual Data Comparison")
    print("=" * 70)
    
    context = SimpleContext()
    
    # Search for items
    collection_id = "ch.bafu.gefaehrdungskarte-oberflaechenabfluss"
    BAFU_TOOLS["bafu_search_collection"](
        {"collection_id": collection_id, "limit": 1},
        context
    )
    
    features = context.get("bafu_search_results", [])
    if not features:
        print("No features found")
        return
    
    feature = features[0]
    
    print("\n📦 COVERAGE AREA (what original code showed):")
    print("-" * 50)
    bbox = feature.get("bbox", [])
    print(f"Bounding Box: {bbox}")
    print("This is just a rectangle showing WHERE data exists.")
    print("It tells you nothing about actual flood risk levels!")
    
    print("\n📊 ACTUAL DATA (what enhanced code shows):")
    print("-" * 50)
    
    # Fetch actual data
    result = BAFU_TOOLS["bafu_get_actual_data"](
        {"item_index": 0, "max_features": 50},
        context
    )
    print(result)
    
    print("\n💡 KEY INSIGHT:")
    print("-" * 50)
    print("""
    Coverage Area = "There is flood data somewhere in this box"
    Actual Data   = "Here are the specific flood zones with risk levels"
    
    For ESG risk assessment, you need the ACTUAL DATA to:
    - Identify specific areas at risk
    - Quantify hazard levels
    - Make informed investment decisions
    """)


def example_wms_visualization():
    """
    Example: Using WMS when vector data isn't easily available.
    
    Some BAFU datasets are better accessed via WMS tiles.
    """
    print("\n" + "=" * 70)
    print("Example: WMS Visualization (Alternative Approach)")
    print("=" * 70)
    
    context = SimpleContext()
    
    # List of interesting BAFU layers available via WMS
    layers_to_try = [
        ("ch.bafu.gefaehrdungskarte-oberflaechenabfluss", "Overland Flow Hazard"),
        ("ch.bafu.waldbrandgefahr", "Forest Fire Risk"),
        ("ch.bafu.bundesinventare-auen", "Floodplain Inventory"),
    ]
    
    print("\nCreating WMS maps for BAFU layers:")
    
    for layer_id, layer_name in layers_to_try:
        print(f"\n- Creating map for: {layer_name}")
        
        # Store collection in context
        context["bafu_collection_id"] = layer_id
        
        result = BAFU_TOOLS["bafu_visualize_wms"](
            {
                "layer_name": layer_id,
                "output_file": f"bafu_wms_{layer_id.split('.')[-1]}.html",
                "zoom": 8
            },
            context
        )
        print(f"  Result: Map saved")
    
    print("\n" + "=" * 70)
    print("WMS maps created!")
    print("=" * 70)


def main():
    """Run all enhanced examples."""
    print("\n" + "=" * 70)
    print("BAFU STAC Tools ENHANCED - Proper Data Visualization")
    print("Swiss Federal Office for the Environment")
    print("=" * 70)
    
    print("""
    
🎯 KEY IMPROVEMENTS IN ENHANCED VERSION:
    
1. bafu_get_actual_data - Fetches REAL geospatial features
   (flood zones, hazard areas, etc.)
   
2. bafu_visualize_actual_data - Renders actual features on map
   (not just a bounding box!)
   
3. bafu_visualize_wms - Uses official WMS tiles as alternative
   
4. bafu_analyze_risk_at_location - Queries data at coordinates
    
    """)
    
    # Run examples
    try:
        example_compare_coverage_vs_actual()
    except Exception as e:
        print(f"Example failed: {e}")
    
    try:
        example_wms_visualization()
    except Exception as e:
        print(f"WMS example failed: {e}")
    
    print("\n" + "=" * 70)
    print("All Examples Complete!")
    print("=" * 70)
    print("""
    
📁 Generated Files:
- flood_hazard_actual_map.html - Map with ACTUAL flood features
- bafu_wms_*.html - WMS tile visualizations

🔍 Next Steps:
1. Open the HTML files in your browser
2. Click on map features to see their attributes
3. Use bafu_analyze_risk_at_location for specific coordinates
4. Integrate with ESG risk assessment frameworks
    """)


if __name__ == "__main__":
    main()
