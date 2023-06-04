"""Module for command line utility to fetch a single triage ticket"""
import argparse
import json
import logging
import os
from subprocess import PIPE
import subprocess
import sys

from command import Command
from search_by_path_and_content import SearchByPathAndContent
from search_for_tickets import SearchForTickets
from workflow_data import WorkflowData


class GetMustGatherPathsException(Exception):
    pass

class GetMustGatherPaths(Command):
    """Responsible for getting the cluster operators for a ticket"""

    def __init__(self):
        """Constructor"""
        self.args = []
        self.unknown_args = []
        self.logger = logging.getLogger(__name__)

    def get_command_key(self) -> str:
        return "get_cluster_operators_for_ticket"

    def get_friendly_name(self) -> str:
        return "Get cluster operators for ticket"

    def run(self, workflow_data: "WorkflowData") -> "WorkflowData":
        search_for_tickets = SearchForTickets()
        search_by_path_and_content = SearchByPathAndContent()
        workflow_data = search_for_tickets._run_internal(workflow_data, self.args, self.args.jira_access_token, self.args.days)
        workflow_data = search_by_path_and_content._run_internal(workflow_data, self.args, self.args.days, "openshift/must-gather", "(.*version$)") 
        if "matches" in workflow_data:
            for key in workflow_data["matches"].keys():
                match = workflow_data["matches"][key]
                if "files" in match:
                    for file in match["files"]:
                        if file != "":
                            match["has_must_gather"] = True
                            must_gather_path = os.path.dirname(file).strip("/")
                            match["must_gather_path"] = must_gather_path
                            self.omg_get_co(match)
        return workflow_data

    def omg_get_co(self, match):
        if "must_gather_path" in match:
            must_gather_path = match["must_gather_path"]
            match["omg_use_command"] = f"use {must_gather_path}"
            try:
                process = subprocess.Popen(
                    [
                        "omg",
                        match["omg_use_command"],
                        "&&",
                        "omg",
                        "get",
                        "co"
                    ],
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=PIPE,
                    shell=True
                )

                output, error = process.communicate(timeout=60)
                print("Cluster operators")
                print(output.decode("utf-8"))
                match["cluster_operators"] = output.decode("utf-8")



            except Exception as e:
                message = f"Error occured while attempting to get cluster operators using {must_gather_path}, error is {e}"
                match["omg_error"] = message
                self.logger.warn(message)

    def process_arguments(self):
        """Process any command specific arguments"""
        parser = argparse.ArgumentParser(add_help=False)
        login_group = parser.add_argument_group(title="login options")
        login_args = login_group.add_argument_group()
        login_args.add_argument(
            "--jira-access-token",
            default=os.environ.get("JIRA_ACCESS_TOKEN"),
            required=True,
            help="PAT (personal access token) for accessing Jira",
        )
        query_group = parser.add_argument_group(title="query parameters")
        query_args = query_group.add_argument_group()
        query_args.add_argument(
            "-d", "--days", required=True, default=7, help="Number of days worth of tickets to pull"
        )
        self.args, self.unknown_args = parser.parse_known_args()
