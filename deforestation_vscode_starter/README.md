# 🌳 Deforestation % (VS Code Starter)

Compute **remaining forest %** and **deforestation %** between two time windows using:
1) **Google Earth Engine (GEE)** with Sentinel‑2 NDVI (recommended)
2) **Local GeoTIFF fallback** (if you already have RED/NIR rasters)

## 🚀 Quick Start (VS Code)
1. **Python 3.10+** recommended. Open this folder in VS Code.
2. Create venv:
   ```bash
   python -m venv .venv
   .venv/Scripts/activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   ```
3. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
4. **GEE auth (first time only):**
   ```bash
   earthengine authenticate
   ```
   - A browser opens → sign in with Google → paste the code back in terminal.
   - Then test:
     ```bash
     earthengine ls
     ```
5. Edit **config.yaml** (set your AOI and date windows).
6. Run (GEE mode, default):
   ```bash
   python -m src.cli --mode gee
   ```
   or Local mode (if you have GeoTIFFs):
   ```bash
   python -m src.cli --mode local --red-past path.tif --nir-past path.tif --red-present path.tif --nir-present path.tif
   ```

Outputs land here:
- `outputs/report.json` & `outputs/summary.csv`
- `outputs/forest_mask_past.tif`, `outputs/forest_mask_present.tif`, `outputs/deforest_mask.tif`
- `outputs/preview_change.png`

## 🛠️ VS Code One‑Click
Use **Run and Debug → “Run GEE pipeline”** (or “Run Local pipeline”) — preconfigured in `.vscode/launch.json`.

## 📁 Files
- `src/gee_pipeline.py` → Sentinel‑2 composites, NDVI, masks, area & %
- `src/local_pipeline.py` → Raster NDVI, Otsu/fixed threshold, %
- `src/utils.py` → IO helpers, % formula, simple plot
- `src/cli.py` → CLI wrapper
- `config.yaml` → your settings (dates, thresholds, AOI)
- `aoi.geojson` → put your polygon here (WGS84 lon/lat)

## ⚠️ Notes
- Keep **same‑season** windows to reduce seasonal bias.
- Sentinel‑2 10 m pixel → 0.01 ha/pixel (handled automatically).
- This is a solid baseline; for higher accuracy later, swap NDVI with a trained U‑Net.

