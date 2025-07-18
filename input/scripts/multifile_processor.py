import os
import sys
import xml.etree.ElementTree as ET

def parse_multifile_xml(file_path):
    """
    Parse the multifile XML and return a list of files with their paths and contents.

    Args:
        file_path (str): The path to the multifile XML file.

    Returns:
        list: A list of dictionaries with keys 'path' and 'content'.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        files = []
        for file_elem in root.findall("file"):
            path = file_elem.get("path")
            content = file_elem.text.strip() if file_elem.text else ""
            files.append({"path": path, "content": content})

        return files
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        sys.exit(1)

def save_files(files, interactive=True):
    """
    Save the files to the appropriate paths.

    Args:
        files (list): A list of dictionaries with keys 'path' and 'content'.
        interactive (bool): If True, prompt the user for confirmation before saving.
    """
    if interactive:
        print("The following files will be updated or created:")
        for file in files:
            print(f"  - {file['path']}")

        confirm = input("Do you want to proceed? (yes/no): ").strip().lower()
        if confirm not in ["yes", "y"]:
            print("Operation cancelled.")
            return

    for file in files:
        file_path = file["path"]
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(file["content"])
        print(f"Saved: {file_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python multifile_processor.py <path_to_multifile.xml> [--non-interactive]")
        sys.exit(1)

    xml_path = sys.argv[1]
    interactive = "--non-interactive" not in sys.argv

    if not os.path.exists(xml_path):
        print(f"Error: File not found: {xml_path}")
        sys.exit(1)

    files = parse_multifile_xml(xml_path)
    save_files(files, interactive=interactive)

if __name__ == "__main__":
    main()