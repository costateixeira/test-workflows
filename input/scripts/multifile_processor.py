"""
Multifile XML Processor for Git Operations

This module provides functionality to process multifile XML configurations
that define operations on multiple files within a Git repository. It handles
parsing XML configurations, validating Git repository status, and coordinating
file operations across the repository.

The processor is designed to work with XML files that specify:
- Repository information and branch details
- Lists of files to process
- Commit messages and metadata
- Processing instructions for batch operations

Author: WHO SMART Guidelines Team
"""

import logging
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from typing import List, Optional


class MultifileProcessor:
    """
    Processes multifile XML configurations for batch Git operations.
    
    This class handles XML files that define operations to be performed
    on multiple files within a Git repository. It provides functionality
    for parsing XML configurations, validating repository state, and
    coordinating file processing operations.
    
    Attributes:
        xml_path (str): Path to the multifile XML configuration
        repo (str): Repository information from XML
        branch (str): Target branch for operations
        commit_message (str): Commit message for batch operations
        files (List[str]): List of files to process
    """
    
    def __init__(self, xml_path: str):
        """
        Initialize the multifile processor.
        
        Args:
            xml_path: Path to the XML configuration file
        """
        self.xml_path = xml_path
        self.repo: Optional[str] = None
        self.branch: Optional[str] = None
        self.commit_message: Optional[str] = None
        self.files: List[str] = []

    def is_git_repo(self) -> bool:
        """Check if the current directory is part of a Git repository."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def get_current_branch(self):
        """Get the current Git branch."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                stdout=subprocess.PIPE,
                check=True
            )
            return result.stdout.decode().strip()
        except subprocess.CalledProcessError:
            return None

    def switch_to_branch(self):
        """Switch to the branch specified in the XML or create it if it doesn't exist."""
        current_branch = self.get_current_branch()
        if self.branch != current_branch:
            logging.getLogger(self.__class__.__name__).info(f"Current branch is '{current_branch}', but XML specifies branch '{self.branch}'.")
            confirm = input(f"Do you want to switch to branch '{self.branch}'? (yes/no): ").strip().lower()
            if confirm in ["yes", "y"]:
                branches = subprocess.run(
                    ["git", "branch"],
                    stdout=subprocess.PIPE
                ).stdout.decode()
                if self.branch not in branches.split():
                    subprocess.run(["git", "checkout", "-b", self.branch], check=True)
                else:
                    subprocess.run(["git", "checkout", self.branch], check=True)
                logging.getLogger(self.__class__.__name__).info(f"Switched to branch '{self.branch}'.")

    def parse_multifile_xml(self):
        """Parse multifile.xml and extract metadata and file contents."""
        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
            self.repo = root.attrib.get("repo")
            self.branch = root.attrib.get("branch", "main")
            meta = root.find("meta")
            if meta is not None:
                commit_elem = meta.find("commit")
                if commit_elem is not None:
                    self.commit_message = commit_elem.text.strip()
            self.files = []
            for file_elem in root.findall("file"):
                path = file_elem.get("path")
                diff_format = file_elem.get("diff")
                content = file_elem.text.strip() if file_elem.text else ""
                self.files.append({"path": path, "content": content, "diff": diff_format})
        except ET.ParseError as e:
            logging.getLogger(self.__class__.__name__).info(f"Error parsing XML: {e}", file=sys.stderr)
            sys.exit(1)

    def apply_changes(self):
        """Apply the changes specified in the XML to the repository."""
        for file in self.files:
            path = file["path"]
            diff = file["diff"]
            content = file["content"]
            if diff:
                try:
                    with open("temp.diff", "w") as temp_diff:
                        temp_diff.write(content)
                    subprocess.run(["git", "apply", "temp.diff"], check=True)
                    os.remove("temp.diff")
                    logging.getLogger(self.__class__.__name__).info(f"Applied diff to: {path}")
                except Exception as e:
                    logging.getLogger(self.__class__.__name__).info(f"Error applying diff to {path}: {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                directory = os.path.dirname(path)
                if directory:
                    os.makedirs(directory, exist_ok=True)
                with open(path, "w") as f:
                    f.write(content)
                logging.getLogger(self.__class__.__name__).info(f"Updated file: {path}")

    def run(self):
        """Main execution method."""
        if not self.is_git_repo():
            logging.getLogger(self.__class__.__name__).info("Error: This script must be run inside a Git repository.", file=sys.stderr)
            sys.exit(1)

        if not os.path.exists(self.xml_path):
            logging.getLogger(self.__class__.__name__).info(f"Error: File not found: {self.xml_path}", file=sys.stderr)
            sys.exit(1)

        self.parse_multifile_xml()
        self.switch_to_branch()
        self.apply_changes()

        diff_choice = input("Would you like to see a diff of the applied changes? (yes/no): ").strip().lower()
        if diff_choice in ["yes", "y"]:
            subprocess.run(["git", "diff"])

        commit_choice = input("Would you like to commit the changes? (yes/no): ").strip().lower()
        if commit_choice in ["yes", "y"]:
            if self.commit_message:
                use_commit_message = input(
                    f"Use commit message from <commit/>? '{self.commit_message}' (yes/no): "
                ).strip().lower()
                if use_commit_message in ["yes", "y"]:
                    subprocess.run(["git", "commit", "-am", self.commit_message], check=True)
                else:
                    custom_message = input("Enter your commit message: ").strip()
                    subprocess.run(["git", "commit", "-am", custom_message], check=True)
            else:
                custom_message = input("Enter your commit message: ").strip()
                subprocess.run(["git", "commit", "-am", custom_message], check=True)

        push_choice = input("Would you like to push the changes? (yes/no): ").strip().lower()
        if push_choice in ["yes", "y"]:
            try:
                subprocess.run(["git", "push", "--set-upstream", "origin", self.branch], check=True)
            except subprocess.CalledProcessError as e:
                logging.getLogger(self.__class__.__name__).info(f"Error pushing changes: {e}", file=sys.stderr)
                sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.getLogger(self.__class__.__name__).info("Usage: python multifile_processor.py <path_to_multifile.xml>")
        sys.exit(1)
    xml_path = sys.argv[1]
    processor = MultifileProcessor(xml_path)
    processor.run()
