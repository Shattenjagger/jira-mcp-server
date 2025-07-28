import os
from typing import Optional
from dotenv import load_dotenv


class JiraConfig:
    """Configuration for Jira integration"""
    
    def __init__(self):
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        self.email: Optional[str] = os.getenv("JIRA_EMAIL", "")
        self.host: Optional[str] = os.getenv("JIRA_HOST", "")
        self.token: Optional[str] = os.getenv("JIRA_TOKEN", "")
        self.context: str = os.getenv("JIRA_CONTEXT", "")
        
        # Validate required configuration
        self._validate()
    
    def _validate(self) -> None:
        """Validate that all required configuration is present"""
        missing = []
        
        if not self.email:
            missing.append("JIRA_EMAIL")
        if not self.host:
            missing.append("JIRA_HOST")
        if not self.token:
            missing.append("JIRA_TOKEN")
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    @property
    def is_configured(self) -> bool:
        """Check if all required configuration is present"""
        return bool(self.email and self.host and self.token)


# Global configuration instance
config = JiraConfig() 