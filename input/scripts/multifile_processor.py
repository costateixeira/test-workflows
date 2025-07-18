import os
import sys
import xml.etree.ElementTree as ET

def parse_multifile(file_path):
    """Parse the multifile XML and return a dictionary of files and their content."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        files = {}
        for file_element in root.findall("file"):
            path = file_element.get("path")
            content = file_element.text or ""
            files[path] = content.strip()
        return files
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}", file=sys.stderr)
        sys.exit(1)

def save_files(files, interactive=False):
    """Save files to disk, creating directories as needed."""
    for file_path, content in files.items():
        try:
            # Ensure the directory exists (if there is a directory component)
            directory = os.path.dirname(file_path)
            if directory:  # Only create directories if the directory path is not empty
                os.makedirs(directory, exist_ok=True)
            
            # Write the file content
            with open(file_path, "w") as f:
                f.write(content)
            print(f"Saved: {file_path}")
        except PermissionError:
            print(f"Permission denied: Unable to create directory for {file_path}. Check your permissions.", file=sys.stderr)
        except OSError as e:
            print(f"OS error: Unable to create directory or save file {file_path}. Error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)

def main():
    """Main entry point for the script."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <multifile.xml>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    files = parse_multifile(file_path)

    print("The following files will be updated or created:")
    for file_path in files.keys():
        print(f"  - {file_path}")

    confirm = input("Do you want to proceed? (yes/no): ").strip().lower()
    if confirm not in ["yes", "y"]:
        print("Aborted.")
        sys.exit(0)

    save_files(files, interactive=True)

if __name__ == "__main__":
    main()