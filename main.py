from mcp.server.fastmcp import FastMCP
from jira import JIRA
from config import config

mcp = FastMCP("Jira MCP Server")

jira = JIRA(
    options={
        "server": config.host,
    },
    token_auth=config.token,
)

@mcp.tool(title="Search issues", description="Search for issues using JQL (Jira Query Language). Examples: 'project = PROJ AND status = Open', 'assignee = currentUser() AND created >= -7d', 'project = PROJ AND issuetype = Bug AND priority = High', 'parent = EPIC-123'. Common fields: project, assignee, status, priority, created, updated, fixVersion, component", annotations={"readOnlyHint": True})
def search_issues(query: str, start_at: int, max_results: int) -> list[dict]:
    """Search for issues in Jira"""
    issues = jira.search_issues(query, startAt=start_at, maxResults=max_results)
    return [{"key": issue.key, "summary": issue.fields.summary} for issue in issues]

# Server and client information
@mcp.tool(title="Server info", description="Get information about the Jira server", annotations={"readOnlyHint": True})
def server_info() -> dict:
    """Get server information"""
    return jira.server_info()

@mcp.tool(title="Current user", description="Get information about the current authenticated user", annotations={"readOnlyHint": True})
def myself() -> dict:
    """Get current user information"""
    return jira.myself()

# Project management
@mcp.tool(title="Get projects", description="Get list of all accessible projects with keys, names, project types, and lead information. Use this to discover available projects for creating issues or searching", annotations={"readOnlyHint": True})
def get_projects() -> list[dict]:
    """Get all projects"""
    projects = jira.projects()
    return [{"key": project.key, "name": project.name, "id": project.id} for project in projects]

@mcp.tool(title="Get project", description="Get specific project by key", annotations={"readOnlyHint": True})
def get_project(key: str) -> dict:
    """Get project by key"""
    project = jira.project(key)
    return {
        "key": project.key,
        "name": project.name,
        "id": project.id,
        "description": getattr(project, 'description', ''),
        "lead": getattr(project.lead, 'displayName', '') if hasattr(project, 'lead') else ''
    }

@mcp.tool(title="Create project", description="Create a new project. key is required (3-10 uppercase letters), name defaults to key if not provided. project_type examples: 'software', 'business', 'service_desk'. assignee is project lead username. template_name for project templates. additional_params for extra fields like description, url, categoryId")
def create_project(key: str, name: str = None, project_type: str = "software", assignee: str = None, template_name: str = None, additional_params: dict = None) -> dict:
    """Create a new project with flexible parameters"""
    params = {
        "key": key,
        "name": name or key,
        "ptype": project_type
    }
    if assignee:
        params["assignee"] = assignee
    if template_name:
        params["template_name"] = template_name
    if additional_params:
        params.update(additional_params)
    
    result = jira.create_project(**params)
    return {"success": True, "project_id": result}

@mcp.tool(title="Get project components", description="Get components of a project", annotations={"readOnlyHint": True})
def get_project_components(project_key: str) -> list[dict]:
    """Get project components"""
    components = jira.project_components(project_key)
    return [{"id": comp.id, "name": comp.name, "description": getattr(comp, 'description', '')} for comp in components]

@mcp.tool(title="Get project versions", description="Get versions of a project", annotations={"readOnlyHint": True})
def get_project_versions(project_key: str) -> list[dict]:
    """Get project versions"""
    versions = jira.project_versions(project_key)
    return [{"id": ver.id, "name": ver.name, "released": getattr(ver, 'released', False)} for ver in versions]

# Issue management
@mcp.tool(title="Get issue", description="Get detailed issue information by key. Returns summary, description, status, assignee, reporter, priority, components, versions, labels, created/updated dates, and all custom fields. Use for getting full issue details", annotations={"readOnlyHint": True})
def get_issue(issue_key: str) -> dict:
    """Get issue by key"""
    issue = jira.issue(issue_key)
    return issue

