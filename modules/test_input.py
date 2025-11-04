"""
test_input.py
--------------
Reads all .xml or .txt files from:
    input/reference_and_expected_results/
Cleans their XML content and stores them as a JSON array in:
    throughput/test_throughput.json

Design follows strict Separation of Concerns:
    • get_paths()              – defines input/output locations
    • clean_xml_content()      – cleans raw XML text
    • read_all_input_files()   – reads and cleans all XML/TXT files dynamically
    • save_to_json()           – writes combined JSON output
    • process_test_input()     – orchestrates the workflow
"""

import json
import re
import html
from pathlib import Path
from paths import INPUT_DIR, THROUGHPUT_DIR

# ---------- CONFIGURATION LAYER ----------

def get_paths() -> tuple[Path, Path]:
    """Return input folder and output JSON file path."""
    input_folder = INPUT_DIR / "reference_and_expected_results"    # Correct data/input folder
    output_file = THROUGHPUT_DIR / "test_throughput.json"          # Correct data/throughput folder
    return input_folder, output_file


# ---------- CLEANING LAYER ----------
import re
import html

def clean_xml_content(raw: str) -> str:
    """
    Cleans XML text from .xml or .txt files before saving to JSON.
    - Removes BOMs, leading/trailing quotes, commas, newlines.
    - Fixes unquoted XML attributes.
    - Ensures valid XML starts with '<'.
    """
    if not isinstance(raw, str):
        return ""

    # Step 1 — remove BOM and whitespace
    text = raw.strip().replace("\ufeff", "").replace("\r", "").replace("\n", " ")

    # Step 2 — remove *leading and trailing quotes*
    text = re.sub(r"^'+|^\"+|'+$|\"+$", "", text.strip())

    # Step 3 — remove Excel-style artifacts
    text = text.replace('""', '"').replace(",", "")
    text = text.encode("utf-8").decode("unicode_escape")
    text = html.unescape(text)

    # Step 4 — fix unquoted attributes (e.g., version=1.0 → version="1.0")
    text = re.sub(r'(\w+)=([\w:\-\.\/]+)', r'\1="\2"', text)

    # Step 5 — normalize spaces and keep only actual XML
    text = re.sub(r"\s+", " ", text)
    start = text.find("<")
    if start != -1:
        text = text[start:]

    return text.strip()

# ---------- FILE READING LAYER ----------

def read_all_input_files(folder_path: Path) -> list[dict]:
    """Read and clean all .xml or .txt files in the folder; return list of {title, content} dicts."""
    print(f"📂 Scanning folder: {folder_path}")
    if not folder_path.exists():
        raise FileNotFoundError(f"❌ Folder not found: {folder_path}")

    input_files = list(folder_path.glob("*.xml")) + list(folder_path.glob("*.txt"))
    if not input_files:
        raise FileNotFoundError(f"⚠️ No .xml or .txt files found in: {folder_path}")

    records = []
    for file_path in input_files:
        print(f"📖 Reading: {file_path.name}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            cleaned_content = clean_xml_content(content)       # ✅ Clean XML before saving
            title = file_path.stem                             # Filename without extension
            records.append({"title": title, "content": cleaned_content})
        except Exception as e:
            print(f"⚠️ Skipping {file_path.name}: {e}")
            continue

    print(f"✅ Read and cleaned {len(records)} XML/TXT file(s).")
    return records


# ---------- FILE WRITING LAYER ----------

def save_to_json(data: list[dict], output_path: Path) -> None:
    """Save cleaned XML data to JSON file."""
    print(f"💾 Writing JSON output: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"✅ JSON file created successfully with {len(data)} record(s).")


# ---------- ORCHESTRATION LAYER ----------

def process_test_input() -> None:
    """Main orchestration: read, clean, and write test throughput JSON."""
    input_folder, output_path = get_paths()
    records = read_all_input_files(input_folder)
    save_to_json(records, output_path)


# ---------- SCRIPT ENTRY POINT ----------

if __name__ == "__main__":
    process_test_input()