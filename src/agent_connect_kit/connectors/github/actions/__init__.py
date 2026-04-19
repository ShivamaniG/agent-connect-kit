from agent_connect_kit.connectors.github.actions.add_labels import add_labels_action
from agent_connect_kit.connectors.github.actions.assign_issue import assign_issue_action
from agent_connect_kit.connectors.github.actions.close_issue import close_issue_action
from agent_connect_kit.connectors.github.actions.comment_on_issue import comment_on_issue_action
from agent_connect_kit.connectors.github.actions.create_issue import create_issue_action
from agent_connect_kit.connectors.github.actions.create_pr import create_pr_action
from agent_connect_kit.connectors.github.actions.get_commits import get_commits_action
from agent_connect_kit.connectors.github.actions.get_file_contents import (
    get_file_contents_action,
)
from agent_connect_kit.connectors.github.actions.get_issues import get_issues_action
from agent_connect_kit.connectors.github.actions.get_pr import get_pr_action
from agent_connect_kit.connectors.github.actions.get_user import get_user_action
from agent_connect_kit.connectors.github.actions.list_branches import list_branches_action
from agent_connect_kit.connectors.github.actions.list_notifications import (
    list_notifications_action,
)
from agent_connect_kit.connectors.github.actions.list_org_members import (
    list_org_members_action,
)
from agent_connect_kit.connectors.github.actions.list_prs import list_prs_action
from agent_connect_kit.connectors.github.actions.list_repos import list_repos_action
from agent_connect_kit.connectors.github.actions.merge_pr import merge_pr_action
from agent_connect_kit.connectors.github.actions.remove_labels import remove_labels_action
from agent_connect_kit.connectors.github.actions.reopen_issue import reopen_issue_action
from agent_connect_kit.connectors.github.actions.search_code import search_code_action
from agent_connect_kit.connectors.github.actions.star_repo import star_repo_action
from agent_connect_kit.connectors.github.actions.unstar_repo import unstar_repo_action

ALL_ACTIONS = [
    # read (repo)
    list_repos_action,
    list_branches_action,
    get_commits_action,
    get_file_contents_action,
    search_code_action,
    # read (issues/prs)
    get_issues_action,
    list_prs_action,
    get_pr_action,
    # write (issues)
    create_issue_action,
    close_issue_action,
    reopen_issue_action,
    comment_on_issue_action,
    add_labels_action,
    remove_labels_action,
    assign_issue_action,
    # write (prs)
    create_pr_action,
    merge_pr_action,
    # user / org / notifications
    get_user_action,
    list_org_members_action,
    list_notifications_action,
    # stars
    star_repo_action,
    unstar_repo_action,
]
