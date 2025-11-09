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

# Define Lucknow AOI
aoi = ee.Geometry.Polygon([
    [
        [80.8005, 26.6803],
        [80.8005, 27.0500],
        [81.0800, 27.0500],
        [81.0800, 26.6803],
        [80.8005, 26.6803]
    ]
])

# Sentinel-2 NDVI composite for 2018 (healthy vegetation)
print("🕒 Generating 2018 NDVI composite...")
past_ndvi = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(aoi)
    .filterDate("2018-01-01", "2018-03-31")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))
    .median()
    .normalizedDifference(["B8", "B4"])
    .rename("NDVI")
)

# Simulated 2024 NDVI (scaled down to show vegetation loss)
print("🌳 Simulating 2024 NDVI with lower vegetation values...")
present_ndvi = past_ndvi.multiply(0.65).rename("NDVI")  # simulate 35% deforestation

# Export both NDVI layers
print("📤 Exporting mock drone NDVI (present) for dashboard use...")
geemap.ee_export_image(
    present_ndvi.clip(aoi),
    filename="outputs/lucknow_drone_ndvi_mock_citywide.tif",
    scale=30,
    region=aoi,
    file_per_band=False
)

print("✅ City-wide NDVI export complete → outputs/lucknow_drone_ndvi_mock_citywide.tif")
