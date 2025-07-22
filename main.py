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

# jql = "project = 'DATA' AND issuetype = 'Task'"

# issues = jira.search_issues(jql, maxResults=100)

# for issue in issues:
#     print(issue.key, issue.fields.summary)

@mcp.tool()
def search_issues(query: str, start_at: int, ) -> list[dict]:
    """Search for issues in Jira"""
    issues = jira.search_issues(query)
    return [{"key": issue.key, "summary": issue.fields.summary} for issue in issues]




# # Add an addition tool
# @mcp.tool()
# def add(a: int, b: int) -> int:
#     """Add two numbers"""
#     return a + b
#
#
# # Add a dynamic greeting resource
# @mcp.resource("greeting://{name}")
# def get_greeting(name: str) -> str:
#     """Get a personalized greeting"""
#     return f"Hello, {name}!"
#
#
# # Add a prompt
# @mcp.prompt()
# def greet_user(name: str, style: str = "friendly") -> str:
#     """Generate a greeting prompt"""
#     styles = {
#         "friendly": "Please write a warm, friendly greeting",
#         "formal": "Please write a formal, professional greeting",
#         "casual": "Please write a casual, relaxed greeting",
#     }
#
#     return f"{styles.get(style, styles['friendly'])} for someone named {name}."