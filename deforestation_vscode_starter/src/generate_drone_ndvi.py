import ee
import geemap

# Initialize Earth Engine
try:
    ee.Initialize(project='smooth-drive-477310-t9')
    print("✅ Earth Engine initialized successfully.")
except Exception:
    print("⚠️ Authentication required — running OAuth flow.")
    ee.Authenticate()
    ee.Initialize(project='smooth-drive-477310-t9')

# Kukrail AOI
aoi = ee.Geometry.Polygon([
    [
        [80.9826, 26.9128],
        [80.9826, 26.9450],
        [81.0255, 26.9450],
        [81.0255, 26.9128],
        [80.9826, 26.9128]
    ]
])

# Sentinel-2 NDVI composite for 2024
ndvi = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(aoi)
    .filterDate("2024-01-01", "2024-03-31")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40))
    .median()
    .normalizedDifference(["B8", "B4"])
    .rename("NDVI")
)

# Export NDVI as a local mock drone GeoTIFF
output_path = "outputs/kukrail_drone_ndvi_mock.tif"
geemap.ee_export_image(
    ndvi.clip(aoi),
    filename=output_path,
    scale=10,
    region=aoi,
    file_per_band=False
)

print(f"✅ Mock drone NDVI exported to {output_path}")

