"""
Shared message structures for agent communication
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class A2AMessage:
    """Agent-to-Agent message structure"""
    message_id: str
    from_agent: str
    to_agent: str
    message_type: str  # "task_delegation", "status_update", "result"
    payload: Dict[str, Any]
    timestamp: str
