from unittest.mock import MagicMock

import jira
import pytest

from tools.triage.ticket_search.settings import (
    JIRA_SEARCH_FAILURE_RETRIES,
    PARSE_FAILURE_COUNT_FATALITY_THRESHOLD,
)
from tools.triage.ticket_search.ticket_fetcher import (
    TicketFetcher,
    TicketFetcherException,
)
from tools.triage.ticket_search.ticket_parser import TicketParserException
from tools.triage.ticket_search.triage_ticket import TriageTicket


class TestTicketFetcher:
    def setup_method(self):
        self.jira_client = MagicMock()
        self.ticket_parser = MagicMock()
        self.cache = MagicMock()
        self.ticket_fetcher = TicketFetcher(self.ticket_parser, self.jira_client)

    def mock_issue(self, issue_id, component):
        """Set up a mock issue"""
        issue = MagicMock()
        issue.key = issue_id
        issue.fields = MagicMock()
        issue.fields.components = [MagicMock()]
        issue.fields.components[0].name = component
        issue.fields.description = f"Description for {issue_id}"
        return issue

    def ticket_query(self, jql):
        query = MagicMock()
        query.build = MagicMock(return_value=jql)
        return query

    def test_ticket_should_be_parsed_if_it_is_a_triage_issue(self):
        """If the ticket is a triage issue then we will parse it"""
        issue_id = "MGMT-12345"
        mock_issue = self.mock_issue(issue_id, "Cloud-Triage")
        self.jira_client.issue = MagicMock(return_value=mock_issue)
        self.ticket_fetcher.fetch_single_ticket_by_key(issue_id)
        self.jira_client.issue.assert_called_once_with(issue_id)
        self.ticket_parser.parse.assert_called_once_with(mock_issue)

    def test_should_throw_an_exception_if_unable_to_fetch_a_ticket(self):
        issue_id = "MGMT-12345"
        self.jira_client.issue = MagicMock(side_effect=jira.exceptions.JIRAError("Jira error"))
        with pytest.raises(TicketFetcherException, match="Jira error"):
            self.ticket_fetcher.fetch_single_ticket_by_key(issue_id)

    def test_ticket_should_not_be_parsed_if_it_is_not_a_triage_issue(self):
        """If the ticket is not a triage issue then we will skip it"""
        issue_id = "MGMT-12345"
        mock_issue = self.mock_issue(issue_id, "Some-other-component")
        self.jira_client.issue = MagicMock(return_value=mock_issue)
        self.ticket_fetcher.fetch_single_ticket_by_key(issue_id)
        self.jira_client.issue.assert_called_once_with(issue_id)
        self.ticket_parser.parse.assert_not_called()

    def test_fetch_page_by_query(self):
        """Test fetch by query"""
        jql = "Generated JQL"
        ticket_query = self.ticket_query(jql)
        issue_1 = self.mock_issue("ISSUE-1", "Cloud-Triage")
        issue_2 = self.mock_issue("ISSUE-2", "Cloud-Triage")

        # This should be excluded because it is not a triage ticket
        issue_3 = self.mock_issue("ISSUE-3", "Some-other-component")
        self.jira_client.search_issues = MagicMock()

        # Make sure we are resiliant to the occasional jira error (auto retry)
        self.jira_client.search_issues.side_effect = [jira.exceptions.JIRAError("Jira error"), [issue_1, issue_2, issue_3]]

        self.ticket_parser.parse = MagicMock()
        self.ticket_parser.parse.side_effect = [TriageTicket(issue_1), TriageTicket(issue_2)]
        tickets = self.ticket_fetcher.fetch_page_by_query(ticket_query, 10, 0)
        self.ticket_parser.parse.assert_any_call(issue_1)
        self.ticket_parser.parse.assert_any_call(issue_2)
        assert self.ticket_parser.parse.call_count == 2
        assert tickets[0].key == "ISSUE-1"
        assert tickets[0].description == "Description for ISSUE-1"
        assert tickets[1].key == "ISSUE-2"
        assert tickets[1].description == "Description for ISSUE-2"

    def test_fetch_page_by_query_jira_errors_below_threshold(self):
        jql = "Generated JQL"
        ticket_query = self.ticket_query(jql)
        number_of_simulated_failures = JIRA_SEARCH_FAILURE_RETRIES - 1
        self.jira_client.search_issues = MagicMock()
        side_effects = []
        for _ in range(0, number_of_simulated_failures):
            side_effects += [jira.exceptions.JIRAError("Ticket fetcher exception")]
        issue_1 = self.mock_issue("ISSUE-1", "Cloud-Triage")
        side_effects += [issue_1]
        self.jira_client.search_issues.side_effect = side_effects
        self.ticket_fetcher.fetch_page_by_query(ticket_query, 10, 0)

    def test_fetch_page_by_query_too_many_jira_errors(self):
        jql = "Generated JQL"
        ticket_query = self.ticket_query(jql)
        number_of_simulated_failures = JIRA_SEARCH_FAILURE_RETRIES + 1
        self.jira_client.search_issues = MagicMock()
        side_effects = []
        for _ in range(0, number_of_simulated_failures):
            side_effects += [jira.exceptions.JIRAError("Ticket fetcher exception")]
        self.jira_client.search_issues.side_effect = side_effects
        with pytest.raises(TicketFetcherException, match="Ticket fetcher exception"):
            self.ticket_fetcher.fetch_page_by_query(ticket_query, 10, 0)

    def test_should_not_fail_when_parse_errors_below_threshold(self):
        """Test fetch by query"""
        jql = "Generated JQL"
        ticket_query = self.ticket_query(jql)
        number_of_simulated_failures = PARSE_FAILURE_COUNT_FATALITY_THRESHOLD - 1
        issues = []
        for i in range(0, number_of_simulated_failures):
            issues += [self.mock_issue(f"ISSUE-{i}", "Cloud-Triage")]
        self.jira_client.search_issues = MagicMock()
        self.jira_client.search_issues.side_effect = [issues]
        self.ticket_parser.parse = MagicMock()
        side_effects = []
        for _ in range(0, number_of_simulated_failures):
            side_effects += [TicketParserException("Ticket parser exception")]
        self.ticket_parser.parse.side_effect = side_effects
        self.ticket_fetcher.fetch_page_by_query(ticket_query, 10, 0)

    def test_should_fail_on_too_many_parse_errors(self):
        """Test fetch by query"""
        jql = "Generated JQL"
        ticket_query = self.ticket_query(jql)
        number_of_simulated_failures = PARSE_FAILURE_COUNT_FATALITY_THRESHOLD + 1
        issues = []
        for i in range(0, number_of_simulated_failures):
            issues += [self.mock_issue(f"ISSUE-{i}", "Cloud-Triage")]
        self.jira_client.search_issues = MagicMock()
        self.jira_client.search_issues.side_effect = [issues]
        self.ticket_parser.parse = MagicMock()
        side_effects = []
        for _ in range(0, number_of_simulated_failures):
            side_effects += [TicketParserException("Ticket parser exception")]
        self.ticket_parser.parse.side_effect = side_effects
        with pytest.raises(TicketFetcherException, match="Ticket parser exception"):
            self.ticket_fetcher.fetch_page_by_query(ticket_query, 10, 0)
