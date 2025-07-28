# Jira MCP Server

A Model Context Protocol (MCP) server that provides comprehensive integration with Jira, enabling AI assistants to interact with Jira projects, issues, users, and workflows.

## Features

- **Issue Management**: Create, update, search, and transition issues
- **Project Operations**: Manage projects, components, and versions  
- **User & Group Management**: Handle users, groups, and permissions
- **Comments & Attachments**: Add comments and manage attachments
- **Workflow Operations**: Get transitions and move issues through workflows
- **Advanced Search**: Powerful JQL (Jira Query Language) support
- **Flexible APIs**: Support for complex field structures and custom fields
- **Service Desk Support**: Enhanced features for Jira Service Desk

## Dependencies

### System Requirements
- **Python**: ≥ 3.12
- **Jira Instance**: Cloud, Server, or Data Center

### Python Dependencies
- `jira` ≥ 3.8.0 - Official Jira Python library
- `mcp[cli]` ≥ 1.12.1 - Model Context Protocol framework
- `python-dotenv` ≥ 1.0.0 - Environment variable loading from .env files

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd jira-mcp-server
```

### 2. Install Dependencies
Using uv (recommended):
```bash
uv install
```

Using pip:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

The server supports loading configuration from a `.env` file for convenience. Create a `.env` file in the project root or set environment variables directly:

#### Option 1: Using .env file (Recommended)
Create a `.env` file in the project root:

```env
# Required Configuration
JIRA_HOST=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_TOKEN=your-api-token

# Optional Configuration  
JIRA_CONTEXT=additional-context
```

#### Option 2: Environment Variables
```bash
# Required Configuration
export JIRA_HOST="https://your-domain.atlassian.net"  # For Jira Cloud
export JIRA_EMAIL="your-email@company.com"           # Your Jira email
export JIRA_TOKEN="your-api-token"                   # Jira API token

# Optional Configuration  
export JIRA_CONTEXT="additional-context"             # Optional context
```

> **Note**: The `.env` file is automatically loaded when the server starts. Environment variables take precedence over .env file values.

#### Getting Your Jira API Token

**For Jira Cloud:**
1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a label and copy the token
4. Use your email and the token for authentication

**For Jira Server/Data Center:**
1. Use your username and password, or
2. Generate a Personal Access Token in your Jira profile

## Usage

### Integration with Claude Desktop

Add the following configuration to your Claude Desktop config file:

#### Location of Config File:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### Configuration:
```json
{
  "mcpServers": {
    "jira": {
      "command": "uv",
      "args": [
        "run"
        "--project",
        "/path/to/jira-mcp-server",
        "mcp",
        "run",
        "main.py"
      ],
      "env": {
        "JIRA_HOST": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your-email@company.com", 
        "JIRA_TOKEN": "your-api-token"
      }
    }
  }
}
```

### Restart Claude Desktop
After adding the configuration, restart Claude Desktop to load the MCP server.

## Available Tools

The server provides 38+ tools organized into categories:

### Core Operations
- `search_issues` - Search using JQL queries
- `get_issue` - Get detailed issue information
- `create_issue` - Create issues with flexible field support
- `update_issue` - Update any issue fields
- `transition_issue` - Move issues through workflow

### Project Management  
- `get_projects` - List all accessible projects
- `get_project` - Get specific project details
- `create_project` - Create new projects
- `get_project_components` - List project components
- `get_project_versions` - List project versions

### User & Group Management
- `get_user` - Get user information
- `search_users` - Search for users
- `get_groups` - List groups
- `create_group` - Create new groups
- `add_user_to_group` - Manage group membership

### Comments & Collaboration
- `add_comment` - Add comments with visibility controls
- `get_issue_comments` - Get all issue comments
- `add_attachment` - Upload file attachments
- `get_watchers` - Get issue watchers
- `add_watcher` - Add issue watchers

### Advanced Features
- `create_issue_link` - Link issues together
- `add_worklog` - Log work time
- `get_fields` - Discover available fields
- `get_issue_types` - Get available issue types
- And many more...

## Examples

### Creating an Issue in an Epic
```python
# Use the create_issue tool with:
{
  "project": {"key": "PROJ"}, 
  "summary": "Story in Epic",
  "description": "Story description",
  "issuetype": {"name": "Story"},
  "parent": {"key": "EPIC-123"}
}
```

### Searching Issues
```python
# JQL Examples:
"project = PROJ AND status = Open"
"assignee = currentUser() AND created >= -7d" 
"project = PROJ AND issuetype = Bug AND priority = High"
"parent = EPIC-123"
```

### Advanced Issue Updates
```python
# Use update_issue with:
{
  "assignee": {"name": "john.doe"},
  "priority": {"name": "High"}, 
  "components": [{"name": "Frontend"}],
  "customfield_10000": "Epic Name",
  "labels": ["urgent", "bug"]
}
```

## Security Notes

⚠️ **Important**: Never commit your Jira credentials to version control!

- Use environment variables for all sensitive configuration
- Remove any hardcoded credentials from config files
- Consider using secrets management for production deployments
- Regularly rotate API tokens

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your API token is correct and not expired
   - Check that your email matches your Jira account
   - Ensure the Jira host URL is correct

2. **Permission Errors**
   - Verify your account has necessary permissions in Jira
   - Check project-level permissions for creating/editing issues
   - Ensure you have access to the specified projects

3. **Connection Issues**
   - Verify network connectivity to your Jira instance
   - Check if your organization uses VPN or firewall restrictions
   - Test the connection manually with curl or browser

### Debug Mode
Set environment variable for verbose logging:
```bash
export MCP_LOG_LEVEL=debug
```

## Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Make your changes
5. Add tests if applicable
6. Submit a pull request

## Acknowledgments

Special thanks to:
- **Anthropic** for the Model Context Protocol framework
- **Atlassian** for the Jira REST API and Python library
- **Python Jira Library Contributors** for the excellent `jira` package
- **MCP Community** for feedback and feature suggestions
- **Open Source Contributors** who help improve this project

## Support

For issues and questions:
- Create an issue in this repository
- Check the [Jira Python Library Documentation](https://jira.readthedocs.io/)
- Review [MCP Documentation](https://modelcontextprotocol.io/docs)
- Consult [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)

## Donate:

ETH (Mainnet): 0x765885e6Cb9e40E1504F80272A7b5B60ffF7b92d
USDT (SOL): GRNmdL1mpdBhgY8cFZggUo5k9eG5ic5QtA6NFTv6ZAbw

---

**Made with ❤️ for the AI and DevOps community**
