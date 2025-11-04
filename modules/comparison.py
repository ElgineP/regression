"""
comparison.py
--------------
Compares XML structures from Reference_Output.json and test_throughput.json.

Features:
1. Robust XML cleaning (fixes unquoted attributes and extraneous quotes/text).
2. Simplified comparison output paths (strips XML namespaces for readability).
3. Skips specific XML tags that are expected to differ (e.g., BizMsgIdr, CreDt, MsgId).
4. Generates a 'Test result overview' header for quick status check.

Dependencies:
    pip install lxml
"""

import json
import re
import html
from pathlib import Path
from lxml import etree
from paths import THROUGHPUT_DIR, OUTPUT_DIR   # ✅ use centralized paths

# ---------- CONFIGURATION LAYER ----------

def get_paths() -> tuple[Path, Path, Path]:
    """Return correct JSON input/output paths using centralized path definitions."""
    ref_path = THROUGHPUT_DIR / "Reference_Output.json"
    test_path = THROUGHPUT_DIR / "test_throughput.json"
    output_file = OUTPUT_DIR / "comparison_results.txt"
    return ref_path, test_path, output_file


# ---------- FILE READING LAYER ----------

def load_json(file_path: Path) -> list:
    """Load JSON file into memory."""
    print(f"📂 Loading JSON: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- XML CLEANING LAYER ----------

def clean_xml_string(raw: str) -> str:
    """Cleans and normalizes XML text extracted from JSON."""
    if not isinstance(raw, str):
        return ""

    # Step 1 — unescape backslash sequences (e.g., \" or \\n)
    text = raw.encode("utf-8").decode("unicode_escape")

    # Step 2 — unescape HTML entities (&lt; &gt;)
    text = html.unescape(text)

    # Step 3 — remove commas and double quotes (Excel artifacts)
    text = text.replace(",", "")
    text = text.replace('""', '"').replace('"', '')

    # Step 4 — fix unquoted attributes (e.g., version=1.0 → version="1.0")
    text = re.sub(r'(\w+)=([\w:\-\.\/]+)', r'\1="\2"', text)

    # Step 5 — normalize spacing and isolate actual XML
    text = text.strip()
    declaration_end = text.find("?>")
    if declaration_end != -1:
        xml_declaration = text[:declaration_end + 2]
        content_start = text.find("<", declaration_end + 2)
        if content_start != -1:
            text = xml_declaration + text[content_start:]

    start = text.find("<")
    if start != -1:
        text = text[start:]

    return text


# ---------- XML COMPARISON LAYER ----------

IGNORED_TAGS = {"BizMsgIdr", "CreDt", "MsgId"}  # ✅ Tags intentionally ignored

def strip_namespace(tag: str) -> str:
    """Strips namespace {uri} from a qualified tag name."""
    return tag.split('}')[-1]


def parse_xml(xml_str: str):
    """Try to parse XML safely with clear error reporting."""
    try:
        return etree.fromstring(xml_str.encode("utf-8"))
    except Exception as e:
        snippet = xml_str[:100].replace('\n', ' ')
        raise ValueError(f"⚠️ Failed to parse XML: {e}\n  Snippet: {snippet}...")


def compare_xml(xml_a: etree._Element, xml_b: etree._Element) -> list[str]:
    """
    Compare two XML trees recursively, skipping ignored tags.
    Returns a list of mismatch messages (empty if identical).
    """
    diffs = []

    def recurse(elem_a, elem_b, path=""):
        tag_a_local = strip_namespace(elem_a.tag)
        tag_b_local = strip_namespace(elem_b.tag)
        current_path = f"{path}/{tag_a_local}"

        # Compare tag names
        if elem_a.tag != elem_b.tag:
            diffs.append(f"Tag mismatch at {path}: '{tag_a_local}' != '{tag_b_local}'")
            return

        # Skip ignored tags entirely
        if tag_a_local in IGNORED_TAGS:
            return

        # Compare text content
        text_a = (elem_a.text or "").strip()
        text_b = (elem_b.text or "").strip()
        if text_a != text_b:
            diffs.append(f"Value mismatch at {current_path}: '{text_a}' != '{text_b}'")

        # Compare attributes
        if elem_a.attrib != elem_b.attrib:
            diffs.append(f"Attribute mismatch at {current_path}: {elem_a.attrib} != {elem_b.attrib}")

        # Compare number of children
        children_a = list(elem_a)
        children_b = list(elem_b)
        if len(children_a) != len(children_b):
            diffs.append(f"Child count mismatch at {current_path}: {len(children_a)} != {len(children_b)}")

        # Recurse into child elements
        for a_child, b_child in zip(children_a, children_b):
            recurse(a_child, b_child, current_path)

    recurse(xml_a, xml_b)
    return diffs


# ---------- OUTPUT WRITING LAYER ----------

def write_results_to_file(output_path: Path, results: list[str]) -> None:
    """Write comparison results to a text file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    print(f"\n📝 Comparison results saved to: {output_path}")


# ---------- MAIN PROCESS LAYER ----------

def process_comparison() -> None:
    """Run the full XML comparison workflow."""
    ref_path, test_path, output_path = get_paths()
    ref_data = load_json(ref_path)
    test_data = load_json(test_path)

    overview_results = []
    detailed_results = []

    # Use dictionary for quick test record lookup
    test_data_map = {str(t.get("title", "")).strip(): t for t in test_data}

    for ref_entry in ref_data:
        ref_id = str(ref_entry.get("#", "")).strip()
        ref_name = ref_entry.get("Name", "N/A")
        ref_description = ref_entry.get("Description ", "N/A")  # note the space after Description
        ref_expected = ref_entry.get("Expected Results", "N/A")
        ref_xml_raw = ref_entry.get("Full MX-Message:", "")
        test_entry = test_data_map.get(ref_id)

        if test_entry:
            test_title = str(test_entry.get("title", "")).strip()
            test_xml_raw = test_entry.get("content", "")

            ref_xml_str = clean_xml_string(ref_xml_raw)
            test_xml_str = clean_xml_string(test_xml_raw)

            # 🧩 Improved Header with reference metadata
            header = (
                f"\n🧩 Test #{ref_id}: {ref_name}\n"
                f"📄 Description: {ref_description}\n"
                f"🎯 Expected Result snippet:\n{ref_expected}\n"
                f"🔁 Comparing Reference ↔ Test '{test_title}' ..."
            )
            print(header)
            detailed_results.append(header)

            try:
                ref_xml = parse_xml(ref_xml_str)
                test_xml = parse_xml(test_xml_str)
                diffs = compare_xml(ref_xml, test_xml)

                if not diffs:
                    msg = f"✅ Match OK for #{ref_id}\n"
                    print(msg)
                    detailed_results.append(msg)
                    overview_results.append(f"test {ref_id} pass")
                else:
                    msg = f"❌ Differences found for #{ref_id}:"
                    print(msg)
                    detailed_results.append(msg)
                    for d in diffs:
                        detailed_results.append(f"   - {d}")
                    detailed_results.append("")
                    overview_results.append(f"test {ref_id} fail")

            except ValueError as e:
                err = f"⚠️ XML parsing error for #{ref_id}: {e}\n"
                print(err)
                detailed_results.append(err)
                overview_results.append(f"test {ref_id} fail (XML Error)")

        else:
            warning = f"⚠️ No matching test record found for Reference #{ref_id}\n"
            print(warning)
            detailed_results.append(warning)
            overview_results.append(f"test {ref_id} fail (No Match)")

    # Combine results
    final_results = [
        "🔍 Starting XML comparison process...\n",
        "Test result overview\n",
        *overview_results,
        "",
        *detailed_results
    ]

    write_results_to_file(output_path, final_results)


# ---------- SCRIPT ENTRY POINT ----------

if __name__ == "__main__":
    process_comparison()
