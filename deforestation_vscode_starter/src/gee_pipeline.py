import os
import json
import ee
import geemap
import geopandas as gpd

# ------------------ Initialize Earth Engine ------------------
def _init_ee():
    """Safely initialize Google Earth Engine."""
    try:
        ee.Initialize(project='smooth-drive-477310-t9')
        print("✅ Earth Engine initialized successfully.")
    except Exception:
        print("⚠️ Authentication required... launching OAuth flow.")
        ee.Authenticate()
        ee.Initialize(project='smooth-drive-477310-t9')
        print("✅ Earth Engine re-initialized after authentication.")


# ------------------ Load AOI ------------------
def load_aoi(aoi_path):
    gdf = gpd.read_file(aoi_path)
    geojson = json.loads(gdf.to_json())
    region = ee.Geometry(geojson["features"][0]["geometry"])
    print("🌍 AOI loaded successfully.")
    return region


# ------------------ Sentinel-2 NDVI ------------------
def get_s2_ndvi(start, end, region, cloud_prob):
    """
    Returns median NDVI image for the given date range and AOI.
    Includes robust checks and a fallback to MODIS NDVI if Sentinel-2 is unavailable.
    """
    data_source = "Sentinel-2"

    s2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_prob))
    )

    count = s2.size().getInfo()
    if count == 0:
        print(f"⚠️ No Sentinel-2 images found for {start}–{end}. Relaxing filters...")
        s2 = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(region)
            .filterDate(start, end)
        )
        count = s2.size().getInfo()

        if count == 0:
            print("🌍 Falling back to MODIS NDVI (MOD13Q1)...")
            data_source = "MODIS"
            modis = (
                ee.ImageCollection("MODIS/061/MOD13Q1")
                .filterBounds(region)
                .filterDate(start, end)
                .select("NDVI")
                .mean()
                .divide(10000)
                .rename("NDVI")
            )
            return modis, data_source

    s2_median = s2.median()
    bands = s2_median.bandNames().getInfo()
    print(f"✅ Found Sentinel-2 images ({count}) with bands: {bands}")

    if not all(b in bands for b in ["B8", "B4"]):
        print(f"⚠️ Sentinel-2 image missing required bands ({bands}), using MODIS fallback...")
        data_source = "MODIS"
        modis = (
            ee.ImageCollection("MODIS/061/MOD13Q1")
            .filterBounds(region)
            .filterDate(start, end)
            .select("NDVI")
            .mean()
            .divide(10000)
            .rename("NDVI")
        )
        return modis, data_source

    ndvi = s2_median.normalizedDifference(["B8", "B4"]).rename("NDVI")
    return ndvi, data_source



# ------------------ Forest Mask ------------------
def forest_mask(ndvi_image, threshold):
    return ndvi_image.gt(threshold).selfMask().rename("ForestMask")


# ------------------ Area Calculation ------------------
def calc_area(mask, region):
    area_img = mask.multiply(ee.Image.pixelArea()).divide(10000)
    stats = area_img.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=region,
        scale=30,
        maxPixels=1e13,
    )
    return stats.getInfo().get("ForestMask", 0)


# ------------------ Local Export ------------------
def export_image_local(image, filename, region, scale=30):
    os.makedirs("outputs", exist_ok=True)
    path = os.path.abspath(os.path.join("outputs", filename))
    try:
        print(f"🛰️ Exporting {filename} ...")
        geemap.ee_export_image(
            image.clip(region),
            filename=path,
            scale=scale,
            region=region,
            file_per_band=False,
        )
        print(f"✅ Exported: {path}")
    except Exception as e:
        print(f"❌ Export failed: {e}")


# ------------------ Save Report ------------------
def save_report(data):
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/deforestation_report.json", "w") as f:
        json.dump(data, f, indent=4)
    print("📄 Report saved → outputs/deforestation_report.json")


# ------------------ Run Pipeline ------------------
def run(aoi_path, t0, t1, ndvi_thresh, cloud_prob):
    _init_ee()
    region = load_aoi(aoi_path)

    print("🕒 Fetching NDVI composites...")
    ndvi_past, source_past = get_s2_ndvi(t0[0], t0[1], region, cloud_prob)
    ndvi_now, source_now = get_s2_ndvi(t1[0], t1[1], region, cloud_prob)


    mask_past = forest_mask(ndvi_past, ndvi_thresh)
    mask_now = forest_mask(ndvi_now, ndvi_thresh)

    forest_area_t0 = calc_area(mask_past, region)
    forest_area_t1 = calc_area(mask_now, region)

    # Change detection
    if forest_area_t0 > 0:
        change_percent = ((forest_area_t1 - forest_area_t0) / forest_area_t0) * 100
    else:
        change_percent = 0

    if change_percent < 0:
        change_type = "Loss"
    else:
        change_type = "Gain"

    report = {
    "region": "AOI",
    "past_window": t0,
    "present_window": t1,
    "forest_area_past_ha": round(forest_area_t0, 2),
    "forest_area_present_ha": round(forest_area_t1, 2),
    "change_percent": round(abs(change_percent), 2),
    "change_type": change_type,
    "ndvi_threshold_used": ndvi_thresh,
    "data_source_past": source_past,
    "data_source_present": source_now
}


    # Save & export
    save_report(report)
    export_image_local(mask_past, "forest_mask_past.tif", region)
    export_image_local(mask_now, "forest_mask_present.tif", region)

    print("✅ Pipeline finished successfully.")
    return report
