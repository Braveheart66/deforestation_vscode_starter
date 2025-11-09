from __future__ import annotations
import numpy as np, rasterio
from skimage.filters import threshold_otsu
from skimage.morphology import binary_closing, remove_small_objects, disk
from typing import Dict, Any, Tuple
from .utils import ensure_dirs, save_report, percent_from_areas, save_preview_change

def compute_ndvi(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
    red = red.astype("float32"); nir = nir.astype("float32")
    return (nir - red) / np.clip(nir + red, 1e-6, None)

def read_band(path: str) -> Tuple[np.ndarray, float]:
    with rasterio.open(path) as ds:
        band = ds.read(1)
        # pixel area from transform (assumes meters; ensure projected CRS)
        pix_area = abs(ds.transform.a * ds.transform.e)
    return band, pix_area

def run(red_past: str, nir_past: str, red_present: str, nir_present: str,
        ndvi_thresh: float | None, min_patch_pixels: int, morph_radius: int) -> Dict[str,Any]:
    ensure_dirs()
    r0, pa0 = read_band(red_past); n0, _ = read_band(nir_past)
    r1, pa1 = read_band(red_present); n1, _ = read_band(nir_present)
    if abs(pa0 - pa1) > 1e-6:
        print("Warning: pixel areas differ between rasters. Using past's pixel area for area calc.")
    pix_area = pa0

    ndvi0 = compute_ndvi(r0, n0)
    ndvi1 = compute_ndvi(r1, n1)

    mask0 = ndvi0 > (threshold_otsu(ndvi0[np.isfinite(ndvi0)]) if ndvi_thresh is None else ndvi_thresh)
    mask1 = ndvi1 > (threshold_otsu(ndvi1[np.isfinite(ndvi1)]) if ndvi_thresh is None else ndvi_thresh)

    # clean small speckles
    if morph_radius > 0:
        mask0 = binary_closing(mask0, disk(morph_radius))
        mask1 = binary_closing(mask1, disk(morph_radius))
    if min_patch_pixels > 0:
        mask0 = remove_small_objects(mask0, min_size=min_patch_pixels)
        mask1 = remove_small_objects(mask1, min_size=min_patch_pixels)

    past_area_m2 = int(mask0.sum()) * pix_area
    pres_area_m2 = int(mask1.sum()) * pix_area
    past_ha = past_area_m2 / 10000.0
    pres_ha = pres_area_m2 / 10000.0
    remaining, loss = percent_from_areas(past_ha, pres_ha)

    report = {
        "region": "AOI",
        "past_window": ["(local)", "(local)"],
        "present_window": ["(local)", "(local)"],
        "total_area_ha": round((mask0.size * pix_area)/10000.0, 2),
        "forest_area_past_ha": round(past_ha, 2),
        "forest_area_present_ha": round(pres_ha, 2),
        "remaining_percent": round(remaining, 2),
        "deforestation_percent": round(loss, 2),
        "ndvi_threshold_used": (ndvi_thresh if ndvi_thresh is not None else "Otsu")
    }
    save_report(report)

    # change = forest at t0 and not at t1
    change_mask = (mask0 & (~mask1)).astype(np.uint8)
    save_preview_change(change_mask)

    # Save masks as simple GeoTIFF using past's profile
    with rasterio.open(red_past) as src:
        profile = src.profile
        profile.update(count=1, dtype="uint8")
        with rasterio.open("outputs/forest_mask_past.tif", "w", **profile) as dst:
            dst.write(mask0.astype("uint8"), 1)
        with rasterio.open("outputs/forest_mask_present.tif", "w", **profile) as dst:
            dst.write(mask1.astype("uint8"), 1)
        with rasterio.open("outputs/deforest_mask.tif", "w", **profile) as dst:
            dst.write(change_mask, 1)

    return report
