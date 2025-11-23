"""
GEO BON STAC Tools - IMPROVED VERSION
Retrieves and processes ACTUAL DATA from STAC assets, not just coverage areas.

Key Improvements:
1. Actually downloads and processes GeoTIFF raster data
2. Calculates real statistics (forest loss hectares, percentages, etc.)
3. Supports Cloud-Optimized GeoTIFFs (COG) for efficient partial reads
4. Provides actual data values, not just bounding boxes

Author: Lamiah Khan (Improved)
Date: November 2024
"""

from typing import Dict, Any, Optional, Tuple, List
import requests
import json
import os
from datetime import datetime
import tempfile


def geobon_list_collections_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    List available collections from GEO BON STAC catalog.
    """
    stac_url = "https://stac.geobon.org/collections"
    limit = args.get("limit", 10)
    search_term = args.get("search_term", "").lower()
    
    try:
        response = requests.get(stac_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        collections = data.get("collections", [])
        
        if search_term:
            collections = [c for c in collections 
                         if search_term in c.get("title", "").lower() 
                         or search_term in c.get("description", "").lower()]
        
        context["geobon_collections"] = collections
        
        result = f"Found {len(collections)} GEO BON collections"
        if search_term:
            result += f" matching '{search_term}'"
        result += ":\n\n"
        
        for i, collection in enumerate(collections[:limit]):
            coll_id = collection.get("id", "Unknown")
            title = collection.get("title", "No title")
            description = collection.get("description", "")[:200]
            
            result += f"{i+1}. {title}\n"
            result += f"   ID: {coll_id}\n"
            result += f"   Description: {description}...\n\n"
        
        if len(collections) > limit:
            result += f"\n(Showing {limit} of {len(collections)} collections)"
        
        return result
        
    except Exception as e:
        return f"Error fetching collections: {str(e)}"


def geobon_get_collection_info_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Get detailed information about a specific GEO BON collection.
    """
    collection_id = args.get("collection_id")
    if not collection_id:
        return "Error: 'collection_id' parameter is required"
    
    url = f"https://stac.geobon.org/collections/{collection_id}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        collection = response.json()
        
        title = collection.get("title", "No title")
        description = collection.get("description", "No description")
        license_info = collection.get("license", "Unknown")
        
        extent = collection.get("extent", {})
        spatial = extent.get("spatial", {}).get("bbox", [[]])
        temporal = extent.get("temporal", {}).get("interval", [[]])
        
        result = f"🌍 Collection: {title}\n"
        result += f"ID: {collection_id}\n\n"
        result += f"Description:\n{description}\n\n"
        result += f"License: {license_info}\n\n"
        
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


