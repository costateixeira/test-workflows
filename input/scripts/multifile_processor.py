import os
import sys
import subprocess
import xml.etree.ElementTree as ET


def is_git_repo():
    """
    Check if the current directory is inside a Git repository.

    Returns:
        bool: True if inside a Git repository, False otherwise.
    """
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def is_git_clean():
    """
    Check if the Git repository is in a clean state (no uncommitted changes).

    Returns:
        bool: True if the repo is clean, False otherwise.
    """
    try:
        result = subprocess.run(["git", "status", "--porcelain"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return result.stdout.strip() == b""
    except subprocess.CalledProcessError:
        return False


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
        print(f"Error parsing XML: {e}", file=sys.stderr)
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
        try:
            with open(file_path, "w") as f:
                f.write(file["content"])
            print(f"Saved: {file_path}")
        except Exception as e:
            print(f"Error saving file {file_path}: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python multifile_processor.py <path_to_multifile.xml> [--non-interactive]")
        sys.exit(1)

    xml_path = sys.argv[1]
    interactive = "--non-interactive" not in sys.argv

    # Check if inside a Git repository
    if not is_git_repo():
        print("Error: This script must be run inside a Git repository.", file=sys.stderr)
        sys.exit(1)

    # Check for a clean Git state if in interactive mode
    if interactive and not is_git_clean():
        print("Warning: The Git repository is not in a clean state (uncommitted changes detected).")
        confirm = input("Do you want to proceed anyway? (yes/no): ").strip().lower()
        if confirm not in ["yes", "y"]:
            print("Operation cancelled.")
            sys.exit(1)

    # Check if the multifile XML file exists
    if not os.path.exists(xml_path):
        print(f"Error: File not found: {xml_path}", file=sys.stderr)
        sys.exit(1)

    # Parse and save the files
    files = parse_multifile_xml(xml_path)
    save_files(files, interactive=interactive)


if __name__ == "__main__":
    main()