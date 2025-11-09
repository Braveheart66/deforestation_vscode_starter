import geemap
import ee
import os

# Initialize Earth Engine safely
try:
    ee.Initialize(project='smooth-drive-477310-t9')
    print("✅ Earth Engine initialized successfully.")
except Exception:
    print("⚠️ Authentication required... running OAuth flow.")
    ee.Authenticate()
    ee.Initialize(project='smooth-drive-477310-t9')
    print("✅ Earth Engine re-initialized after authentication.")

# Define AOI (same as your inpu.geojson)
aoi = ee.Geometry.Polygon(
    [[[80.90, 28.60],
      [80.90, 28.70],
      [81.00, 28.70],
      [81.00, 28.60],
      [80.90, 28.60]]]
)

# Fetch Sentinel-2 harmonized NDVI
img = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(aoi)
    .filterDate("2024-01-01", "2024-03-31")
    .median()
    .normalizedDifference(['B8', 'B4'])
    .rename('NDVI')
)

# ----------------------------------------------------------------
# ✅ Safe export workaround for the deprecated _credentials method
# ----------------------------------------------------------------
def safe_export_to_drive(image, filename, scale, region):
    """Export to Google Drive safely without using deprecated credentials."""
    try:
        description = os.path.splitext(os.path.basename(filename))[0]
        task = ee.batch.Export.image.toDrive(
            image=image,
            description=description,
            folder='deforestation_exports',
            fileNamePrefix=description,
            region=region,
            scale=scale,
            maxPixels=1e13,
            fileFormat='GeoTIFF'
        )
        task.start()
        print(f"📤 Export started in Google Drive as '{description}' (check Drive > deforestation_exports)")
    except Exception as e:
        print(f"❌ Export failed: {e}")

# ✅ Export NDVI as GeoTIFF (mock drone NDVI)
safe_export_to_drive(img, "drone_ndvi_mock.tif", 10, aoi)
print("✅ Mock drone NDVI export started — check Google Drive folder 'deforestation_exports'.")