def geobon_search_collection_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Search for items within a specific GEO BON collection.
    Now includes detailed asset information for data access.
    """
    collection_id = args.get("collection_id")
    if not collection_id:
        return "Error: 'collection_id' parameter is required"
    
    limit = args.get("limit", 10)
    bbox = args.get("bbox")
    
    search_url = f"https://stac.geobon.org/collections/{collection_id}/items"
    
    try:
        params = {"limit": limit}
        if bbox:
            params["bbox"] = ",".join(map(str, bbox))
        
        response = requests.get(search_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        features = data.get("features", [])
        
        # Store in context for later use
        context["geobon_search_results"] = features
        context["geobon_collection_id"] = collection_id
        
        if not features:
            return f"No items found in collection '{collection_id}'"
        
        result = f"🔍 Found {len(features)} items in collection '{collection_id}':\n\n"
        
        for i, feature in enumerate(features):
            feature_id = feature.get("id", "Unknown")
            properties = feature.get("properties", {})
            bbox = feature.get("bbox", [])
            
            result += f"{i+1}. Item ID: {feature_id}\n"
            
            if "datetime" in properties:
                result += f"   Date: {properties['datetime']}\n"
            
            if bbox:
                result += f"   Bounding Box: [{bbox[0]:.2f}, {bbox[1]:.2f}, {bbox[2]:.2f}, {bbox[3]:.2f}]\n"
            
            # Detailed asset information - THIS IS KEY FOR ACCESSING ACTUAL DATA
            assets = feature.get("assets", {})
            if assets:
                result += f"   📦 Data Assets:\n"
                for asset_key, asset_info in assets.items():
                    asset_type = asset_info.get("type", "unknown")
                    href = asset_info.get("href", "")
                    title = asset_info.get("title", asset_key)
                    
                    # Check if it's a Cloud-Optimized GeoTIFF (COG)
                    is_cog = "cloud-optimized" in asset_type.lower() or href.endswith(".tif")
                    cog_note = " [COG - supports partial reads]" if is_cog else ""
                    
                    result += f"      • {asset_key}: {title} ({asset_type}){cog_note}\n"
                    result += f"        URL: {href[:80]}...\n" if len(href) > 80 else f"        URL: {href}\n"
            
            result += "\n"
        
        result += "\n💡 Use 'geobon_get_raster_data' to retrieve and analyze actual data values!"
        
        return result
        
    except Exception as e:
        return f"Error searching collection: {str(e)}"


def geobon_get_asset_info_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Get detailed information about assets in a STAC item including
    the actual data URLs needed to retrieve the real data.
    
    Args:
        args: Dictionary with:
            - item_index: Index of item from search results (default: 0)
        context: Server context containing search results
    
    Returns:
        Detailed asset information including URLs and data access instructions
    """
    item_index = args.get("item_index", 0)
    
    features = context.get("geobon_search_results", [])
    if not features:
        return "Error: No search results found. Please run geobon_search_collection first."
    
    if item_index >= len(features):
        return f"Error: Item index {item_index} out of range. Only {len(features)} items available."
    
    feature = features[item_index]
    feature_id = feature.get("id", "Unknown")
    assets = feature.get("assets", {})
    
    result = f"📦 Asset Details for Item: {feature_id}\n"
    result += "=" * 60 + "\n\n"
    
    if not assets:
        return result + "No assets found in this item."
    
    for asset_key, asset_info in assets.items():
        result += f"🗂️ Asset: {asset_key}\n"
        result += f"   Title: {asset_info.get('title', 'No title')}\n"
        result += f"   Type: {asset_info.get('type', 'unknown')}\n"
        result += f"   URL: {asset_info.get('href', 'No URL')}\n"
        
        # Check for additional properties
        if 'roles' in asset_info:
            result += f"   Roles: {', '.join(asset_info['roles'])}\n"
        
        # Check for raster extension info (common in STAC)
        if 'raster:bands' in asset_info:
            bands = asset_info['raster:bands']
            result += f"   Bands: {len(bands)}\n"
            for i, band in enumerate(bands):
                result += f"      Band {i+1}: {band.get('description', 'No description')}\n"
                if 'nodata' in band:
                    result += f"         NoData: {band['nodata']}\n"
                if 'data_type' in band:
                    result += f"         Data Type: {band['data_type']}\n"
        
        result += "\n"
    
    result += "\n💡 To retrieve actual data, use:\n"
    result += "   • geobon_get_raster_data - for GeoTIFF analysis\n"
    result += "   • geobon_get_raster_stats - for statistics within a region\n"
    result += "   • geobon_download_asset - to download the full file\n"
    
    return result


def geobon_get_raster_data_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    ACTUALLY RETRIEVE AND ANALYZE RASTER DATA from GEO BON STAC assets.
    
    This function downloads the GeoTIFF data and extracts real values,
    not just the coverage area. Supports:
    - Reading a specific region (by bbox)
    - Getting statistics (min, max, mean, std)
    - Counting pixels by value (e.g., forest loss years)
    - Calculating area in hectares
    
    Args:
        args: Dictionary with:
            - item_index: Index of item from search results (default: 0)
            - asset_key: Key of raster asset to read (default: auto-detect)
            - bbox: Optional [west, south, east, north] to subset data
            - calculate_stats: Whether to calculate statistics (default: True)
        context: Server context containing search results
    
    Returns:
        Actual data values and statistics from the raster
    """
    try:
        import rasterio
        from rasterio.windows import from_bounds
        from rasterio.crs import CRS
        import numpy as np
    except ImportError:
        return """Error: Required libraries not installed. 
Please install with: pip install rasterio numpy

