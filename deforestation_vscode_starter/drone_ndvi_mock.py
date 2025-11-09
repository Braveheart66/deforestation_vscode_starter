import ee
import geemap
import os

def init_ee():
    try:
        ee.Initialize(project='smooth-drive-477310-t9')
        print("✅ EE initialized.")
    except Exception:
        print("⚠️ Auth required... running OAuth.")
        ee.Authenticate()
        ee.Initialize(project='smooth-drive-477310-t9')
        print("✅ Re-initialized.")

if __name__ == "__main__":
    init_ee()

    aoi = ee.Geometry.Polygon(
        [[[80.90, 28.60],
          [80.90, 28.70],
          [81.00, 28.70],
          [81.00, 28.60],
          [80.90, 28.60]]]
    )

    img = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate("2024-01-01", "2024-03-31")
        .median()
        .normalizedDifference(['B8', 'B4'])
        .rename('NDVI')
    )

    os.makedirs("outputs", exist_ok=True)
    output_path = "outputs/drone_ndvi_mock.tif"

    print("🛰️ Exporting mock drone NDVI locally...")
    geemap.ee_export_image(img.clip(aoi), filename=output_path, scale=30, region=aoi)
    print(f"✅ Saved mock NDVI → {output_path}")
