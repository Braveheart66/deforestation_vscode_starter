from __future__ import annotations
import argparse, yaml, sys
from . import gee_pipeline, local_pipeline

def main():
    p = argparse.ArgumentParser(description="Deforestation % tool (GEE or Local)")
    p.add_argument("--mode", choices=["gee","local"], default="gee")
    p.add_argument("--config", default="config.yaml")
    # local mode args:
    p.add_argument("--red-past"); p.add_argument("--nir-past")
    p.add_argument("--red-present"); p.add_argument("--nir-present")
    args = p.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    if args.mode == "gee":
        aoi = cfg["aoi_path"]
        t0 = (cfg["past"]["start"], cfg["past"]["end"])
        t1 = (cfg["present"]["start"], cfg["present"]["end"])
        ndvi_thresh = float(cfg.get("ndvi_threshold", 0.4))
        cloud_prob = int(cfg.get("cloud_prob_threshold", 40))
        gee_pipeline.run(aoi, t0, t1, ndvi_thresh, cloud_prob)
    else:
        if not all([args.red_past, args.nir_past, args.red_present, args.nir_present]):
            print("Local mode requires --red-past --nir-past --red-present --nir-present", file=sys.stderr)
            sys.exit(2)
        ndvi_thresh = cfg.get("ndvi_threshold", None)
        minpix = int(cfg.get("min_patch_pixels", 25))
        morph = int(cfg.get("morph_radius", 1))
        local_pipeline.run(args.red_past, args.nir_past, args.red_present, args.nir_present,
                           ndvi_thresh, minpix, morph)

if __name__ == "__main__":
    main()
