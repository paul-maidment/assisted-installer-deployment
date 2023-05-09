from tools.triage.ticket_search.triage_ticket import TriageTicket


class IssueCacheException(Exception):
    pass


class IssueCache:
    """Interface for an issue cache"""

    def exists(self, issue_id: str) -> bool:
        raise IssueCacheException("Not implemented")

    def save_metadata(self, triage_ticket: "TriageTicket"):
        raise IssueCacheException("Not implemented")