@mcp.tool(title="Create issue", description="Create a new issue with flexible fields dict. Must include at minimum: project, summary, description, issuetype. Examples: {'project': {'key': 'PROJ'}, 'summary': 'Task title', 'description': 'Task description', 'issuetype': {'name': 'Story'}, 'parent': {'key': 'EPIC-123'}} for creating story in epic, or {'project': {'key': 'PROJ'}, 'summary': 'Bug title', 'description': 'Bug description', 'issuetype': {'name': 'Bug'}, 'priority': {'name': 'High'}, 'components': [{'name': 'Frontend'}]} for bug with priority and component")
def create_issue(fields: dict) -> dict:
    """Create a new issue with custom fields dict. Must include at minimum: project, summary, description, issuetype"""
    new_issue = jira.create_issue(fields=fields)
    return {"key": new_issue.key, "id": new_issue.id, "summary": new_issue.fields.summary}

@mcp.tool(title="Create simple issue", description="Create a basic issue with common fields. Parameters: project_key (e.g. 'PROJ'), summary (title), description (detailed description), issue_type (Task, Story, Bug, Epic, etc.). Example: project_key='MYPROJ', summary='Fix login bug', description='User cannot login with special characters', issue_type='Bug'")
def create_simple_issue(project_key: str, summary: str, description: str, issue_type: str = "Task") -> dict:
    """Create a simple issue with basic fields"""
    issue_dict = {
        'project': {'key': project_key},
        'summary': summary,
        'description': description,
        'issuetype': {'name': issue_type}
    }
    new_issue = jira.create_issue(fields=issue_dict)
    return {"key": new_issue.key, "id": new_issue.id, "summary": new_issue.fields.summary}

@mcp.tool(title="Update issue", description="Update issue with flexible fields dict. Can update any field like assignee, priority, components, etc. Example fields: {'assignee': {'name': 'john.doe'}, 'priority': {'name': 'High'}, 'components': [{'name': 'Frontend'}], 'customfield_10000': 'Epic Name', 'labels': ['urgent', 'bug']}")
def update_issue(issue_key: str, fields: dict, notify_users: bool = True) -> dict:
    """Update issue with custom fields"""
    issue = jira.issue(issue_key)
    issue.update(fields=fields, notify=notify_users)
    return {"success": True, "message": f"Issue {issue_key} updated"}

@mcp.tool(title="Assign issue", description="Assign issue to a user")
def assign_issue(issue_key: str, assignee: str) -> dict:
    """Assign issue to user"""
    jira.assign_issue(issue_key, assignee)
    return {"success": True, "message": f"Issue {issue_key} assigned to {assignee}"}

@mcp.tool(title="Get issue transitions", description="Get available workflow transitions for an issue. Returns transition IDs and names that can be used with transition_issue(). Common transitions: To Do -> In Progress, In Progress -> Done, Open -> Resolved", annotations={"readOnlyHint": True})
def get_issue_transitions(issue_key: str) -> list[dict]:
    """Get available transitions for issue"""
    transitions = jira.transitions(issue_key)
    return [{"id": t['id'], "name": t['name']} for t in transitions]

@mcp.tool(title="Transition issue", description="Transition issue to new status with optional fields. transition_id can be found using get_transitions(). Optional fields example: {'resolution': {'name': 'Fixed'}, 'assignee': {'name': 'john.doe'}, 'comment': [{'add': {'body': 'Resolving as fixed'}}]}. Common transitions: Done, In Progress, Closed")
def transition_issue(issue_key: str, transition_id: str, fields: dict = None) -> dict:
    """Transition issue to new status with optional fields (e.g., resolution, assignee, etc.)"""
    jira.transition_issue(issue_key, transition_id, fields=fields or {})
    return {"success": True, "message": f"Issue {issue_key} transitioned"}

