"""
MCP (Model Context Protocol) Server
Provides tools and context for AI agents

This server exposes three core tools:
1. create_task - Task creation and tracking
2. execute_action - Generic action executor
3. request_payment - Payment initiation (triggers AP2)
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Task data model"""
    task_id: str
    task_name: str
    metadata: Dict[str, Any]
    status: TaskStatus
    created_at: str
    updated_at: str
    result: Optional[Dict[str, Any]] = None


@dataclass
class ActionResult:
    """Action execution result"""
    action_name: str
    success: bool
    data: Dict[str, Any]
    timestamp: str
    error: Optional[str] = None


class MCPServer:
    """
    MCP Server implementing the Model Context Protocol
    
    Provides a standardized interface for agents to:
    - Create and manage tasks
    - Execute actions with parameters
    - Request payments through AP2
    """
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.action_handlers: Dict[str, callable] = {
            "find_workspace": self._find_workspace,
            "confirm_booking": self._confirm_booking,
            "send_notification": self._send_notification,
        }
        print("[MCP Server] Initialized with tools: create_task, execute_action, request_payment")
    
    def create_task(self, task_name: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new task
        
        Args:
            task_name: Human-readable task name
            metadata: Additional task context and parameters
            
        Returns:
            Task creation result with task_id
        """
        task_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        task = Task(
            task_id=task_id,
            task_name=task_name,
            metadata=metadata,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now
        )
        
        self.tasks[task_id] = task
        
        print(f"[MCP Server] ✓ Task created: {task_name} (ID: {task_id})")
        
        return {
            "success": True,
            "task_id": task_id,
            "task_name": task_name,
            "status": task.status.value,
            "created_at": now
        }
    
    def execute_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a named action with parameters
        
        Args:
            action_name: Name of the action to execute
            parameters: Action-specific parameters
            
        Returns:
            Action execution result
        """
        print(f"[MCP Server] Executing action: {action_name}")
        
        if action_name not in self.action_handlers:
            return {
                "success": False,
                "action_name": action_name,
                "error": f"Unknown action: {action_name}",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            handler = self.action_handlers[action_name]
            result_data = handler(parameters)
            
            result = ActionResult(
                action_name=action_name,
                success=True,
                data=result_data,
                timestamp=datetime.utcnow().isoformat()
            )
            
            print(f"[MCP Server] ✓ Action completed: {action_name}")
            return asdict(result)
            
        except Exception as e:
            print(f"[MCP Server] ✗ Action failed: {action_name} - {str(e)}")
            return {
                "success": False,
                "action_name": action_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def request_payment(self, amount: float, purpose: str) -> Dict[str, Any]:
        """
        Request a payment (triggers AP2 flow)
        
        Args:
            amount: Payment amount in USD
            purpose: Payment purpose/description
            
        Returns:
            Payment request details (to be processed by AP2)
        """
        payment_id = str(uuid.uuid4())
        
        print(f"[MCP Server] Payment requested: ${amount:.2f} for '{purpose}'")
        
        return {
            "success": True,
            "payment_id": payment_id,
            "amount": amount,
            "purpose": purpose,
            "status": "pending_authorization",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Action Handlers (simulated business logic)
    
    def _find_workspace(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate finding a workspace"""
        duration = parameters.get("duration_hours", 1)
        workspace_type = parameters.get("type", "premium")
        
        # Simulate workspace search
        workspace = {
            "workspace_id": "WS-" + str(uuid.uuid4())[:8],
            "type": workspace_type,
            "duration_hours": duration,
            "price_per_hour": 25.0,
            "total_price": 25.0 * duration,
            "location": "Downtown Tech Hub",
            "amenities": ["High-speed WiFi", "Standing desk", "Coffee bar"]
        }
        
        return workspace
    
    def _confirm_booking(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate booking confirmation"""
        workspace_id = parameters.get("workspace_id")
        payment_id = parameters.get("payment_id")
        
        booking = {
            "booking_id": "BK-" + str(uuid.uuid4())[:8],
            "workspace_id": workspace_id,
            "payment_id": payment_id,
            "status": "confirmed",
            "confirmation_code": str(uuid.uuid4())[:6].upper(),
            "check_in_time": "2025-12-22T18:00:00Z"
        }
        
        return booking
    
    def _send_notification(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate sending a notification"""
        recipient = parameters.get("recipient", "user@example.com")
        message = parameters.get("message", "")
        
        return {
            "notification_id": "NT-" + str(uuid.uuid4())[:8],
            "recipient": recipient,
            "message": message,
            "sent_at": datetime.utcnow().isoformat(),
            "delivery_status": "sent"
        }
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current task status"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task.task_id,
            "task_name": task.task_name,
            "status": task.status.value,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "result": task.result
        }
    
    def update_task_status(self, task_id: str, status: TaskStatus, result: Optional[Dict[str, Any]] = None):
        """Update task status"""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            self.tasks[task_id].updated_at = datetime.utcnow().isoformat()
            if result:
                self.tasks[task_id].result = result


# Singleton instance
_mcp_server = None

def get_mcp_server() -> MCPServer:
    """Get or create MCP server instance"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()
    return _mcp_server


if __name__ == "__main__":
    # Test the MCP server
    server = get_mcp_server()
    
    print("\n=== MCP Server Test ===\n")
    
    # Test task creation
    task_result = server.create_task(
        "Book workspace",
        {"duration": 2, "type": "premium"}
    )
    print(f"Task created: {json.dumps(task_result, indent=2)}\n")
    
    # Test action execution
    action_result = server.execute_action(
        "find_workspace",
        {"duration_hours": 2, "type": "premium"}
    )
    print(f"Action result: {json.dumps(action_result, indent=2)}\n")
    
    # Test payment request
    payment_result = server.request_payment(50.0, "Workspace booking")
    print(f"Payment request: {json.dumps(payment_result, indent=2)}\n")
