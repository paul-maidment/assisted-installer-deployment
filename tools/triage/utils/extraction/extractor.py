from tools.triage.utils.filesystem import FileSystemHelpers, FileSystemHelpersException

from .extractor_exception import ExtractorException


class ExtractorInterface:
    """Interface for extrator"""

    def can_handle_file(self, filename: str) -> bool:
        try:
            FileSystemHelpers.assert_path_exists(filename)
            return True
        except FileSystemHelpersException as e:
            raise ExtractorException(e)

    def extract(self, filename: str, destination_directory: str) -> str:
        try:
            FileSystemHelpers.assert_path_exists(filename)
        except FileSystemHelpersException as e:
            raise ExtractorException(e)