These libraries are needed to read and analyze actual GeoTIFF data.
"""
    
    item_index = args.get("item_index", 0)
    asset_key = args.get("asset_key")
    user_bbox = args.get("bbox")
    calculate_stats = args.get("calculate_stats", True)
    
    # Get search results from context
    features = context.get("geobon_search_results", [])
    if not features:
        return "Error: No search results found. Please run geobon_search_collection first."
    
    if item_index >= len(features):
        return f"Error: Item index {item_index} out of range."
    
    feature = features[item_index]
    feature_id = feature.get("id", "Unknown")
    assets = feature.get("assets", {})
    
    # Auto-detect raster asset if not specified
    if not asset_key:
        for key, info in assets.items():
            asset_type = info.get("type", "").lower()
            if "tiff" in asset_type or "geotiff" in asset_type or key == "data":
                asset_key = key
                break
        
        if not asset_key:
            available = ", ".join(assets.keys())
            return f"Error: Could not auto-detect raster asset. Available: {available}"
    
    if asset_key not in assets:
        available = ", ".join(assets.keys())
        return f"Error: Asset '{asset_key}' not found. Available: {available}"
    
    asset_url = assets[asset_key].get("href")
    if not asset_url:
        return f"Error: No URL found for asset '{asset_key}'"
    
    result = f"📊 ACTUAL RASTER DATA Analysis\n"
    result += f"Item: {feature_id}\n"
    result += f"Asset: {asset_key}\n"
    result += "=" * 60 + "\n\n"
    
    try:
        # Open raster data - rasterio can read Cloud-Optimized GeoTIFFs directly via HTTP
        with rasterio.open(asset_url) as src:
            result += f"🗺️ Raster Properties:\n"
            result += f"   Size: {src.width} x {src.height} pixels\n"
            result += f"   CRS: {src.crs}\n"
            result += f"   Bands: {src.count}\n"
            result += f"   Data Type: {src.dtypes[0]}\n"
            result += f"   Resolution: {src.res[0]:.6f} x {src.res[1]:.6f} (degrees/meters)\n"
            result += f"   Full Bounds: {src.bounds}\n\n"
            
            # Read data - either full or windowed
            if user_bbox:
                # Read only the region specified
                window = from_bounds(
                    user_bbox[0], user_bbox[1], 
                    user_bbox[2], user_bbox[3], 
                    src.transform
                )
                data = src.read(1, window=window)
                result += f"📍 Reading subset region: {user_bbox}\n"
            else:
                # For large files, read a sample or the full array
                if src.width * src.height > 10000000:  # > 10M pixels
                    # Read a center sample for statistics
                    result += f"⚠️ Large file - reading center sample (1000x1000)\n"
                    center_x = src.width // 2
                    center_y = src.height // 2
                    window = rasterio.windows.Window(
                        center_x - 500, center_y - 500, 1000, 1000
                    )
                    data = src.read(1, window=window)
                else:
                    data = src.read(1)
            
            if calculate_stats:
                result += f"\n📈 DATA STATISTICS (actual values!):\n"
                
                # Handle nodata values
                nodata = src.nodata
                if nodata is not None:
                    valid_data = data[data != nodata]
                    result += f"   NoData Value: {nodata}\n"
                    result += f"   Valid Pixels: {len(valid_data):,} of {data.size:,}\n"
                else:
                    valid_data = data.flatten()
                    result += f"   Total Pixels: {data.size:,}\n"
                
                if len(valid_data) > 0:
                    result += f"\n   Min Value: {np.min(valid_data)}\n"
                    result += f"   Max Value: {np.max(valid_data)}\n"
                    result += f"   Mean Value: {np.mean(valid_data):.4f}\n"
                    result += f"   Std Dev: {np.std(valid_data):.4f}\n"
                    
                    # For forest loss year data (values 1-23 = years 2001-2023)
                    unique_values = np.unique(valid_data)
                    if len(unique_values) <= 30:
                        result += f"\n   📊 Value Distribution:\n"
                        for val in sorted(unique_values):
                            count = np.sum(valid_data == val)
                            pct = (count / len(valid_data)) * 100
                            
                            # For GFW loss year, interpret the value
                            if 1 <= val <= 23:
                                year = 2000 + int(val)
                                result += f"      {int(val)}: {count:,} pixels ({pct:.2f}%) - Year {year}\n"
                            else:
                                result += f"      {val}: {count:,} pixels ({pct:.2f}%)\n"
                    else:
                        result += f"   Unique Values: {len(unique_values)} (too many to list)\n"
                    
                    # Calculate approximate area
                    pixel_area_deg = abs(src.res[0] * src.res[1])
                    # Rough conversion: 1 degree ≈ 111km at equator
                    pixel_area_km2 = pixel_area_deg * (111 ** 2)
                    pixel_area_ha = pixel_area_km2 * 100  # 1 km² = 100 ha
                    
                    total_area_ha = len(valid_data) * pixel_area_ha
                    result += f"\n   📐 Approximate Area:\n"
                    result += f"      Pixel size: ~{pixel_area_ha:.4f} hectares\n"
                    result += f"      Total valid area: ~{total_area_ha:,.0f} hectares\n"
                else:
                    result += "   No valid data found in this region.\n"
        
        result += "\n✅ Successfully retrieved ACTUAL DATA from the STAC asset!\n"
        result += "\n💡 This shows real values from the GeoTIFF, not just coverage area."
        
    except Exception as e:
        result += f"\n❌ Error reading raster data: {str(e)}\n"
        result += "\nPossible causes:\n"
        result += "  • Network connectivity issues\n"
        result += "  • Authentication required for this dataset\n"
        result += "  • File format not supported\n"
        result += f"\nAsset URL: {asset_url}\n"
        result += "\nTry downloading the file first with geobon_download_asset"
    
    return result


def geobon_calculate_forest_loss_stats_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Calculate detailed forest loss statistics for a specific region.
    
    This provides ESG-relevant metrics like:
    - Total hectares of forest lost per year
    - Deforestation rates and trends
    - Cumulative loss over time periods
    
    Args:
        args: Dictionary with:
            - item_index: Index of item from search results (default: 0)
            - bbox: Bounding box [west, south, east, north] for region of interest
            - start_year: Start year for analysis (default: 2001)
            - end_year: End year for analysis (default: 2023)
        context: Server context containing search results
    
    Returns:
        Detailed forest loss statistics with ESG context
    """
    try:
        import rasterio
        from rasterio.windows import from_bounds
        import numpy as np
    except ImportError:
        return "Error: Install rasterio and numpy: pip install rasterio numpy"
    
    item_index = args.get("item_index", 0)
    user_bbox = args.get("bbox")
    start_year = args.get("start_year", 2001)
    end_year = args.get("end_year", 2023)
    
    features = context.get("geobon_search_results", [])
    collection_id = context.get("geobon_collection_id", "Unknown")
    
    if not features:
        return "Error: No search results found. Please run geobon_search_collection first."
    
    if item_index >= len(features):
        return f"Error: Item index {item_index} out of range."
    
    feature = features[item_index]
    feature_id = feature.get("id", "Unknown")
    assets = feature.get("assets", {})
    
    # Find the data asset
    asset_url = None
    for key, info in assets.items():
        asset_type = info.get("type", "").lower()
        if "tiff" in asset_type or key == "data":
            asset_url = info.get("href")
            break
    
    if not asset_url:
        return "Error: No raster data asset found in this item."
    
    result = "🌲 FOREST LOSS STATISTICS (ACTUAL DATA)\n"
    result += "=" * 60 + "\n"
    result += f"Collection: {collection_id}\n"
    result += f"Item: {feature_id}\n"
    if user_bbox:
        result += f"Region: [{user_bbox[0]:.2f}°, {user_bbox[1]:.2f}°] to [{user_bbox[2]:.2f}°, {user_bbox[3]:.2f}°]\n"
    result += f"Analysis Period: {start_year} - {end_year}\n"
    result += "=" * 60 + "\n\n"
    
    try:
        with rasterio.open(asset_url) as src:
            # Read the data
            if user_bbox:
                window = from_bounds(
                    user_bbox[0], user_bbox[1], 
                    user_bbox[2], user_bbox[3], 
                    src.transform
                )
                data = src.read(1, window=window)
            else:
                # Read full dataset or sample
                if src.width * src.height > 10000000:
                    result += "⚠️ Large dataset - using sampling\n\n"
                    center_x, center_y = src.width // 2, src.height // 2
                    window = rasterio.windows.Window(center_x - 500, center_y - 500, 1000, 1000)
                    data = src.read(1, window=window)
                else:
                    data = src.read(1)
            
            # Calculate pixel area
            pixel_area_deg = abs(src.res[0] * src.res[1])
            pixel_area_ha = pixel_area_deg * (111 ** 2) * 100  # hectares
            
            nodata = src.nodata
            if nodata is not None:
                data = np.where(data == nodata, 0, data)
            
            # Calculate yearly statistics
            result += "📊 YEARLY FOREST LOSS:\n"
            result += "-" * 40 + "\n"
            
            yearly_stats = []
            total_loss_ha = 0
            
            for year in range(start_year, end_year + 1):
                year_code = year - 2000  # GFW uses 1=2001, 2=2002, etc.
                pixel_count = np.sum(data == year_code)
                area_ha = pixel_count * pixel_area_ha
                yearly_stats.append((year, pixel_count, area_ha))
                total_loss_ha += area_ha
                
                if pixel_count > 0:
                    result += f"   {year}: {area_ha:,.0f} hectares ({pixel_count:,} pixels)\n"
            
            result += "-" * 40 + "\n"
            result += f"   TOTAL: {total_loss_ha:,.0f} hectares\n\n"
            
            # Calculate trends
            recent_5yr = sum(s[2] for s in yearly_stats[-5:])
            earlier_5yr = sum(s[2] for s in yearly_stats[:5]) if len(yearly_stats) >= 10 else 0
            
            result += "📈 TREND ANALYSIS:\n"
            result += f"   Recent 5 years ({end_year-4}-{end_year}): {recent_5yr:,.0f} hectares\n"
            if earlier_5yr > 0:
                result += f"   Earlier period ({start_year}-{start_year+4}): {earlier_5yr:,.0f} hectares\n"
                change_pct = ((recent_5yr - earlier_5yr) / earlier_5yr) * 100
                trend = "INCREASING ⬆️" if change_pct > 10 else "DECREASING ⬇️" if change_pct < -10 else "STABLE ➡️"
                result += f"   Trend: {trend} ({change_pct:+.1f}%)\n"
            
            result += "\n🎯 ESG RELEVANCE:\n"
            result += "   • Deforestation tracking for supply chain due diligence\n"
            result += "   • Carbon impact assessment (forests = carbon sinks)\n"
            result += "   • Biodiversity loss monitoring\n"
            result += "   • Regulatory compliance (EU Deforestation Regulation)\n"
            
            # Store statistics in context for other tools
            context["forest_loss_stats"] = {
                "total_loss_ha": total_loss_ha,
                "yearly_stats": yearly_stats,
                "region_bbox": user_bbox,
                "analysis_period": f"{start_year}-{end_year}"
            }
            
    except Exception as e:
        result += f"\n❌ Error: {str(e)}\n"
        result += "Try downloading the data first with geobon_download_asset"
    
    return result


