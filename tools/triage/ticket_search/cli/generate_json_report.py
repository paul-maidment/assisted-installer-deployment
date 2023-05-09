"""Module for command line utility to fetch a single triage ticket"""
import json
import logging
import os
import sys

from command import Command
from workflow_data import WorkflowData

from tools.triage.ticket_search.settings import DATA_DIRECTORY, REPORT_OUTPUT_FILE
from tools.triage.utils.filesystem import FileSystemHelpers


class GenerateJSONReportException(Exception):
    pass


class GenerateJSONReport(Command):
    """Responsible for fetching a single ticket for a triage issue"""

    def __init__(self):
        """Constructor"""
        self.args = []
        self.unknown_args = []
        self.logger = logging.getLogger(__name__)

    def get_command_key(self) -> str:
        return "generate_json_report"

    def get_friendly_name(self) -> str:
        return "Generate JSON report"

    def run(self, workflow_data: "WorkflowData") -> "WorkflowData":
        """This runs the command"""
        self.workflow_data = workflow_data
        self.report = workflow_data.copy()
        try:
            matches_count = 0
            if "matches" in self.report:
                matches_count = len(self.report["matches"])
                self.report["matches_count"] = matches_count
            all_issues_count = len(self.report["issue_ids"])
            non_matching_issues_count = all_issues_count - matches_count
            del self.report["issue_ids"]
            self.report["non_matches_count"] = non_matching_issues_count
            if matches_count > 0:
                for match in self.report["matches"].keys():
                    del self.report["matches"][match]["metadata"]["olm_operators"]
                    del self.report["matches"][match]["metadata"]["configured_features"]
            json_output = json.dumps(self.report)
            destination_path = os.path.join(f"{DATA_DIRECTORY}", f"{REPORT_OUTPUT_FILE}")
            FileSystemHelpers.write_file_content(destination_path, bytes(json_output, "utf-8"))
            # Dump JSON output to stdio so that we are composible
            sys.stdout.write(json_output)
        except Exception as e:
            raise GenerateJSONReportException(f"Unable to generate JSON report due to error {e}")
        return self.workflow_data

    def process_arguments(self):
        """Process any command specific arguments"""
        pass