# Comments
@mcp.tool(title="Get issue comments", description="Get all comments for an issue including comment ID, body text, author information, creation date, and visibility restrictions. Use for reviewing issue discussion history", annotations={"readOnlyHint": True})
def get_issue_comments(issue_key: str) -> list[dict]:
    """Get issue comments"""
    comments = jira.comments(issue_key)
    return comments

@mcp.tool(title="Add comment", description="Add comment to an issue with optional visibility. visibility example: {'type': 'group', 'value': 'jira-developers'} for group visibility or {'type': 'role', 'value': 'Developers'} for role visibility. Use is_internal=True for internal comments in Service Desk")
def add_comment(issue_key: str, comment_body: str, visibility: dict = None, is_internal: bool = False) -> dict:
    """Add comment to issue with optional visibility settings"""
    comment = jira.add_comment(issue_key, comment_body, visibility=visibility, is_internal=is_internal)
    return {"id": comment.id, "body": comment.body, "created": comment.created}

# Links
@mcp.tool(title="Create issue link", description="Create link between issues. link_data must contain type, inwardIssue, outwardIssue. Example: {'type': {'name': 'Blocks'}, 'inwardIssue': {'key': 'PROJ-1'}, 'outwardIssue': {'key': 'PROJ-2'}} means PROJ-1 blocks PROJ-2. Common link types: Blocks, Duplicate, Relates, Causes, Cloners")
def create_issue_link(link_data: dict) -> dict:
    """Create issue link with custom data dict. Example: {'type': {'name': 'Duplicate'}, 'inwardIssue': {'key': 'PROJ-1'}, 'outwardIssue': {'key': 'PROJ-2'}}"""
    result = jira.create_issue_link(link_data)
    return {"success": True, "message": "Issue link created"}

# Attachments
@mcp.tool(title="Add attachment", description="Add attachment to an issue")
def add_attachment(issue_key: str, file_path: str) -> dict:
    """Add attachment to issue"""
    attachment = jira.add_attachment(issue_key, file_path)
    return {"id": attachment.id, "filename": attachment.filename, "size": attachment.size}

# Users
@mcp.tool(title="Get user", description="Get user information by account ID or username. Returns display name, email, active status, account type. Use account ID for Jira Cloud, username for Server/Data Center", annotations={"readOnlyHint": True})
def get_user(account_id: str) -> dict:
    """Get user by account ID"""
    user = jira.user(account_id)
    return user

@mcp.tool(title="Search users", description="Search for users", annotations={"readOnlyHint": True})
def search_users(query: str, max_results: int = 50) -> list[dict]:
    """Search for users"""
    users = jira.search_users(query=query, maxResults=max_results)
    return users

# Groups
@mcp.tool(title="Get groups", description="Get list of groups", annotations={"readOnlyHint": True})
def get_groups(query: str = None) -> list[str]:
    """Get groups"""
    return jira.groups(query=query)

@mcp.tool(title="Add user to group", description="Add user to a group")
def add_user_to_group(username: str, group_name: str) -> dict:
    """Add user to group"""
    result = jira.add_user_to_group(username, group_name)
    return {"success": True, "message": f"User {username} added to group {group_name}"}

# Components
@mcp.tool(title="Create component", description="Create a new component in project. name is component name, project_key is project identifier. leadUserName is component lead username. assigneeType examples: 'PROJECT_LEAD', 'COMPONENT_LEAD', 'UNASSIGNED'. additional_params can include isAssigneeTypeValid, realAssignee")
def create_component(name: str, project_key: str, description: str = "", lead_user_name: str = None, assignee_type: str = None, additional_params: dict = None) -> dict:
    """Create component with flexible parameters"""
    params = {
        "name": name,
        "project": project_key,
        "description": description
    }
    if lead_user_name:
        params["leadUserName"] = lead_user_name
    if assignee_type:
        params["assigneeType"] = assignee_type
    if additional_params:
        params.update(additional_params)
    
    component = jira.create_component(**params)
    return {"id": component.id, "name": component.name, "description": getattr(component, 'description', '')}

