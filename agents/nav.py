"""
Agent Nav - The Executor Agent (ADK-based)

Role: Task execution and tool orchestration
Capabilities:
- Receives tasks from Agent Kai via A2A messages
- Calls MCP tools to perform actions
- Handles AP2 payment flows
- Returns execution status and results

This agent simulates ADK (Agent Development Kit) concepts:
- Task execution engine
- Tool integration (MCP)
- Payment handling (AP2)
- Result reporting
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.server import get_mcp_server
from ap2.payment_mock import get_ap2_instance
from .messages import A2AMessage


@dataclass
class TaskExecution:
    """Task execution record"""
    execution_id: str
    plan_id: str
    step_number: int
    action: str
    status: str  # "pending", "running", "completed", "failed"
    started_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentNav:
    """
    Agent Nav - The Executor
    
    Implements ADK-style agent with:
    - A2A message handling
    - MCP tool execution
    - AP2 payment processing
    - Result reporting
    """
    
    def __init__(self, agent_id: str = "agent_nav"):
        self.agent_id = agent_id
        self.role = "executor"
        self.executions: Dict[str, TaskExecution] = {}
        self.message_history: List[A2AMessage] = []
        
        # Connect to MCP server and AP2
        self.mcp_server = get_mcp_server()
        self.ap2 = get_ap2_instance()
        
        # Execution context (stores results from previous steps)
        self.execution_context: Dict[str, Any] = {}
        
        print(f"[Agent Nav] ⚡ Executor agent initialized (ID: {agent_id})")
        print(f"[Agent Nav] Connected to MCP Server and AP2")
    
    def receive_a2a_message(self, message: A2AMessage) -> Dict[str, Any]:
        """
        Receive and process A2A message from Agent Kai
        
        Args:
            message: A2A message with task delegation
            
        Returns:
            Execution result
        """
        self.message_history.append(message)
        
        print(f"\n[Agent Nav] 📨 Received A2A message from {message.from_agent}")
        print(f"[Agent Nav] Message type: {message.message_type}")
        
        if message.message_type == "task_delegation":
            return self._handle_task_delegation(message)
        else:
            return {"error": f"Unknown message type: {message.message_type}"}
    
    def _handle_task_delegation(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle task delegation from Agent Kai"""
        payload = message.payload
        step = payload.get("step")
        plan_id = payload.get("plan_id", "UNKNOWN")
        
        if not step:
            return {"error": "No step information in message"}
        
        print(f"[Agent Nav] 🎯 Executing Step {step['step_number']}: {step['action']}")
        
        # Create execution record
        import uuid
        execution_id = "EXEC-" + str(uuid.uuid4())[:8]
        now = datetime.utcnow().isoformat()
        
        execution = TaskExecution(
            execution_id=execution_id,
            plan_id=plan_id,
            step_number=step['step_number'],
            action=step['action'],
            status="running",
            started_at=now
        )
        
        self.executions[execution_id] = execution
        
        # Execute the action
        try:
            result = self._execute_action(step)
            
            execution.status = "completed"
            execution.completed_at = datetime.utcnow().isoformat()
            execution.result = result
            
            # Store result in context for future steps
            self.execution_context[f"step{step['step_number']}"] = result
            
            print(f"[Agent Nav] ✓ Step {step['step_number']} completed successfully")
            
            return {
                "success": True,
                "execution_id": execution_id,
                "step_number": step['step_number'],
                "action": step['action'],
                "result": result
            }
            
        except Exception as e:
            execution.status = "failed"
            execution.completed_at = datetime.utcnow().isoformat()
            execution.error = str(e)
            
            print(f"[Agent Nav] ✗ Step {step['step_number']} failed: {str(e)}")
            
            return {
                "success": False,
                "execution_id": execution_id,
                "step_number": step['step_number'],
                "action": step['action'],
                "error": str(e)
            }
    
    def _execute_action(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific action using appropriate tools
        
        Routes actions to:
        - MCP tools (create_task, execute_action)
        - AP2 payment flow (request_payment)
        """
        action = step['action']
        parameters = step['parameters']
        
        # Resolve parameter references (e.g., ${step2.workspace_id})
        resolved_params = self._resolve_parameters(parameters)
        
        # Route to appropriate handler
        if action == "create_task":
            return self._call_mcp_create_task(resolved_params)
        
        elif action == "request_payment":
            return self._handle_payment_flow(resolved_params)
        
        elif action in ["find_workspace", "confirm_booking", "send_notification", 
                       "gather_information", "analyze_data"]:
            return self._call_mcp_execute_action(action, resolved_params)
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _call_mcp_create_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP create_task tool"""
        print(f"[Agent Nav] 🔧 Calling MCP: create_task")
        
        result = self.mcp_server.create_task(
            task_name=parameters.get("task_name", "Unnamed task"),
            metadata=parameters.get("metadata", {})
        )
        
        return result
    
    def _call_mcp_execute_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP execute_action tool"""
        print(f"[Agent Nav] 🔧 Calling MCP: execute_action({action_name})")
        
        result = self.mcp_server.execute_action(
            action_name=action_name,
            parameters=parameters
        )
        
        return result
    
    def _handle_payment_flow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle complete AP2 payment flow
        
        Steps:
        1. Create payment intent
        2. Authorize payment
        3. Confirm payment
        4. Return receipt
        """
        amount = parameters.get("amount", 0.0)
        purpose = parameters.get("purpose", "Payment")
        
        print(f"\n[Agent Nav] 💳 Initiating AP2 payment flow")
        print(f"[Agent Nav] Amount: ${amount:.2f}")
        print(f"[Agent Nav] Purpose: {purpose}")
        
        # Step 1: Create payment intent
        intent = self.ap2.create_payment_intent(
            amount=amount,
            purpose=purpose,
            metadata=parameters
        )
        
        if not intent.get("payment_id"):
            raise Exception("Failed to create payment intent")
        
        payment_id = intent["payment_id"]
        
        # Step 2: Authorize payment
        print(f"[Agent Nav] 🔐 Requesting payment authorization...")
        auth = self.ap2.authorize_payment(
            payment_id=payment_id,
            authorized_by=self.agent_id,
            auth_method="agent_signature"
        )
        
        if not auth.get("success"):
            raise Exception(f"Payment authorization failed: {auth.get('error')}")
        
        # Step 3: Confirm payment
        print(f"[Agent Nav] ✅ Confirming payment...")
        receipt = self.ap2.confirm_payment(payment_id)
        
        if not receipt.get("success"):
            raise Exception(f"Payment confirmation failed: {receipt.get('error')}")
        
        print(f"[Agent Nav] ✓ Payment completed successfully")
        print(f"[Agent Nav] Transaction ID: {receipt.get('transaction_id')}")
        print(f"[Agent Nav] Confirmation Code: {receipt.get('confirmation_code')}")
        
        return receipt
    
    def _resolve_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve parameter references like ${step2.workspace_id}
        
        This allows steps to reference results from previous steps
        """
        resolved = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # Extract reference: ${step2.workspace_id} -> step2, workspace_id
                ref = value[2:-1]  # Remove ${ and }
                parts = ref.split(".")
                
                if len(parts) == 2:
                    step_ref, field = parts
                    
                    if step_ref in self.execution_context:
                        step_result = self.execution_context[step_ref]
                        
                        # Navigate nested result
                        if "data" in step_result and field in step_result["data"]:
                            resolved[key] = step_result["data"][field]
                        elif field in step_result:
                            resolved[key] = step_result[field]
                        else:
                            resolved[key] = value  # Keep original if not found
                    else:
                        resolved[key] = value  # Keep original if step not executed
                else:
                    resolved[key] = value
            else:
                resolved[key] = value
        
        return resolved
    
    def send_status_update(self, to_agent: str, status: str, data: Dict[str, Any]) -> A2AMessage:
        """Send status update to another agent (usually Agent Kai)"""
        import uuid
        
        message = A2AMessage(
            message_id="MSG-" + str(uuid.uuid4())[:8],
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type="status_update",
            payload={"status": status, "data": data},
            timestamp=datetime.utcnow().isoformat()
        )
        
        self.message_history.append(message)
        print(f"[Agent Nav] 📤 Sent status update to {to_agent}")
        
        return message


if __name__ == "__main__":
    # Test Agent Nav
    nav = AgentNav()
    
    print("\n=== Agent Nav Test ===\n")
    
    # Simulate A2A message from Agent Kai
    test_message = A2AMessage(
        message_id="MSG-TEST-001",
        from_agent="agent_kai",
        to_agent="agent_nav",
        message_type="task_delegation",
        payload={
            "plan_id": "PLAN-TEST",
            "step": {
                "step_number": 1,
                "action": "create_task",
                "description": "Test task creation",
                "parameters": {
                    "task_name": "Test Task",
                    "metadata": {"test": True}
                },
                "dependencies": [],
                "assigned_to": "agent_nav"
            },
            "goal": "Test goal"
        },
        timestamp=datetime.utcnow().isoformat()
    )
    
    result = nav.receive_a2a_message(test_message)
    print(f"\n✓ Execution result: {json.dumps(result, indent=2)}")
