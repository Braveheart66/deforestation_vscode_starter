import streamlit as st
import os, sys, tempfile, time, asyncio
from datetime import date
import numpy as np, rasterio, folium, matplotlib.pyplot as plt
from PIL import Image

# --- Patch async loop for tileserver ---
try: asyncio.get_event_loop()
except RuntimeError: asyncio.set_event_loop(asyncio.new_event_loop())

# --- Imports ---
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import gee_pipeline
import geemap.foliumap as geemap_folium

# Optional leafmap swipe support
try:
    import leafmap.foliumap as leafmap
    HAS_LEAFMAP = True
except Exception:
    HAS_LEAFMAP = False

# --- Helper functions ---
def safe_makedirs(p): os.makedirs(p, exist_ok=True)
def save_temp_file(f,suffix):
    tmp = tempfile.NamedTemporaryFile(delete=False,suffix=suffix)
    tmp.write(f.read()); tmp.flush(); tmp.close(); return tmp.name
def write_png_thumb(tiff,out):
    with rasterio.open(tiff) as src:
        band = src.read(1).astype(float)
        band = np.nan_to_num(band)
        mn,mx = np.nanmin(band), np.nanmax(band)
        arr = (band-mn)/(mx-mn+1e-9)
        rgb = (plt.get_cmap("RdYlGn")(arr)[:,:,:3]*255).astype(np.uint8)
        Image.fromarray(rgb).save(out)
def add_raster(m,tiff,name):
    try:
        m.add_raster(tiff,palette=["red","yellow","green"],layer_name=name,opacity=0.8)
    except Exception:
        with rasterio.open(tiff) as src:
            arr = src.read(1)
            arr = np.nan_to_num(arr)
            arr = (arr-arr.min())/(arr.max()-arr.min()+1e-9)
            rgb = (plt.get_cmap("RdYlGn")(arr)[:,:,:3]*255).astype(np.uint8)
            png=tempfile.NamedTemporaryFile(delete=False,suffix=".png").name
            Image.fromarray(rgb).save(png)
            bounds=[[src.bounds.bottom,src.bounds.left],[src.bounds.top,src.bounds.right]]
            folium.raster_layers.ImageOverlay(image=png,bounds=bounds,name=name,opacity=0.85).add_to(m)

# --- Page style ---
st.set_page_config(page_title="🌳 Drone-AI Neo-Forest Console",layout="wide",page_icon="🛰️")
st.markdown("""
<style>
body{background:linear-gradient(135deg,#000 0%,#021 60%,#043 100%);color:#e6f7ee;}
h1,h2{color:#39FF14;text-shadow:0 0 12px #00ffcc;}
.metric-value{font-size:32px;font-weight:700;}
.legend-bar{height:12px;background:linear-gradient(to right,#e74c3c,#f1c40f,#2ecc71);border-radius:6px;}
.legend-labels{display:flex;justify-content:space-between;color:#ccc;font-size:0.85rem;}
</style>
""",unsafe_allow_html=True)
st.title("🌳 **Drone-AI Neo-Forest Console**")
st.caption("Dual-panel NDVI visualization and deforestation analytics powered by Google Earth Engine + Drone AI.")
st.divider()

# --- Inputs ---
col1,col2=st.columns(2)
with col1:
    aoi_file=st.file_uploader("📁 Upload AOI GeoJSON",type=["geojson"])
    start_past=st.date_input("Past Start",date(2019,1,1))
    end_past=st.date_input("Past End",date(2019,3,31))
    ndvi_thresh=st.slider("🌿 NDVI Threshold",0.2,0.8,0.4,0.05)
    drone_file=st.file_uploader("🚁 Drone NDVI GeoTIFF (optional)",type=["tif","tiff"])
with col2:
    start_present=st.date_input("Present Start",date(2024,1,1))
    end_present=st.date_input("Present End",date(2024,3,31))
    cloud_prob=st.slider("☁️ Cloud Probability (%)",0,100,60,5)
    run_btn=st.button("🚀 Run Analysis",use_container_width=True)

