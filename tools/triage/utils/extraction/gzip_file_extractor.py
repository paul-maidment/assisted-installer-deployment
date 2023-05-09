"""Gzip file extractor module"""
import gzip
import logging
import os

from tools.triage.utils.extraction import ExtractorException, ExtractorInterface
from tools.triage.utils.filesystem import FileSystemHelpers, FileSystemHelpersException


class GzipFileExtractor(ExtractorInterface):
    """Responsible for handling the extraction of gzip format files"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def can_handle_file(self, filename: str) -> bool:
        """Overrides ExtractorInterface.can_handle_file()"""
        try:
            if not super().can_handle_file(filename):
                return False
            return filename.endswith(".gz")
        except ExtractorException as e:
            message = f"Unable to extract {filename} due to error {e}"
            self._handle_error(message)

    def extract(self, filename, destination_directory) -> str:
        """Overrides ExtractorInterface.extract()"""
        if not self.can_handle_file(filename):
            message = f"This extractor does not support the file {filename}"
            self._handle_error(message)
        content = self._extract_gzip_content(filename)
        try:
            FileSystemHelpers.mkdir(destination_directory)
            basename = os.path.basename(filename)
            extraction_filename = os.path.join(destination_directory, "extracted_" + basename.replace(".", "_"))
            FileSystemHelpers.write_file_content(extraction_filename, content)
            return destination_directory
        except FileSystemHelpersException as e:
            message = f"A filesystem error was encountered during extraction of {filename} to {destination_directory}, the error was {e}"
            self._handle_error(message)

    def _extract_gzip_content(self, filename):
        try:
            file_content = []
            with gzip.open(filename, "rb") as f:
                file_content = f.read()
            return file_content
        except Exception as e:
            self._handle_error(f"Could not extract gzip file {filename} due to error {e}")

    def _handle_error(self, message):
        """Handles an error if it occurs"""
        self.logger.error(message)
        raise GzipFileExtractorException(message)


class GzipFileExtractorException(ExtractorException):
    """If there is an unrecoverable error during archive extraction, this error is raised"""

    pass