# Versions
@mcp.tool(title="Create version", description="Create a new version in project. name is version name, project_key is project identifier. release_date/start_date format: 'YYYY-MM-DD'. archived=true for archived versions, released=true for released versions. additional_params can include userReleaseDate, userStartDate, projectId")
def create_version(name: str, project_key: str, description: str = "", release_date: str = None, start_date: str = None, archived: bool = False, released: bool = False, additional_params: dict = None) -> dict:
    """Create version with flexible parameters"""
    params = {
        "name": name,
        "project": project_key,
        "description": description,
        "archived": archived,
        "released": released
    }
    if release_date:
        params["releaseDate"] = release_date
    if start_date:
        params["startDate"] = start_date
    if additional_params:
        params.update(additional_params)
    
    version = jira.create_version(**params)
    return {"id": version.id, "name": version.name, "description": getattr(version, 'description', '')}

# Filters
@mcp.tool(title="Get favorite filters", description="Get favorite filters", annotations={"readOnlyHint": True})
def get_favorite_filters() -> list[dict]:
    """Get favorite filters"""
    filters = jira.favourite_filters()
    return [{
        "id": f.id,
        "name": f.name,
        "jql": getattr(f, 'jql', ''),
        "description": getattr(f, 'description', '')
    } for f in filters]

# Fields and types
@mcp.tool(title="Get fields", description="Get all available issue fields including system fields (summary, description, assignee) and custom fields (customfield_10000, etc.). Use this to discover field IDs for create_issue and update_issue operations", annotations={"readOnlyHint": True})
def get_fields() -> list[dict]:
    """Get all fields"""
    return jira.fields()

@mcp.tool(title="Get issue types", description="Get all issue types", annotations={"readOnlyHint": True})
def get_issue_types() -> list[dict]:
    """Get issue types"""
    issue_types = jira.issue_types()
    return [{"id": it.id, "name": it.name, "description": getattr(it, 'description', '')} for it in issue_types]

@mcp.tool(title="Get priorities", description="Get all priorities", annotations={"readOnlyHint": True})
def get_priorities() -> list[dict]:
    """Get priorities"""
    priorities = jira.priorities()
    return [{"id": p.id, "name": p.name, "description": getattr(p, 'description', '')} for p in priorities]

@mcp.tool(title="Get statuses", description="Get all statuses", annotations={"readOnlyHint": True})
def get_statuses() -> list[dict]:
    """Get statuses"""
    statuses = jira.statuses()
    return [{"id": s.id, "name": s.name, "description": getattr(s, 'description', '')} for s in statuses]

@mcp.tool(title="Get resolutions", description="Get all resolutions", annotations={"readOnlyHint": True})
def get_resolutions() -> list[dict]:
    """Get resolutions"""
    resolutions = jira.resolutions()
    return [{"id": r.id, "name": r.name, "description": getattr(r, 'description', '')} for r in resolutions]

# Agile / Jira Software
@mcp.tool(title="Get boards", description="Get agile boards", annotations={"readOnlyHint": True})
def get_boards(start_at: int = 0, max_results: int = 50) -> list[dict]:
    """Get agile boards"""
    boards = jira.boards(startAt=start_at, maxResults=max_results)
    return [{"id": board.id, "name": board.name, "type": getattr(board, 'type', '')} for board in boards]

@mcp.tool(title="Create board", description="Create a new agile board")
def create_board(name: str, filter_id: str, board_type: str = "scrum") -> dict:
    """Create agile board"""
    board = jira.create_board(name, filter_id, preset=board_type)
    return {"id": board.id, "name": board.name}

@mcp.tool(title="Get sprints", description="Get sprints for a board", annotations={"readOnlyHint": True})
def get_sprints(board_id: int, state: str = None) -> list[dict]:
    """Get sprints for board"""
    sprints = jira.sprints(board_id, state=state)
    return [{
        "id": sprint.id,
        "name": sprint.name,
        "state": getattr(sprint, 'state', ''),
        "startDate": getattr(sprint, 'startDate', ''),
        "endDate": getattr(sprint, 'endDate', '')
    } for sprint in sprints]