def geobon_download_asset_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Download an asset from a GEO BON STAC item.
    """
    item_index = args.get("item_index", 0)
    asset_key = args.get("asset_key")
    output_dir = args.get("output_dir", "downloads/geobon")
    
    features = context.get("geobon_search_results", [])
    if not features:
        return "Error: No search results found. Please run geobon_search_collection first."
    
    if item_index >= len(features):
        return f"Error: Item index {item_index} out of range."
    
    feature = features[item_index]
    assets = feature.get("assets", {})
    
    if not asset_key:
        if not assets:
            return "Error: No assets found in this item."
        result = "Available assets for this item:\n\n"
        for key, asset_info in assets.items():
            title = asset_info.get("title", "No title")
            asset_type = asset_info.get("type", "unknown")
            result += f"• {key}: {title} (type: {asset_type})\n"
        result += "\nSpecify 'asset_key' parameter to download."
        return result
    
    if asset_key not in assets:
        return f"Error: Asset '{asset_key}' not found."
    
    asset = assets[asset_key]
    asset_url = asset.get("href")
    
    if not asset_url:
        return f"Error: No URL found for asset '{asset_key}'"
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        feature_id = feature.get("id", "unknown")
        clean_id = feature_id.replace("/", "_").replace("\\", "_")
        file_ext = asset_url.split(".")[-1].split("?")[0] if "." in asset_url else "dat"
        filename = f"{clean_id}_{asset_key}.{file_ext}"
        filepath = os.path.join(output_dir, filename)
        
        print(f"Downloading {asset_url}...")
        response = requests.get(asset_url, timeout=120, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(filepath)
        size_mb = file_size / (1024 * 1024)
        
        return f"✅ Downloaded successfully!\nFile: {filepath}\nSize: {size_mb:.2f} MB"
        
    except Exception as e:
        return f"Error downloading asset: {str(e)}"


def geobon_visualize_forest_loss_tool(args: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Create an interactive map WITH ACTUAL DATA visualization.
    
    IMPROVED: Now shows actual forest loss statistics on the map,
    not just the coverage area!
    """
    try:
        import folium
    except ImportError:
        return "Error: folium not installed. Run: pip install folium"
    
    item_index = args.get("item_index", 0)
    output_file = args.get("output_file", "geobon_forest_loss_map.html")
    region_name = args.get("region_name", "Global")
    
    features = context.get("geobon_search_results", [])
    collection_id = context.get("geobon_collection_id", "Unknown")
    
    if not features:
        return "Error: No search results found. Please run geobon_search_collection first."
    
    if item_index >= len(features):
        return f"Error: Item index {item_index} out of range."
    
    feature = features[item_index]
    properties = feature.get("properties", {})
    feature_id = feature.get("id", "Unknown")
    bbox = feature.get("bbox")
    
    # Get forest loss stats if available
    forest_stats = context.get("forest_loss_stats", {})
    has_actual_data = bool(forest_stats)
    
    # Calculate center and zoom
    if bbox and len(bbox) == 4:
        center = [(bbox[1] + bbox[3]) / 2, (bbox[0] + bbox[2]) / 2]
        lat_range = abs(bbox[3] - bbox[1])
        lon_range = abs(bbox[2] - bbox[0])
        max_range = max(lat_range, lon_range)
        
        if max_range > 100:
            auto_zoom = 2
        elif max_range > 50:
            auto_zoom = 3
        elif max_range > 20:
            auto_zoom = 4
        elif max_range > 10:
            auto_zoom = 5
        else:
            auto_zoom = 6
            
        zoom = args.get("zoom", auto_zoom)
    else:
        center = [0, 0]
        bbox = [-180, -90, 180, 90]
        zoom = args.get("zoom", 2)
    
    # Create map
    m = folium.Map(
        location=center, 
        zoom_start=zoom, 
        tiles="OpenStreetMap",
        world_copy_jump=False,
        no_wrap=True,
        min_zoom=2,
        max_bounds=True
    )
    
    # Add satellite layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite Imagery',
        overlay=False,
        control=True,
        no_wrap=True
    ).add_to(m)
    
    # Create popup content with ACTUAL DATA if available
    if has_actual_data:
        total_loss = forest_stats.get("total_loss_ha", 0)
        period = forest_stats.get("analysis_period", "N/A")
        popup_content = f"""
        <div style="width: 320px; font-family: Arial, sans-serif; padding: 10px;">
            <h3 style="color: #D32F2F; margin: 0 0 10px 0;">🌲 Actual Forest Loss Data</h3>
            <b>Collection:</b> {collection_id}<br>
            <b>Region:</b> {region_name}<br>
            <hr style="margin: 10px 0;">
            <div style="background: #fff3f3; padding: 10px; border-radius: 5px;">
                <b style="color: #D32F2F; font-size: 18px;">{total_loss:,.0f} hectares</b><br>
                <span style="font-size: 12px;">Total forest loss ({period})</span>
            </div>
            <hr style="margin: 10px 0;">
            <small style="color: #666;">✅ This shows ACTUAL DATA, not just coverage area!</small>
        </div>
        """
    else:
        popup_content = f"""
        <div style="width: 280px; font-family: Arial, sans-serif; padding: 5px;">
            <b style="color: #D32F2F;">🌲 Coverage Area</b><br><br>
            <b>Collection:</b> {collection_id}<br>
            <b>Item:</b> {feature_id}<br>
            <b>Region:</b> {region_name}<br>
            <hr style="margin: 10px 0;">
            <small style="color: #666;">
                ⚠️ This shows coverage area only.<br>
                Run geobon_calculate_forest_loss_stats to get actual data!
            </small>
        </div>
        """
    
    # Add coverage rectangle
    if bbox and len(bbox) == 4:
        folium.Rectangle(
            bounds=[[bbox[1], bbox[0]], [bbox[3], bbox[2]]],
            color='#D32F2F',
            weight=2,
            fill=True,
            fillColor='#EF5350',
            fillOpacity=0.15,
            popup=folium.Popup(popup_content, max_width=350)
        ).add_to(m)
    
    # Add center marker
    marker_icon = folium.Icon(color='darkred', icon='tree', prefix='fa')
    folium.Marker(location=center, popup=folium.Popup(popup_content, max_width=350), icon=marker_icon).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Info box content
    if has_actual_data:
        info_content = f"""
        <div style="position: fixed; top: 10px; right: 10px; width: 280px; 
                    background: rgba(255,255,255,0.95); border: 3px solid #D32F2F;
                    z-index: 9999; padding: 15px; border-radius: 5px; font-family: Arial;">
            <div style="font-size: 14px; font-weight: bold; color: #D32F2F;">
                ✅ ACTUAL DATA LOADED
            </div>
            <div style="margin: 10px 0; padding: 10px; background: #fff3f3; border-radius: 3px;">
                <span style="font-size: 20px; font-weight: bold; color: #D32F2F;">
                    {forest_stats.get('total_loss_ha', 0):,.0f}
                </span><br>
                <span style="font-size: 11px;">hectares of forest loss</span>
            </div>
            <div style="font-size: 10px; color: #666;">
                Period: {forest_stats.get('analysis_period', 'N/A')}<br>
                Region: {region_name}
            </div>
        </div>
        """
    else:
        info_content = f"""
        <div style="position: fixed; top: 10px; right: 10px; width: 280px; 
                    background: rgba(255,255,255,0.95); border: 3px solid #FFA000;
                    z-index: 9999; padding: 15px; border-radius: 5px; font-family: Arial;">
            <div style="font-size: 14px; font-weight: bold; color: #FFA000;">
                ⚠️ COVERAGE AREA ONLY
            </div>
            <div style="margin: 10px 0; font-size: 11px; color: #666;">
                This map shows WHERE the data exists, but not the actual values.
            </div>
            <div style="font-size: 10px; padding: 8px; background: #fff8e1; border-radius: 3px;">
                💡 To load actual data, run:<br>
                <code>geobon_calculate_forest_loss_stats</code>
            </div>
        </div>
        """
    
    m.get_root().html.add_child(folium.Element(info_content))
    
    # Save map
    m.save(output_file)
    
    if has_actual_data:
        return f"""✅ Map Created WITH ACTUAL DATA!

📊 Forest Loss Summary:
   Total Loss: {forest_stats.get('total_loss_ha', 0):,.0f} hectares
   Period: {forest_stats.get('analysis_period', 'N/A')}
   Region: {region_name}

🗺️ Map saved to: {output_file}

This map shows REAL forest loss statistics, not just the coverage area!
"""
    else:
        return f"""⚠️ Map Created (Coverage Area Only)

🗺️ Map saved to: {output_file}

NOTE: This map shows only WHERE the data exists.
To get ACTUAL forest loss statistics, run:

1. geobon_get_raster_data - to see raw data values
2. geobon_calculate_forest_loss_stats - for detailed statistics

Then re-run this visualization to see the actual data on the map.
"""


# Tool registration dictionary
GEOBON_TOOLS = {
    "geobon_list_collections": geobon_list_collections_tool,
    "geobon_get_collection_info": geobon_get_collection_info_tool,
    "geobon_search_collection": geobon_search_collection_tool,
    "geobon_get_asset_info": geobon_get_asset_info_tool,  # NEW
    "geobon_get_raster_data": geobon_get_raster_data_tool,  # NEW - Get actual data!
    "geobon_calculate_forest_loss_stats": geobon_calculate_forest_loss_stats_tool,  # NEW
    "geobon_download_asset": geobon_download_asset_tool,
    "geobon_visualize_forest_loss": geobon_visualize_forest_loss_tool,  # IMPROVED
}
