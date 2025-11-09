import numpy as np
import rasterio
from rasterio.transform import from_bounds

# Define AOI bounding box (Lucknow region)
minx, miny, maxx, maxy = 80.85, 26.75, 81.05, 26.95
width, height = 400, 400  # resolution

# Create synthetic NDVI pattern
x = np.linspace(-1, 1, width)
y = np.linspace(-1, 1, height)
xx, yy = np.meshgrid(x, y)
ndvi = 0.5 * np.exp(-(xx**2 + yy**2))  # centered green blob
ndvi += 0.2 * np.sin(3 * xx) * np.cos(3 * yy)  # natural variation

# simulate past vs present NDVI
ndvi_past = ndvi + np.random.normal(0, 0.05, ndvi.shape)
ndvi_present = ndvi - 0.1 * (xx > 0.3)  # remove greens in one side

ndvi = np.clip(ndvi, -0.2, 0.9)

# Define raster metadata
transform = from_bounds(minx, miny, maxx, maxy, width, height)
meta = {
    "driver": "GTiff",
    "dtype": "float32",
    "count": 1,
    "height": height,
    "width": width,
    "transform": transform,
    "crs": "EPSG:4326"
}

output_path = "outputs/drone_ndvi_mock_lko.tif"

# Write GeoTIFF
with rasterio.open(output_path, "w", **meta) as dst:
    dst.write(ndvi.astype("float32"), 1)

print(f"✅ Mock NDVI GeoTIFF generated at: {output_path}")
