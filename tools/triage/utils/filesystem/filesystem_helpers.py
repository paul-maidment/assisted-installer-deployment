import logging
import os


class FileSystemHelpers:
    @staticmethod
    def _handle_error(message):
        logger = logging.getLogger(__name__)
        logger.error(message)
        raise FileSystemHelpersException(message)

    @staticmethod
    def isdir(path: str):
        return os.path.isdir(path)

    @staticmethod
    def listdir(path: str):
        try:
            entries = os.listdir(path)
            return entries
        except Exception as e:
            raise FileSystemHelpers._handle_error(f"Fatal: Could not list directory {path} due to exception {e}")

    @staticmethod
    def assert_path_exists(path):
        if not os.path.exists(path):
            FileSystemHelpers._handle_error(f"The specified path {path} does not exist.")

    @staticmethod
    def does_path_exist(path) -> bool:
        return os.path.exists(path)

    @staticmethod
    def mkdir(path):
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except Exception as e:
                FileSystemHelpers._handle_error(f"Could not create directory {path} due to error {e}")

    @staticmethod
    def get_current_user_directory():
        try:
            return os.path.expanduser("~")
        except Exception as e:
            FileSystemHelpers._handle_error(f"Could not determine user directory directory due to error {e}")

    @staticmethod
    def remove(path):
        FileSystemHelpers.assert_path_exists(path)
        try:
            os.remove(path)
        except Exception as e:
            FileSystemHelpers._handle_error(f"Could not remove path {path} due to error {e}")

    @staticmethod
    def write_file_content(filename, content):
        try:
            with open(filename, "wb") as out:
                out.write(content)
        except Exception as e:
            FileSystemHelpers._handle_error(f"Could not write file content to {filename} due to error {e}")

    @staticmethod
    def load_file_content(filename):
        try:
            with open(filename, "rb") as file:
                return file.read()
        except Exception as e:
            FileSystemHelpers._handle_error(f"Could not read file content from {filename} due to error {e}")


class FileSystemHelpersException(Exception):
    """If there is an unrecoverable error during a filesystem operation, this error is raised"""

    pass
