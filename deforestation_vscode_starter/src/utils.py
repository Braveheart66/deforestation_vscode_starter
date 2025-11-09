from __future__ import annotations
import json, os
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def ensure_dirs():
    os.makedirs("outputs", exist_ok=True)

def save_report(report: Dict[str, Any]):
    ensure_dirs()
    with open("outputs/report.json", "w") as f:
        json.dump(report, f, indent=2)
    row = { 
        "region": report.get("region", "AOI"),
        "t0_start": report["past_window"][0],
        "t0_end": report["past_window"][1],
        "t1_start": report["present_window"][0],
        "t1_end": report["present_window"][1],
        "total_area_ha": report["total_area_ha"],
        "forest_area_past_ha": report["forest_area_past_ha"],
        "forest_area_present_ha": report["forest_area_present_ha"],
        "remaining_percent": report["remaining_percent"],
        "deforestation_percent": report["deforestation_percent"],
        "ndvi_threshold_used": report["ndvi_threshold_used"],
    }
    df = pd.DataFrame([row])
    df.to_csv("outputs/summary.csv", index=False)

def percent_from_areas(area_past_ha: float, area_present_ha: float) -> Tuple[float,float]:
    if area_past_ha <= 0:
        return 0.0, 0.0
    remaining = (area_present_ha / area_past_ha) * 100.0
    loss = ((area_past_ha - area_present_ha) / area_past_ha) * 100.0
    return remaining, loss

def save_preview_change(mask_loss: np.ndarray, title: str = "Deforestation (t0→t1)"):
    ensure_dirs()
    # simple visualization: show loss mask
    plt.figure()
    plt.imshow(mask_loss, interpolation="nearest")
    plt.title(title)
    plt.axis("off")
    plt.savefig("outputs/preview_change.png", bbox_inches="tight", dpi=150)
    plt.close()
