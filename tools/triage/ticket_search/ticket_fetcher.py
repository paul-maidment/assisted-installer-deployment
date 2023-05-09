"""Ticket fetcher module"""

import logging

import jira

from tools.triage.ticket_search import settings

from .ticket_parser import TicketParser, TicketParserException
from .ticket_query import TicketQuery
from .triage_ticket import TriageTicket


class TicketFetcherException(Exception):
    pass


class TicketFetcher:
    """Responsible for fetching tickets from Jira in response to queries"""

    def __init__(self, ticket_parser: "TicketParser", jira_client: "jira"):
        """Constructor"""
        self.client = jira_client
        self.ticket_parser = ticket_parser
        self.logger = logging.getLogger(__name__)

    def fetch_single_ticket_by_key(self, key) -> "TriageTicket":
        """Fetches a single triage ticket from Jira using the key"""
        try:
            issue = self.client.issue(key)
            if issue is not None:
                if issue.fields.components[0].name != settings.TRIAGE_TICKET_SEARCH_COMPONENT:
                    self.logger.warn(
                        f"WARNING: Ticket fetched for ID {key} \
                        but the component indicates that this is not a triage ticket. \
                        Returning None for this ticket."
                    )
                    return None
                self.logger.info(f"Fetched {key}, parsing...")
                return self.ticket_parser.parse(issue)
            return None
        except jira.exceptions.JIRAError as exception:
            if exception.status_code == 404:
                self.logger.warn(f"Jira issue with ID {key} was not found!")
                return None
            raise TicketFetcherException(exception)

    def count_for_query(self, query: "TicketQuery"):
        """Helper for pagination, provides a total item count for a query in an efficient way"""
        query_text = query.build()
        return self.client.search_issues(query_text, maxResults=1).total

    def fetch_page_by_query(self, query: "TicketQuery", page_size, start_index) -> list["TriageTicket"]:
        """Fetches a specific page of a query, given a pagesize and startindex"""
        tickets = []
        for attempt in range(1, settings.JIRA_SEARCH_FAILURE_RETRIES + 1):
            try:
                issues = self.client.search_issues(query.build(), maxResults=page_size, startAt=start_index)
                break
            except Exception as e:
                message = f"{attempt}/{settings.JIRA_SEARCH_FAILURE_RETRIES} There was an error while attempting to fetch issues from jira using query: {query.build()}, maxResults: {page_size}, startAt: {start_index}, error {e}"
                is_fatal = attempt == settings.JIRA_SEARCH_FAILURE_RETRIES
                if is_fatal:
                    message += f"\nFailures have reached acceptable limit of {settings.JIRA_SEARCH_FAILURE_RETRIES}"
                self._handle_error(message, is_fatal=is_fatal)

        parse_failure_count = 0
        for issue in issues:
            # If we are not dealing with a Triage issue, then skip this ticket.
            if issue.fields.components[0].name != settings.TRIAGE_TICKET_SEARCH_COMPONENT:
                continue
            try:
                triage_ticket = self.ticket_parser.parse(issue)
                tickets += [triage_ticket]
            except TicketParserException as exception:
                parse_failure_count += 1
                is_fatal = parse_failure_count > settings.PARSE_FAILURE_COUNT_FATALITY_THRESHOLD
                self._handle_error(f"{str(exception)}", is_fatal=is_fatal)

        return tickets

    def _handle_error(self, message, is_fatal=True):
        """Handles an error if it occurs"""
        self.logger.error(message)
        if is_fatal:
            raise TicketFetcherException(message)
