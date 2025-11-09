import ee
import geemap

# Initialize Earth Engine
try:
    ee.Initialize(project='smooth-drive-477310-t9')
    print("✅ Earth Engine initialized successfully.")
except Exception:
    ee.Authenticate()
    ee.Initialize(project='smooth-drive-477310-t9')

# Deforestation AOI in Lucknow
aoi = ee.Geometry.Polygon([
    [
        [80.9273, 26.7811],
        [80.9273, 26.8185],
        [80.9825, 26.8185],
        [80.9825, 26.7811],
        [80.9273, 26.7811]
    ]
])

# Generate NDVI for 2019 (healthy vegetation)
past_ndvi = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(aoi)
    .filterDate("2019-01-01", "2019-03-31")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))
    .median()
    .normalizedDifference(["B8", "B4"])
    .rename("NDVI")
)

# Simulate current NDVI (reduced vegetation → deforestation)
# Apply artificial decrease to NDVI to emulate urban development
present_ndvi = past_ndvi.multiply(0.6).rename("NDVI")  # 40% vegetation loss

# Export simulated "drone" NDVI GeoTIFF
output_path = "outputs/lucknow_drone_ndvi_mock_deforestation.tif"
geemap.ee_export_image(
    present_ndvi.clip(aoi),
    filename=output_path,
    scale=10,
    region=aoi,
    file_per_band=False
)

print(f"✅ Mock deforestation NDVI exported to {output_path}")

