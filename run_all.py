import os
import subprocess
import sys

# make sure the folders exist (Git does not keep empty folders)
for folder in ["data/raw", "data/clean", "models_saved"]:
    os.makedirs(folder, exist_ok=True)

steps = [
    "src/ingest/openaq_locations.py",      # list of stations
    "src/ingest/download_daily.py",        # 18 daily files, saved untouched
    "src/cleaning/build_clean.py",         # flag bad days, never fill
    "src/cleaning/make_stations_file.py",  # station positions for the map
    "models/pooled_model.py",              # model comparison table
]

for step in steps:
    print("\n=== Running", step)
    result = subprocess.run([sys.executable, step])
    if result.returncode != 0:
        sys.exit(f"Stopped: {step} failed")

print("\nDone. Start the app with: streamlit run app/Home.py")