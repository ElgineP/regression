"""
reference.py
-------------
Reads 'Test_Builder.xls' from the input folder,
extracts the first 5 columns, and saves them as a JSON file
in the 'throughput' folder.

Design follows strict Separation of Concerns:
    • get_paths()          – defines project file locations
    • read_input_file()    – handles file reading
    • clean_xml_content()  – NEW: Cleans up unquoted XML attributes (FIX for parsing error)
    • select_columns()     – filters DataFrame and applies cleaning
    • save_to_json()       – writes JSON output
    • process_reference()  – orchestrates workflow

Dependencies:
    pip install pandas xlrd
"""

import re
import html
import pandas as pd
from pathlib import Path
from paths import INPUT_DIR  # imports the correct data/input/ folder

# ---------- CONFIGURATION LAYER ----------

def get_paths() -> tuple[Path, Path]:
    """Define and return input and output file paths."""
    base_path = Path(__file__).parent
    input_file = base_path / "input" / "Test_Builder.xls"           # Input Excel file
    output_file = base_path / "throughput" / "Reference_Output.json"  # Output JSON file
    return input_file, output_file


# ---------- FILE READING LAYER ----------

def read_input_file(file_path: Path) -> pd.DataFrame:
    """Read Excel file and return as DataFrame."""
    print(f"📂 Reading Excel file: {file_path}")
    try:
        df = pd.read_excel(file_path, engine="xlrd")                # Read .xls format using xlrd
        print(f"✅ Loaded {len(df.columns)} columns and {len(df)} rows.")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"❌ File not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"⚠️ Error reading Excel file: {e}")


# ---------- XML CLEANING UTILITY (FIX APPLIED HERE) ----------

def clean_xml_content(raw: str) -> str:
    """
    Cleans XML text from .xml or .txt files before saving to JSON.
    - Removes BOMs, leading/trailing quotes, commas, newlines.
    - Fixes unquoted XML attributes (e.g., version=1.0 → version="1.0").
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
    # ⭐ THIS IS THE CRITICAL LINE THAT RESOLVES THE PARSING ERROR ⭐
    text = re.sub(r'(\w+)=([\w:\-\.\/]+)', r'\1="\2"', text)

    # Step 5 — normalize spaces and keep only actual XML
    text = re.sub(r"\s+", " ", text)
    start = text.find("<")
    if start != -1:
        text = text[start:]

    return text.strip()


# ---------- DATA PROCESSING LAYER ----------

def select_columns(df: pd.DataFrame, num_cols: int = 5) -> pd.DataFrame:
    """Select only the first N columns, clean XML in 'Full MX-Message:'."""
    if df.empty:
        raise ValueError("⚠️ Input DataFrame is empty.")
    if len(df.columns) < num_cols:
        print(f"⚠️ Warning: File has only {len(df.columns)} columns, not {num_cols}.")

    subset = df.iloc[:, :num_cols].copy()

    # ⭐ APPLY THE NEW CLEANING FUNCTION HERE ⭐
    if "Full MX-Message:" in subset.columns:
        subset["Full MX-Message:"] = subset["Full MX-Message:"].apply(clean_xml_content)

    return subset


# ---------- FILE WRITING LAYER ----------

def save_to_json(df: pd.DataFrame, output_path: Path) -> None:
    """Save DataFrame to a JSON file."""
    print(f"💾 Writing data to JSON: {output_path}")
    json_data = df.to_json(orient="records", indent=4)               # Convert DataFrame to JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)            # Ensure 'throughput' folder exists
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json_data)
    print(f"✅ Successfully saved JSON with {len(df)} records.")


# ---------- ORCHESTRATION LAYER ----------

def process_reference():
    file_path = INPUT_DIR / "Test_Builder.xls"
    print(f"📂 Reading Excel file: {file_path}")

    if not file_path.exists():
        raise FileNotFoundError(f"❌ File not found: {file_path}")

# ---------- SCRIPT ENTRY POINT ----------

if __name__ == "__main__":
    process_reference()