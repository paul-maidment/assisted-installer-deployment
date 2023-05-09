"""The module for the main cli app"""
# pylint: disable=too-few-public-methods
import argparse
import logging
import sys

from command import Command
from fetch_by_id import FetchById
from generate_json_report import GenerateJSONReport
from search_by_path_and_content import SearchByPathAndContent
from search_for_tickets import SearchForTickets
from workflow_data import WorkflowData


class App:
    """General launcher app for command line utilities"""

    def __init__(self, arguments: list[str]):
        self.args = arguments
        self.logger = logging.getLogger(__name__)

    def run(self, logging_verbosity):
        """App entry point"""

        self.logger.debug("Starting...")

        # Data structure to store results between workflows.
        workflow_data = WorkflowData()

        # Get the workflow to run
        cmds = self.setup_cmds()

        # Validate the parameters for the workflow the user has chosen.
        # We evaluate the params for all workflows at once to ensure timely feedback.
        for cmd in cmds:
            self.logger.debug(f"Processing arguments for {cmd.get_friendly_name()}")
            cmd.process_arguments()

        # Run the chosen workflow by running all cmds in the flow.
        for cmd in cmds:
            self.logger.debug(f"Running {cmd.get_friendly_name()}")
            workflow_data = cmd.run(workflow_data)

    def setup_cmds(self) -> list[Command]:
        # Set up the workflow according to user settings
        cmds = []
        if self.args.fetch is not None and self.args.fetch == "fetch_by_id":
            cmds += [FetchById()]
        elif self.args.fetch is not None and self.args.fetch == "search_for_tickets":
            cmds += [SearchForTickets()]
        cmds += [SearchByPathAndContent()]
        cmds += [GenerateJSONReport()]
        return cmds


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    functionGroup = parser.add_argument_group(title="function")
    functionGroup.add_argument(
        "--fetch",
        required=False,
        help="The fetch function to use (if any)",
    )
    functionGroup.add_argument(
        "-v",
        "--verbosity",
        required=False,
        type=str,
        choices=["warn", "info", "error", "debug"],
        help="The level of logging that should take place",
    )
    args, unknown = parser.parse_known_args()
    verbosity = logging.ERROR
    if args.verbosity is not None:
        if args.verbosity == "debug":
            verbosity = level = logging.DEBUG
        elif args.verbosity == "info":
            verbosity = level = logging.INFO
        elif args.verbosity == "error":
            verbosity = level = logging.ERROR
        elif args.verbosity == "warn":
            verbosity = level = logging.WARN

    logging.basicConfig(
        stream=sys.stderr,
        level=verbosity,
        format="%(asctime)s %(levelname)-10s %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
    )
    logger = logging.getLogger(__name__).setLevel(verbosity)
    logging.getLogger("__main__").setLevel(verbosity)
    application = App(args)
    application.run(verbosity)