st.divider()

# --- Run pipeline ---
if run_btn:
    if not aoi_file: st.warning("Upload AOI first."); st.stop()
    tmp_aoi=save_temp_file(aoi_file,".geojson")
    st.success("✅ AOI loaded.")

    progress=st.progress(0);status=st.empty()
    steps=["Initializing Earth Engine...","Fetching Sentinel-2...","Computing NDVI...","Generating Masks...","Comparing Areas...","Preparing Report..."]
    for i,s in enumerate(steps): status.info(s); progress.progress((i+1)/len(steps)); time.sleep(0.4)

    result=gee_pipeline.run(tmp_aoi,[str(start_past),str(end_past)],[str(start_present),str(end_present)],ndvi_thresh,cloud_prob)

    st.markdown("### 📊 Forest Change Summary")
    c1,c2,c3=st.columns(3)
    c1.metric("🌲 Past Forest",f"{result['forest_area_past_ha']:,} ha")
    c2.metric("🌳 Present Forest",f"{result['forest_area_present_ha']:,} ha")
    if result["change_type"]=="Loss":
        c3.metric("🔥 Deforestation",f"{result['change_percent']} % ↓")
    else:
        c3.metric("🌱 Reforestation",f"{result['change_percent']} % ↑")

    st.markdown("<div class='legend-bar'></div><div class='legend-labels'><span>Bare</span><span>Moderate</span><span>Healthy</span></div>",unsafe_allow_html=True)
    st.expander("📄 Full Report").json(result)
    # Display dataset source info
    st.markdown(
        f"""
        <div style='margin-top:10px; background:rgba(0,255,153,0.1); 
            border-left:4px solid #00ff99; padding:8px; border-radius:6px;'>
            <b>🛰️ Data Sources:</b><br>
            • Past NDVI → <span style='color:#00ffcc;'>{result.get('data_source_past','Unknown')}</span><br>
            • Present NDVI → <span style='color:#00ffcc;'>{result.get('data_source_present','Unknown')}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


    # --- Swipe visualization ---
    st.markdown("### 🛰️ NDVI Swipe Comparison (Past vs Present)")
    past_tif=os.path.join("outputs","forest_mask_past.tif")
    pres_tif=os.path.join("outputs","forest_mask_present.tif")

    if HAS_LEAFMAP:
        try:
            m=leafmap.Map(center=[26.85,80.95],zoom=9)
            if hasattr(leafmap,"set_default_center"): leafmap.set_default_center(26.85,80.95)
            m.split_map(left_layer=past_tif,right_layer=pres_tif,left_label="Past NDVI",right_label="Present NDVI")
            m.to_streamlit(width=1000,height=600)
        except Exception as e:
            st.warning(f"⚠️ Swipe map unavailable: {e}")
    else:
        st.warning("⚠️ Swipe map requires `leafmap`. Showing static fallback.")
        m=geemap_folium.Map(center=[26.85,80.95],zoom=9)
        if os.path.exists(past_tif): add_raster(m,past_tif,"Past NDVI")
        if os.path.exists(pres_tif): add_raster(m,pres_tif,"Present NDVI")
        m.add_layer_control(); m.to_streamlit(width=950,height=600)

    # --- NDVI histogram ---
    st.markdown("### 📈 NDVI Distribution")
    try:
        with rasterio.open(past_tif) as src: past=src.read(1).ravel()
        with rasterio.open(pres_tif) as src: pres=src.read(1).ravel()
        plt.figure(figsize=(6,3))
        plt.hist(past,bins=40,alpha=0.5,label="Past",color="red")
        plt.hist(pres,bins=40,alpha=0.5,label="Present",color="green")
        plt.legend(); plt.xlabel("NDVI"); plt.ylabel("Pixel Count")
        st.pyplot(plt.gcf())
    except Exception as e:
        st.info(f"Histogram unavailable: {e}")

    st.success("🌿 Visualization complete — scroll and explore!")
