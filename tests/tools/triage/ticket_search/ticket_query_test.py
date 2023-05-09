from tools.triage.ticket_search.ticket_query import TicketQuery


def test_default_ticket_query():
    """
    Test that the default ticket query filters for triage tickets within the default days range
    """
    ticket_query = TicketQuery.create()
    assert ticket_query.build() == """(project = \"AITRIAGE\"  AND component = \"Cloud-Triage\") ORDER BY created DESC"""


def test_days_filter():
    """
    Test the days filter
    """
    ticket_query = TicketQuery.create().days_query(7)
    assert ticket_query.build() == """(project = \"AITRIAGE\"  AND component = \"Cloud-Triage\" AND created >= -7d) ORDER BY created DESC"""


def test_text_like_query():
    """
    Test the text search query
    """
    ticket_query = TicketQuery.create().text_like_query("Some text search")
    assert ticket_query.build() == """(project = \"AITRIAGE\"  AND component = \"Cloud-Triage\" AND text ~ \"Some text search\") ORDER BY created DESC"""


def test_jql_clause():
    """
    Test the JQL clause functionality
    """
    ticket_query = TicketQuery.create().jql_clause("jql_clause_1").jql_clause("jql_clause_2")
    assert ticket_query.build() == """(project = \"AITRIAGE\"  AND component = \"Cloud-Triage\" AND jql_clause_1 AND jql_clause_2) ORDER BY created DESC"""


def test_openshift_version():
    """
    Test openshift version query
    """
    ticket_query = TicketQuery.create().openshift_version("4.13.11")
    assert ticket_query.build() == """(project = \"AITRIAGE\"  AND component = \"Cloud-Triage\" AND text ~ \"OpenShift version: 4.13.11\") ORDER BY created DESC"""
