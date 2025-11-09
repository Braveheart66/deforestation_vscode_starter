# Drone-AI Deforestation Monitor

Drone-based AI System for monitoring deforestation patterns using Sentinel-2, Google Earth Engine, and drone NDVI inputs. Provides NDVI generation, mask comparison, and interactive visualizations.

Features
- AOI-based NDVI extraction (past vs present)
- Cloud filtering and NDVI thresholding
- Forest change quantification and summary reports
- Interactive folium/leafmap swipe and static map fallbacks
- Optional drone GeoTIFF ingestion

Quickstart (Windows)
1. Install dependencies:
   - Python >= 3.9
   - pip install -r requirements.txt
2. Run locally:
   - python -m streamlit run src/app.py

Repository suggestions
- Name: drone-deforestation-monitor
- .gitignore: exclude venv, outputs, .vscode, __pycache__

License
- MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
... (standard MIT text) ...