@mcp.tool(title="Create sprint", description="Create a new sprint")
def create_sprint(name: str, board_id: int, start_date: str = None, end_date: str = None) -> dict:
    """Create sprint"""
    sprint = jira.create_sprint(name, board_id, startDate=start_date, endDate=end_date)
    return {"id": sprint.id, "name": sprint.name, "state": getattr(sprint, 'state', '')}

@mcp.tool(title="Add issues to sprint", description="Add issues to a sprint")
def add_issues_to_sprint(sprint_id: int, issue_keys: list[str]) -> dict:
    """Add issues to sprint"""
    jira.add_issues_to_sprint(sprint_id, issue_keys)
    return {"success": True, "message": f"Added {len(issue_keys)} issues to sprint {sprint_id}"}

# Voting and watching
@mcp.tool(title="Get watchers", description="Get watchers for an issue", annotations={"readOnlyHint": True})
def get_watchers(issue_key: str) -> dict:
    """Get issue watchers"""
    watchers = jira.watchers(issue_key)
    return {
        "watchCount": watchers.watchCount,
        "watchers": [{"accountId": w.accountId, "displayName": w.displayName} for w in watchers.watchers]
    }

@mcp.tool(title="Add watcher", description="Add watcher to an issue")
def add_watcher(issue_key: str, username: str) -> dict:
    """Add watcher to issue"""
    jira.add_watcher(issue_key, username)
    return {"success": True, "message": f"Added {username} as watcher to {issue_key}"}

# Worklogs
@mcp.tool(title="Get worklogs", description="Get worklogs for an issue", annotations={"readOnlyHint": True})
def get_worklogs(issue_key: str) -> list[dict]:
    """Get issue worklogs"""
    worklogs = jira.worklogs(issue_key)
    return [{
        "id": worklog.id,
        "author": worklog.author.displayName,
        "comment": getattr(worklog, 'comment', ''),
        "timeSpent": worklog.timeSpent,
        "started": worklog.started
    } for worklog in worklogs]

@mcp.tool(title="Add worklog", description="Add worklog to an issue. time_spent format: '1h 30m', '2d', '45m'. time_spent_seconds as alternative (3600 for 1 hour). started format: '2023-12-01T10:00:00.000+0000'. user is username for worklog author. visibility example: {'type': 'group', 'value': 'jira-developers'}")
def add_worklog(issue_key: str, time_spent: str = None, time_spent_seconds: str = None, comment: str = "", started: str = None, user: str = None, visibility: dict = None, additional_params: dict = None) -> dict:
    """Add worklog to issue with flexible parameters"""
    params = {}
    if time_spent:
        params["timeSpent"] = time_spent
    if time_spent_seconds:
        params["timeSpentSeconds"] = time_spent_seconds
    if comment:
        params["comment"] = comment
    if started:
        params["started"] = started
    if user:
        params["user"] = user
    if visibility:
        params["visibility"] = visibility
    if additional_params:
        params.update(additional_params)
    
    worklog = jira.add_worklog(issue_key, **params)
    return {"id": worklog.id, "timeSpent": worklog.timeSpent, "comment": getattr(worklog, 'comment', '')}

# Service Desk (if supported)
@mcp.tool(title="Check service desk support", description="Check if Service Desk is supported", annotations={"readOnlyHint": True})
def check_service_desk_support() -> dict:
    """Check Service Desk support"""
    return {"supported": jira.supports_service_desk()}

@mcp.tool(title="Get service desks", description="Get service desks", annotations={"readOnlyHint": True})
def get_service_desks() -> list[dict]:
    """Get service desks"""
    try:
        service_desks = jira.service_desks()
        return [{"id": sd.id, "projectKey": sd.projectKey, "projectName": sd.projectName} for sd in service_desks]
    except:
        return []


