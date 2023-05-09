import logging
import os

from tools.triage.utils.extraction import ExtractorException, ExtractorInterface
from tools.triage.utils.filesystem import FileSystemHelpers, FileSystemHelpersException


class ActionExtractArchive:
    def __init__(self, extractors: list[ExtractorInterface]):
        self.extractors = extractors
        self.logger = logging.getLogger(__name__)

    def file_action(self, full_path):
        archive_path, destination_path = self._get_paths(full_path)
        try:
            for extractor in self.extractors:
                if extractor.can_handle_file(archive_path):
                    next_path = extractor.extract(archive_path, destination_path)
                    self._clean_up_old_archive(archive_path)
                    return next_path
            return None
        except ExtractorException as e:
            self._handle_error(f"There was a problem during the extraction of {full_path} due to error {e}")
        except FileSystemHelpersException as e:
            self._handle_error(f"There was a problem during cleanup of {archive_path} due to {e}", is_fatal=False)

    def _get_paths(self, full_path):
        pathparts = full_path.split("/")
        name = os.path.basename(full_path)
        path = os.path.dirname(full_path)
        if len(path) == 0 or len(name) == 0:
            self._handle_error(
                f"Could not calculate a path or name from {full_path}, name:{name}, path:{path}, pathparts:{pathparts}"
            )
        return os.path.join(path, name), os.path.join(path, "extracted_" + name.replace(".", "_"))

    def _clean_up_old_archive(self, archive_path):
        FileSystemHelpers.remove(archive_path)

    def _handle_error(self, message, is_fatal=True):
        self.logger.error(message)
        if is_fatal:
            raise ActionExtractArchiveException(message)


class ActionExtractArchiveException(Exception):
    """If there is an unrecoverable error during archive extraction, this error is raised"""

    pass
