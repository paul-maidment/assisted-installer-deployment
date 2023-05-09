"""File path recursor module"""
import logging
import os
import re

from tools.triage.utils.filesystem import FileSystemHelpers, FileSystemHelpersException


class FilePathRecursor:
    """Recurses a filesystem and calls functions when files are encountered"""

    def __init__(
        self, on_file_action_class, recurse_after_action: bool, path_match_regex=None, path_error_is_fatal=True
    ):
        """Constructor"""
        self.on_file_action_class = on_file_action_class
        self.recurse_after_action = recurse_after_action
        self.path_match_regex = path_match_regex
        self.path_error_is_fatal = path_error_is_fatal
        self.logger = logging.getLogger(__name__)

    def _handle_error(self, message, is_fatal=True):
        self.logger.error(message)
        if is_fatal:
            raise FilePathRecursorException(message)

    def recurse(self, path: str):
        """Recursive function to navigate a file tree"""
        try:
            # just in case there is a file where we do not expect one, do not process it.
            if not FileSystemHelpers.isdir(path):
                return
            entries = FileSystemHelpers.listdir(path)
        except FileSystemHelpersException as e:
            self._handle_error(f"Unable to list directory {path} due to error {e}", self.path_error_is_fatal)

        for entry in entries:
            full_path = os.path.join(path, entry)
            FileSystemHelpers.assert_path_exists(full_path)
            if os.path.isdir(full_path):
                self.recurse(full_path)
            elif os.path.isfile(full_path):
                # This allows us to recurse a tree and perform an action on only the files that match the path_match_regex.
                # If the path_match_regex is not set (None) then the action will be performed on every file.
                if self.path_match_regex is None or re.search(self.path_match_regex, full_path):
                    new_path = self.on_file_action_class.file_action(full_path)
                    if new_path is not None and self.recurse_after_action:
                        self.recurse(new_path)


class FilePathRecursorException(Exception):
    "Raised when an error occurs during recursion of the filepath"
    pass
