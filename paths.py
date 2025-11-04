# paths.py
# -----------------------------------------------------------
# Centralized definition of project directories and file paths
# Ensures consistent, portable path references across modules
# -----------------------------------------------------------

from pathlib import Path  # modern and cross-platform path handling

# 🏗️ Get absolute path to the project root (the folder that contains main.py)
BASE_DIR: Path = Path(__file__).resolve().parent

# 📂 Define key project directories relative to BASE_DIR
ASSETS_DIR: Path = BASE_DIR / "assets"          # folder for static files, images, etc.
DATA_DIR: Path = BASE_DIR / "data"              # root folder for test data
INPUT_DIR: Path = DATA_DIR / "input"            # input XML/JSON test data
OUTPUT_DIR: Path = DATA_DIR / "output"          # regression results
THROUGHPUT_DIR: Path = DATA_DIR / "throughput"  # performance test results
MODULES_DIR: Path = BASE_DIR / "modules"        # holds all code modules
LOGS_DIR: Path = BASE_DIR / "logs"              # folder for logs

# 🧾 Define key file paths
LOG_FILE: Path = LOGS_DIR / "regression_log.txt"

# 🧱 Automatically create directories if missing
for directory in [ASSETS_DIR, INPUT_DIR, OUTPUT_DIR, THROUGHPUT_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# 🧩 Optional sanity check when running directly
if __name__ == "__main__":
    print("Base directory:", BASE_DIR)
    print("Input directory:", INPUT_DIR)
    print("Output directory:", OUTPUT_DIR)
    print("Log file:", LOG_FILE)
