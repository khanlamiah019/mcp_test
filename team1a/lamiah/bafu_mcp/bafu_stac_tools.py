"""
BAFU STAC Tools Enhanced - Swiss Federal Office for the Environment

Enhanced tools for accessing and visualizing ACTUAL geospatial data from the 
Swiss Federal Office for the Environment's STAC catalog.

Key Improvements:
- Downloads and processes actual data assets (GeoJSON, GeoTIFF, etc.)
- Renders real features on maps (flood zones, hazard areas, etc.)
- Extracts meaningful metrics from the data

Author: Enhanced version
Date: November 2024
"""

from typing import Dict, Any, List, Optional, Tuple
import requests
import json
import os
from datetime import datetime
import tempfile


def bafu_list_collections_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    List available collections from BAFU STAC catalog.
    
    Args:
        args: Dictionary with optional:
            - limit: Maximum number of collections to display (default: 10)
            - search_term: Filter collections by keyword in title/description
        context: Server context for storing collection data
    
    Returns:
        String with formatted list of available collections
    """
    stac_url = "https://data.geo.admin.ch/api/stac/v1/collections"
    limit = args.get("limit", 10)
    search_term = args.get("search_term", "").lower()
    
    try:
        response = requests.get(stac_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        collections = data.get("collections", [])
        
        # Filter by search term if provided
        if search_term:
            collections = [c for c in collections 
                         if search_term in c.get("title", "").lower() 
                         or search_term in c.get("description", "").lower()
                         or search_term in c.get("id", "").lower()]
        
        # Store in context for later use
        context["bafu_collections"] = collections
        
        # Format output
        result = f"Found {len(collections)} BAFU collections"
        if search_term:
            result += f" matching '{search_term}'"
        result += ":\n\n"
        
        for i, collection in enumerate(collections[:limit]):
            coll_id = collection.get("id", "Unknown")
            title = collection.get("title", "No title")
            description = collection.get("description", "")[:150]
            
            result += f"{i+1}. {title}\n"
            result += f"   ID: {coll_id}\n"
            result += f"   Description: {description}...\n\n"
        
        if len(collections) > limit:
            result += f"\n(Showing {limit} of {len(collections)} collections. Increase 'limit' to see more.)"
        
        return result
        
    except Exception as e:
        return f"Error fetching collections: {str(e)}"


def bafu_search_collection_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Search for items within a specific BAFU collection.
    
    Args:
        args: Dictionary with:
            - collection_id: BAFU collection ID (e.g., "ch.bafu.gefaehrdungskarte-oberflaechenabfluss")
            - bbox: Optional bounding box [west, south, east, north] in WGS84
            - limit: Maximum number of items to return (default: 5)
        context: Server context for storing search results
    
    Returns:
        String with formatted search results including available data formats
    """
    collection_id = args.get("collection_id")
    if not collection_id:
        return "Error: 'collection_id' parameter is required"
    
    limit = args.get("limit", 5)
    bbox = args.get("bbox")
    
    # STAC API search endpoint
    search_url = f"https://data.geo.admin.ch/api/stac/v1/collections/{collection_id}/items"
    
    try:
        params = {"limit": limit}
        if bbox:
            params["bbox"] = ",".join(map(str, bbox))
        
        response = requests.get(search_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        features = data.get("features", [])
        
        # Store in context for later use
        context["bafu_search_results"] = features
        context["bafu_collection_id"] = collection_id
        
        if not features:
            return f"No items found in collection '{collection_id}'"
        
        result = f"Found {len(features)} items in collection '{collection_id}':\n\n"
        
        for i, feature in enumerate(features):
            feature_id = feature.get("id", "Unknown")
            properties = feature.get("properties", {})
            
            result += f"{i+1}. Item ID: {feature_id}\n"
            
            # Show relevant properties
            if "datetime" in properties:
                result += f"   Date: {properties['datetime']}\n"
            if "title" in properties:
                result += f"   Title: {properties['title']}\n"
            
            # Show available assets with their types
            assets = feature.get("assets", {})
            if assets:
                result += f"   Available Assets ({len(assets)}):\n"
                for asset_key, asset_info in assets.items():
                    media_type = asset_info.get("type", "unknown")
                    title = asset_info.get("title", asset_key)
                    href = asset_info.get("href", "")
                    
                    # Determine if it's visualizable
                    visualizable = ""
                    if any(ext in href.lower() for ext in ['.geojson', '.json', '.gpkg', '.shp']):
                        visualizable = " [VECTOR - Can visualize!]"
                    elif any(ext in href.lower() for ext in ['.tif', '.tiff', '.png', '.jpg']):
                        visualizable = " [RASTER]"
                    
                    result += f"      - {asset_key}: {title} ({media_type}){visualizable}\n"
            
            result += "\n"
        
        result += "\n💡 To visualize actual data, use bafu_visualize_actual_data with an asset that contains vector data (.geojson, .json, .gpkg)"
        
        return result
        
    except Exception as e:
        return f"Error searching collection: {str(e)}"


def bafu_get_collection_info_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Get detailed information about a specific BAFU collection.
    """
    collection_id = args.get("collection_id")
    if not collection_id:
        return "Error: 'collection_id' parameter is required"
    
    url = f"https://data.geo.admin.ch/api/stac/v1/collections/{collection_id}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        collection = response.json()
        
        title = collection.get("title", "No title")
        description = collection.get("description", "No description")
        license_info = collection.get("license", "Unknown")
        
        # Get extent information
        extent = collection.get("extent", {})
        spatial = extent.get("spatial", {}).get("bbox", [[]])
        temporal = extent.get("temporal", {}).get("interval", [[]])
        
        # Get providers
        providers = collection.get("providers", [])
        provider_names = [p.get("name", "Unknown") for p in providers]
        
        result = f"Collection: {title}\n"
        result += f"ID: {collection_id}\n\n"
        result += f"Description:\n{description}\n\n"
        result += f"License: {license_info}\n"
        result += f"Providers: {', '.join(provider_names)}\n\n"
        
        if spatial and spatial[0]:
            bbox = spatial[0]
            result += f"Spatial Extent (bbox): {bbox}\n"
        
        if temporal and temporal[0]:
            start = temporal[0][0] if temporal[0][0] else "Unknown"
            end = temporal[0][1] if temporal[0][1] else "Present"
            result += f"Temporal Extent: {start} to {end}\n"
        
        return result
        
    except Exception as e:
        return f"Error fetching collection info: {str(e)}"


def _fetch_geojson_data(url: str, max_features: int = 1000) -> Optional[Dict]:
    """
    Fetch GeoJSON data from a URL.
    
    Args:
        url: URL to the GeoJSON file
        max_features: Maximum number of features to load (for large files)
    
    Returns:
        GeoJSON dictionary or None if failed
    """
    try:
        response = requests.get(url, timeout=60, stream=True)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        
        # Try to parse as JSON
        data = response.json()
        
        # Limit features if too many
        if "features" in data and len(data["features"]) > max_features:
            print(f"Warning: Limiting to {max_features} features (total: {len(data['features'])})")
            data["features"] = data["features"][:max_features]
        
        return data
        
    except Exception as e:
        print(f"Error fetching GeoJSON: {e}")
        return None


def bafu_identify_features_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Identify features at a specific location using the GeoAdmin REST API.
    
    This is the RECOMMENDED way to get actual geospatial features from BAFU.
    It uses the GeoAdmin identify service which returns real features in GeoJSON format.
    
    Args:
        args: Dictionary with:
            - layer_id: BAFU layer ID (e.g., "ch.bafu.gefaehrdungskarte-oberflaechenabfluss")
            - geometry: Either [x, y] point in LV95 coords, or bbox [minx, miny, maxx, maxy]
            - geometry_type: "point" or "bbox" (default: "bbox")
            - tolerance: Tolerance in pixels for point queries (default: 10)
        context: Server context for storing results
    
    Returns:
        String with identified features and their attributes
    """
    layer_id = args.get("layer_id")
    if not layer_id:
        # Use collection from context
        layer_id = context.get("bafu_collection_id")
    
    if not layer_id:
        return "Error: 'layer_id' parameter required or run bafu_search_collection first"
    
    geometry = args.get("geometry")
    geometry_type = args.get("geometry_type", "bbox")
    tolerance = args.get("tolerance", 10)
    
    # Default to a Swiss bbox if none provided (Zurich area)
    if not geometry:
        # Default: Zurich area in LV95 coordinates
        geometry = [2683000, 1247000, 2685000, 1249000]
        geometry_type = "bbox"
    
    # Build the identify request URL
    base_url = "https://api3.geo.admin.ch/rest/services/api/MapServer/identify"
    
    if geometry_type == "point" and len(geometry) == 2:
        params = {
            "geometry": f"{geometry[0]},{geometry[1]}",
            "geometryType": "esriGeometryPoint",
            "layers": f"all:{layer_id}",
            "imageDisplay": "500,500,96",
            "mapExtent": f"{geometry[0]-5000},{geometry[1]-5000},{geometry[0]+5000},{geometry[1]+5000}",
            "tolerance": tolerance,
            "returnGeometry": "true",
            "geometryFormat": "geojson",
            "sr": "2056"  # LV95
        }
    elif geometry_type == "bbox" and len(geometry) == 4:
        params = {
            "geometry": f"{geometry[0]},{geometry[1]},{geometry[2]},{geometry[3]}",
            "geometryType": "esriGeometryEnvelope",
            "layers": f"all:{layer_id}",
            "imageDisplay": "500,500,96",
            "mapExtent": f"{geometry[0]},{geometry[1]},{geometry[2]},{geometry[3]}",
            "tolerance": tolerance,
            "returnGeometry": "true",
            "geometryFormat": "geojson",
            "sr": "2056"  # LV95
        }
    else:
        return f"Error: Invalid geometry. Use [x,y] for point or [minx,miny,maxx,maxy] for bbox"
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        
        if not results:
            return f"""No features found at the specified location.

Layer: {layer_id}
Geometry: {geometry}

Tips:
- Try a different location (coordinates must be in LV95/EPSG:2056)
- Try a larger bounding box
- Verify the layer contains data for this area"""
        
        # Convert to GeoJSON FeatureCollection for compatibility
        geojson_features = []
        for r in results:
            feature = {
                "type": "Feature",
                "id": r.get("id"),
                "geometry": r.get("geometry"),
                "properties": r.get("properties", {})
            }
            # Also add attributes to properties
            if "attributes" in r:
                feature["properties"].update(r["attributes"])
            geojson_features.append(feature)
        
        geojson_data = {
            "type": "FeatureCollection",
            "features": geojson_features
        }
        
        # Store in context
        context["bafu_geojson_data"] = geojson_data
        context["bafu_data_source"] = "GeoAdmin Identify API"
        context["bafu_collection_id"] = layer_id
        
        # Format output
        result = f"✅ Found {len(results)} features!\n\n"
        result += f"Layer: {layer_id}\n"
        result += f"Query geometry: {geometry}\n\n"
        
        for i, r in enumerate(results[:5]):
            result += f"Feature {i+1}: {r.get('id', 'Unknown')}\n"
            attrs = r.get("attributes", r.get("properties", {}))
            for key, value in list(attrs.items())[:8]:
                result += f"  {key}: {value}\n"
            result += "\n"
        
        if len(results) > 5:
            result += f"... and {len(results) - 5} more features\n"
        
        result += "\n💡 Use bafu_visualize_actual_data to create a map with these features!"
        
        return result
        
    except Exception as e:
        return f"Error identifying features: {str(e)}"


def bafu_query_by_coordinates_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Query BAFU environmental data using WGS84 coordinates (lat/lon).
    
    This is a convenience function that converts lat/lon to Swiss LV95 coordinates
    and queries the GeoAdmin API.
    
    Args:
        args: Dictionary with:
            - lat: Latitude in WGS84 (e.g., 47.3769 for Zurich)
            - lon: Longitude in WGS84 (e.g., 8.5417 for Zurich)
            - layer_id: BAFU layer ID (optional, uses context if not provided)
            - radius_m: Search radius in meters (default: 1000)
        context: Server context
    
    Returns:
        String with features found at the location
    """
    lat = args.get("lat")
    lon = args.get("lon")
    layer_id = args.get("layer_id") or context.get("bafu_collection_id")
    radius_m = args.get("radius_m", 1000)
    
    if lat is None or lon is None:
        return "Error: Both 'lat' and 'lon' parameters are required"
    
    if not layer_id:
        return "Error: 'layer_id' required or run bafu_search_collection first"
    
    # Approximate conversion from WGS84 to LV95
    # Using simplified formula (accurate to ~100m for Switzerland)
    # For production, use proper proj4 transformation
    y = lat
    x = lon
    
    # Approximate LV95 conversion (good enough for querying)
    # These formulas work reasonably well within Switzerland
    phi = (y * 3600 - 169028.66) / 10000
    lam = (x * 3600 - 26782.5) / 10000
    
    E = 2600072.37 + 211455.93 * lam \
        - 10938.51 * lam * phi \
        - 0.36 * lam * phi * phi \
        - 44.54 * lam * lam * lam
    
    N = 1200147.07 + 308807.95 * phi \
        + 3745.25 * lam * lam \
        + 76.63 * phi * phi \
        - 194.56 * lam * lam * phi \
        + 119.79 * phi * phi * phi
    
    # Create bounding box around the point
    half_radius = radius_m / 2
    bbox = [E - half_radius, N - half_radius, E + half_radius, N + half_radius]
    
    result = f"📍 Querying at: {lat}, {lon} (WGS84)\n"
    result += f"   Converted to LV95: {E:.0f}, {N:.0f}\n"
    result += f"   Search radius: {radius_m}m\n\n"
    
    # Call the identify function
    identify_result = bafu_identify_features_tool(
        {
            "layer_id": layer_id,
            "geometry": bbox,
            "geometry_type": "bbox"
        },
        context
    )
    
    return result + identify_result


def _get_asset_url_for_visualization(feature: Dict, preferred_formats: List[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Get the best asset URL for visualization from a STAC feature.
    
    Args:
        feature: STAC feature dictionary
        preferred_formats: List of preferred file extensions
    
    Returns:
        Tuple of (asset_url, asset_key) or (None, None)
    """
    if preferred_formats is None:
        preferred_formats = ['.geojson', '.json', '.gpkg', '.shp.zip', '.kml']
    
    assets = feature.get("assets", {})
    
    # First pass: look for preferred formats
    for fmt in preferred_formats:
        for asset_key, asset_info in assets.items():
            href = asset_info.get("href", "")
            if fmt in href.lower():
                return href, asset_key
    
    # Second pass: look for any JSON-like content
    for asset_key, asset_info in assets.items():
        media_type = asset_info.get("type", "")
        if "json" in media_type.lower() or "geojson" in media_type.lower():
            return asset_info.get("href"), asset_key
    
    return None, None


def bafu_get_actual_data_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Fetch and analyze actual data from a BAFU STAC item.
    
    This retrieves the real geospatial features (flood zones, hazard areas, etc.)
    not just the bounding box coverage area.
    
    Args:
        args: Dictionary with:
            - item_index: Index of item from search results (default: 0)
            - asset_key: Specific asset to fetch (optional, auto-detects if not provided)
            - max_features: Maximum features to retrieve (default: 100)
        context: Server context containing search results
    
    Returns:
        String with data analysis and sample features
    """
    item_index = args.get("item_index", 0)
    asset_key = args.get("asset_key")
    max_features = args.get("max_features", 100)
    
    # Get search results from context
    features = context.get("bafu_search_results", [])
    collection_id = context.get("bafu_collection_id", "Unknown")
    
    if not features:
        return "Error: No search results found. Please run bafu_search_collection first."
    
    if item_index >= len(features):
        return f"Error: Item index {item_index} out of range. Only {len(features)} items available."
    
    feature = features[item_index]
    
    # Find the best asset for data retrieval
    if asset_key:
        assets = feature.get("assets", {})
        if asset_key not in assets:
            return f"Error: Asset '{asset_key}' not found. Available: {list(assets.keys())}"
        asset_url = assets[asset_key].get("href")
    else:
        asset_url, asset_key = _get_asset_url_for_visualization(feature)
    
    if not asset_url:
        # List what's available
        assets = feature.get("assets", {})
        asset_list = "\n".join([f"  - {k}: {v.get('href', 'no url')}" for k, v in assets.items()])
        return f"""No directly visualizable data format found.

Available assets:
{asset_list}

Many BAFU datasets use specialized formats (GeoPackage, Raster TIFFs).
For these, use bafu_download_asset to download, then open in GIS software.

Alternatively, try the WMS visualization with bafu_visualize_wms."""
    
    result = f"📊 Fetching actual data from: {asset_key}\n"
    result += f"URL: {asset_url}\n\n"
    
    # Fetch the data
    geojson_data = _fetch_geojson_data(asset_url, max_features)
    
    if not geojson_data:
        return result + "Error: Could not fetch or parse the data file."
    
    # Store for visualization
    context["bafu_geojson_data"] = geojson_data
    context["bafu_data_source"] = asset_url
    
    # Analyze the data
    if "features" in geojson_data:
        num_features = len(geojson_data["features"])
        result += f"✅ Successfully retrieved {num_features} features!\n\n"
        
        # Analyze geometry types
        geom_types = {}
        for f in geojson_data["features"]:
            geom = f.get("geometry", {})
            gtype = geom.get("type", "Unknown")
            geom_types[gtype] = geom_types.get(gtype, 0) + 1
        
        result += "Geometry Types:\n"
        for gtype, count in geom_types.items():
            result += f"  - {gtype}: {count}\n"
        
        # Analyze properties (attributes)
        if geojson_data["features"]:
            sample_props = geojson_data["features"][0].get("properties", {})
            result += f"\nAvailable Attributes ({len(sample_props)}):\n"
            for key, value in list(sample_props.items())[:15]:
                result += f"  - {key}: {type(value).__name__} (e.g., {str(value)[:50]})\n"
            
            if len(sample_props) > 15:
                result += f"  ... and {len(sample_props) - 15} more attributes\n"
        
        # Look for hazard/risk related fields
        risk_fields = []
        for key in sample_props.keys():
            key_lower = key.lower()
            if any(term in key_lower for term in ['risk', 'hazard', 'danger', 'level', 'class', 'category', 'intensity']):
                risk_fields.append(key)
        
        if risk_fields:
            result += f"\n🎯 Potential Risk/Hazard Fields Found:\n"
            for field in risk_fields:
                # Get unique values
                values = set()
                for f in geojson_data["features"][:100]:
                    val = f.get("properties", {}).get(field)
                    if val is not None:
                        values.add(str(val))
                result += f"  - {field}: {list(values)[:10]}\n"
        
        result += "\n💡 Use bafu_visualize_actual_data to create a map with this real data!"
    else:
        result += "Data format not recognized as GeoJSON FeatureCollection."
    
    return result


def bafu_visualize_actual_data_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Create an interactive map with ACTUAL geospatial features from BAFU.
    
    This renders the real flood zones, hazard areas, etc. - not just a bounding box.
    
    Args:
        args: Dictionary with:
            - output_file: HTML file to save map (default: "bafu_actual_data_map.html")
            - color_by: Property name to color features by (optional)
            - zoom: Initial zoom level (default: 10)
            - max_features: Maximum features to display (default: 500)
        context: Server context containing fetched geojson data
    
    Returns:
        String with map creation status
    """
    try:
        import folium
        from folium.plugins import MarkerCluster
    except ImportError:
        return "Error: folium library not installed. Run: pip install folium"
    
    output_file = args.get("output_file", "bafu_actual_data_map.html")
    color_by = args.get("color_by")
    zoom = args.get("zoom", 10)
    max_features = args.get("max_features", 500)
    
    # Get the actual data from context
    geojson_data = context.get("bafu_geojson_data")
    collection_id = context.get("bafu_collection_id", "Unknown")
    data_source = context.get("bafu_data_source", "Unknown")
    
    if not geojson_data:
        return """Error: No actual data loaded. Please run these steps first:
1. bafu_search_collection - to find items
2. bafu_get_actual_data - to fetch the real geospatial data
3. Then run bafu_visualize_actual_data"""
    
    features = geojson_data.get("features", [])
    if not features:
        return "Error: No features found in the loaded data."
    
    # Limit features for performance
    if len(features) > max_features:
        features = features[:max_features]
        limited = True
    else:
        limited = False
    
    # Calculate center from actual features
    all_coords = []
    for f in features[:100]:  # Sample for center calculation
        geom = f.get("geometry", {})
        coords = _extract_coords(geom)
        all_coords.extend(coords)
    
    if all_coords:
        avg_lat = sum(c[1] for c in all_coords) / len(all_coords)
        avg_lon = sum(c[0] for c in all_coords) / len(all_coords)
        center = [avg_lat, avg_lon]
    else:
        center = [46.8182, 8.2275]  # Switzerland default
    
    # Create map
    m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")
    
    # Define color scheme
    if color_by:
        # Get unique values for the color field
        unique_values = list(set(
            str(f.get("properties", {}).get(color_by, "Unknown")) 
            for f in features
        ))
        colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', 
                  '#ffff33', '#a65628', '#f781bf', '#999999']
        color_map = {val: colors[i % len(colors)] for i, val in enumerate(unique_values)}
    else:
        color_map = None
    
    # Add features to map
    feature_group = folium.FeatureGroup(name="BAFU Data")
    
    for i, feature in enumerate(features):
        geom = feature.get("geometry", {})
        props = feature.get("properties", {})
        geom_type = geom.get("type", "")
        
        # Determine color
        if color_map and color_by:
            color = color_map.get(str(props.get(color_by, "Unknown")), '#3388ff')
        else:
            color = '#e41a1c'  # Red for hazard data
        
        # Create popup content
        popup_html = "<div style='max-height:200px; overflow:auto;'>"
        popup_html += f"<b>Feature {i+1}</b><br>"
        for key, value in list(props.items())[:10]:
            popup_html += f"<b>{key}:</b> {value}<br>"
        popup_html += "</div>"
        
        try:
            if geom_type == "Point":
                coords = geom.get("coordinates", [])
                if len(coords) >= 2:
                    folium.CircleMarker(
                        location=[coords[1], coords[0]],
                        radius=6,
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.7,
                        popup=folium.Popup(popup_html, max_width=300)
                    ).add_to(feature_group)
                    
            elif geom_type in ["LineString", "MultiLineString"]:
                folium.GeoJson(
                    feature,
                    style_function=lambda x, c=color: {
                        'color': c,
                        'weight': 3,
                        'opacity': 0.8
                    },
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(feature_group)
                
            elif geom_type in ["Polygon", "MultiPolygon"]:
                folium.GeoJson(
                    feature,
                    style_function=lambda x, c=color: {
                        'fillColor': c,
                        'color': '#000000',
                        'weight': 1,
                        'fillOpacity': 0.5
                    },
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(feature_group)
        except Exception as e:
            continue  # Skip problematic features
    
    feature_group.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add legend if color_by is specified
    if color_map:
        legend_html = f'''
        <div style="position: fixed; bottom: 50px; left: 50px; 
                    background-color: white; padding: 10px; 
                    border: 2px solid grey; z-index:9999; font-size:12px;">
        <b>Legend: {color_by}</b><br>
        '''
        for val, col in list(color_map.items())[:8]:
            legend_html += f'<i style="background:{col};width:12px;height:12px;display:inline-block;margin-right:5px;"></i>{val}<br>'
        legend_html += '</div>'
        m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add title
    title_html = f'''
    <div style="position: fixed; top: 10px; left: 50px; width: 400px; 
                background-color: white; border:3px solid #e41a1c; z-index:9999; 
                padding: 15px; border-radius: 5px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
    <b style="font-size:16px;">🗺️ BAFU Actual Environmental Data</b><br>
    <hr style="margin: 10px 0;">
    <b>Collection:</b> {collection_id}<br>
    <b>Features Displayed:</b> {len(features)}{' (limited)' if limited else ''}<br>
    {f'<b>Colored by:</b> {color_by}<br>' if color_by else ''}
    <br>
    <i style="font-size:11px; color:#666;">
    ✅ This map shows ACTUAL geospatial features from the dataset!<br>
    Click on features to see their attributes.
    </i>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Save map
    m.save(output_file)
    
    return f"""✅ Map with ACTUAL DATA created successfully!

📊 What this map shows:
- {len(features)} real geospatial features (not just a bounding box!)
- Actual flood zones / hazard areas / environmental data
- Click on any feature to see its attributes

{f'🎨 Features colored by: {color_by}' if color_by else '💡 Tip: Use color_by parameter to color features by an attribute'}

📁 File: {output_file}
🌐 Open this file in your browser to view the interactive map!
"""


def _extract_coords(geometry: Dict) -> List[Tuple[float, float]]:
    """Extract coordinate pairs from a GeoJSON geometry."""
    coords = []
    geom_type = geometry.get("type", "")
    
    if geom_type == "Point":
        c = geometry.get("coordinates", [])
        if len(c) >= 2:
            coords.append((c[0], c[1]))
    elif geom_type == "LineString":
        for c in geometry.get("coordinates", []):
            if len(c) >= 2:
                coords.append((c[0], c[1]))
    elif geom_type == "Polygon":
        for ring in geometry.get("coordinates", []):
            for c in ring:
                if len(c) >= 2:
                    coords.append((c[0], c[1]))
    elif geom_type == "MultiPolygon":
        for poly in geometry.get("coordinates", []):
            for ring in poly:
                for c in ring:
                    if len(c) >= 2:
                        coords.append((c[0], c[1]))
    elif geom_type == "MultiLineString":
        for line in geometry.get("coordinates", []):
            for c in line:
                if len(c) >= 2:
                    coords.append((c[0], c[1]))
    elif geom_type == "MultiPoint":
        for c in geometry.get("coordinates", []):
            if len(c) >= 2:
                coords.append((c[0], c[1]))
    
    return coords


def bafu_visualize_wms_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Create a map using WMS (Web Map Service) layers from geo.admin.ch.
    
    This is an alternative visualization that uses pre-rendered map tiles
    for datasets that don't have easily downloadable vector data.
    
    Args:
        args: Dictionary with:
            - layer_name: WMS layer name (usually same as collection_id)
            - output_file: HTML file to save map (default: "bafu_wms_map.html")
            - zoom: Initial zoom level (default: 8)
            - center: [lat, lon] center point (default: Switzerland center)
        context: Server context
    
    Returns:
        String with map creation status
    """
    try:
        import folium
    except ImportError:
        return "Error: folium library not installed. Run: pip install folium"
    
    layer_name = args.get("layer_name")
    output_file = args.get("output_file", "bafu_wms_map.html")
    zoom = args.get("zoom", 8)
    center = args.get("center", [46.8182, 8.2275])
    
    # Use collection_id from context if no layer specified
    if not layer_name:
        layer_name = context.get("bafu_collection_id")
    
    if not layer_name:
        return "Error: No layer_name provided and no collection in context. Please specify layer_name or run bafu_search_collection first."
    
    # Create map
    m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")
    
    # Add WMS layer from geo.admin.ch
    wms_url = "https://wms.geo.admin.ch/"
    
    folium.WmsTileLayer(
        url=wms_url,
        name=layer_name,
        layers=layer_name,
        fmt='image/png',
        transparent=True,
        version='1.3.0',
        attr='© swisstopo',
        overlay=True,
        control=True
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add title
    title_html = f'''
    <div style="position: fixed; top: 10px; left: 50px; width: 400px; 
                background-color: white; border:3px solid #377eb8; z-index:9999; 
                padding: 15px; border-radius: 5px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
    <b style="font-size:16px;">🗺️ BAFU WMS Layer Visualization</b><br>
    <hr style="margin: 10px 0;">
    <b>Layer:</b> {layer_name}<br>
    <br>
    <i style="font-size:11px; color:#666;">
    This map uses WMS tiles from geo.admin.ch<br>
    Toggle the layer using the control in the top right.
    </i>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Save map
    m.save(output_file)
    
    return f"""✅ WMS Map created successfully!

📊 What this map shows:
- Official BAFU map layer rendered via WMS
- Layer: {layer_name}

📁 File: {output_file}
🌐 Open this file in your browser to view the map!

💡 Note: WMS shows pre-rendered tiles. For feature-level data analysis,
use bafu_get_actual_data + bafu_visualize_actual_data instead.
"""


def bafu_download_asset_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Download an asset from a BAFU STAC item.
    
    Args:
        args: Dictionary with:
            - item_index: Index of item from search results (default: 0)
            - asset_key: Key of asset to download (e.g., "data", "metadata")
            - output_dir: Directory to save downloaded file (default: "downloads/bafu")
        context: Server context containing search results
    
    Returns:
        String with download status and file path
    """
    item_index = args.get("item_index", 0)
    asset_key = args.get("asset_key")
    output_dir = args.get("output_dir", "downloads/bafu")
    
    # Get search results from context
    features = context.get("bafu_search_results", [])
    if not features:
        return "Error: No search results found. Please run bafu_search_collection first."
    
    if item_index >= len(features):
        return f"Error: Item index {item_index} out of range. Only {len(features)} items available."
    
    feature = features[item_index]
    assets = feature.get("assets", {})
    
    # If no asset_key specified, list available and pick first
    if not asset_key:
        if not assets:
            return "Error: No assets found in this item."
        asset_key = list(assets.keys())[0]
    
    if asset_key not in assets:
        available = ", ".join(assets.keys())
        return f"Error: Asset '{asset_key}' not found. Available assets: {available}"
    
    asset = assets[asset_key]
    asset_url = asset.get("href")
    
    if not asset_url:
        return f"Error: No URL found for asset '{asset_key}'"
    
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        feature_id = feature.get("id", "unknown")
        file_ext = asset_url.split(".")[-1].split("?")[0] if "." in asset_url else "dat"
        filename = f"{feature_id}_{asset_key}.{file_ext}"
        filepath = os.path.join(output_dir, filename)
        
        # Download file
        print(f"Downloading {asset_url}...")
        response = requests.get(asset_url, timeout=120, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(filepath)
        size_mb = file_size / (1024 * 1024)
        
        return f"""✅ Downloaded successfully!
File: {filepath}
Size: {size_mb:.2f} MB

Next steps:
- For GeoJSON/JSON: Use bafu_get_actual_data to analyze
- For GeoPackage/Shapefile: Open in QGIS or ArcGIS
- For GeoTIFF: Process with rasterio or GDAL
"""
        
    except Exception as e:
        return f"Error downloading asset: {str(e)}"


def bafu_analyze_risk_at_location_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Analyze environmental risk at a specific location using loaded BAFU data.
    
    Args:
        args: Dictionary with:
            - lat: Latitude (WGS84)
            - lon: Longitude (WGS84)
            - radius_m: Search radius in meters (default: 100)
        context: Server context containing loaded geojson data
    
    Returns:
        String with risk analysis for the location
    """
    lat = args.get("lat")
    lon = args.get("lon")
    radius_m = args.get("radius_m", 100)
    
    if lat is None or lon is None:
        return "Error: Both 'lat' and 'lon' parameters are required"
    
    geojson_data = context.get("bafu_geojson_data")
    collection_id = context.get("bafu_collection_id", "Unknown")
    
    if not geojson_data:
        return """Error: No data loaded. Please run:
1. bafu_search_collection
2. bafu_get_actual_data
Then try this function again."""
    
    features = geojson_data.get("features", [])
    
    # Simple point-in-polygon / nearby check
    # Note: This is a simplified check - for production use shapely
    nearby_features = []
    
    for feature in features:
        geom = feature.get("geometry", {})
        coords = _extract_coords(geom)
        
        for coord in coords:
            # Simple distance check (approximate for small distances)
            dist_deg = ((coord[0] - lon)**2 + (coord[1] - lat)**2)**0.5
            dist_m_approx = dist_deg * 111000  # Rough conversion
            
            if dist_m_approx < radius_m:
                nearby_features.append(feature)
                break
    
    result = f"📍 Risk Analysis at Location ({lat}, {lon})\n"
    result += f"Collection: {collection_id}\n"
    result += f"Search radius: {radius_m}m\n\n"
    
    if not nearby_features:
        result += "✅ No hazard features found within the search radius.\n"
        result += "\nNote: This doesn't guarantee safety - try a larger radius or check other datasets."
    else:
        result += f"⚠️ Found {len(nearby_features)} features within {radius_m}m:\n\n"
        
        for i, feature in enumerate(nearby_features[:5]):
            props = feature.get("properties", {})
            result += f"Feature {i+1}:\n"
            for key, value in list(props.items())[:8]:
                result += f"  {key}: {value}\n"
            result += "\n"
        
        if len(nearby_features) > 5:
            result += f"... and {len(nearby_features) - 5} more features\n"
    
    return result


# Tool registration dictionary
BAFU_TOOLS = {
    "bafu_list_collections": bafu_list_collections_tool,
    "bafu_search_collection": bafu_search_collection_tool,
    "bafu_get_collection_info": bafu_get_collection_info_tool,
    "bafu_get_actual_data": bafu_get_actual_data_tool,
    "bafu_identify_features": bafu_identify_features_tool,  # NEW: Best way to get actual data
    "bafu_query_by_coordinates": bafu_query_by_coordinates_tool,  # NEW: Query with lat/lon
    "bafu_visualize_actual_data": bafu_visualize_actual_data_tool,
    "bafu_visualize_wms": bafu_visualize_wms_tool,
    "bafu_download_asset": bafu_download_asset_tool,
    "bafu_analyze_risk_at_location": bafu_analyze_risk_at_location_tool,
}


# Example usage
if __name__ == "__main__":
    print("BAFU STAC Tools Enhanced")
    print("=" * 50)
    print("\nTools for accessing ACTUAL geospatial data:")
    print("")
    print("PRIMARY METHODS (Recommended):")
    print("1. bafu_identify_features - Get actual features via GeoAdmin API")
    print("   → Best for: Getting real flood zones, hazard polygons, etc.")
    print("   → Input: Layer ID + bounding box in LV95 coordinates")
    print("")
    print("2. bafu_query_by_coordinates - Query with lat/lon coordinates")
    print("   → Best for: Quick risk check at specific WGS84 location")
    print("   → Input: Lat, Lon, Layer ID")
    print("")
    print("SECONDARY METHODS:")
    print("3. bafu_get_actual_data - Try to fetch data from STAC assets")
    print("4. bafu_visualize_wms - Use WMS tiles for visualization")
    print("5. bafu_visualize_actual_data - Map real features from context")
    print("6. bafu_analyze_risk_at_location - Check risk at coordinates")
    print("")
    print("WORKFLOW EXAMPLE:")
    print("  1. bafu_list_collections(search_term='flood')")
    print("  2. bafu_search_collection(collection_id='ch.bafu.xxx')")
    print("  3. bafu_query_by_coordinates(lat=47.37, lon=8.54, layer_id='ch.bafu.xxx')")
    print("  4. bafu_visualize_actual_data(output_file='map.html')")
