"""
Agent Kai - The Planner Agent (ADK-based)

Role: Strategic planning and task decomposition
Capabilities:
- Accepts high-level user goals
- Breaks goals into structured, actionable steps
- Delegates execution tasks to Agent Nav using A2A protocol
- Monitors execution progress and adapts plans

This agent simulates ADK (Agent Development Kit) concepts:
- Agent lifecycle management
- Planning and reasoning
- Inter-agent communication
- Memory and context management
"""

import json
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PlanStep:
    """Individual step in an execution plan"""
    step_number: int
    action: str
    description: str
    parameters: Dict[str, Any]
    dependencies: List[int]  # Step numbers this depends on
    assigned_to: str  # Which agent executes this


@dataclass
class ExecutionPlan:
    """Complete execution plan for a goal"""
    plan_id: str
    goal: str
    steps: List[PlanStep]
    created_at: str
    status: str


@dataclass
class A2AMessage:
    """Agent-to-Agent message structure"""
    message_id: str
    from_agent: str
    to_agent: str
    message_type: str  # "task_delegation", "status_update", "result"
    payload: Dict[str, Any]
    timestamp: str


class AgentKai:
    """
    Agent Kai - The Planner
    
    Implements ADK-style agent with:
    - Goal understanding and decomposition
    - Multi-step planning
    - A2A communication for delegation
    - Plan monitoring and adaptation
    """
    
    def __init__(self, agent_id: str = "agent_kai"):
        self.agent_id = agent_id
        self.role = "planner"
        self.plans: Dict[str, ExecutionPlan] = {}
        self.message_history: List[A2AMessage] = []
        print(f"[Agent Kai] 🧠 Planner agent initialized (ID: {agent_id})")
    
    def receive_goal(self, goal: str, context: Dict[str, Any] = None) -> ExecutionPlan:
        """
        Receive a high-level goal from the user
        
        Args:
            goal: Natural language goal description
            context: Additional context for planning
            
        Returns:
            Execution plan with structured steps
        """
        print(f"\n[Agent Kai] 📋 Received goal: '{goal}'")
        print(f"[Agent Kai] 🤔 Analyzing and creating execution plan...")
        
        # Generate plan based on goal
        plan = self._create_plan(goal, context or {})
        
        # Store plan
        self.plans[plan.plan_id] = plan
        
        print(f"[Agent Kai] ✓ Plan created with {len(plan.steps)} steps")
        self._display_plan(plan)
        
        return plan
    
    def _create_plan(self, goal: str, context: Dict[str, Any]) -> ExecutionPlan:
        """
        Create an execution plan by decomposing the goal
        
        This is a simplified planning algorithm. Production ADK would use:
        - LLM-based reasoning for complex goal decomposition
        - Domain-specific planning algorithms
        - Constraint satisfaction
        - Resource optimization
        """
        import uuid
        
        plan_id = "PLAN-" + str(uuid.uuid4())[:8]
        now = datetime.utcnow().isoformat()
        
        # Goal-specific planning logic
        steps = []
        
        if "book" in goal.lower() and "workspace" in goal.lower():
            steps = self._plan_workspace_booking(context)
        elif "research" in goal.lower():
            steps = self._plan_research_task(context)
        else:
            # Generic task planning
            steps = self._plan_generic_task(goal, context)
        
        plan = ExecutionPlan(
            plan_id=plan_id,
            goal=goal,
            steps=steps,
            created_at=now,
            status="ready"
        )
        
        return plan
    
    def _plan_workspace_booking(self, context: Dict[str, Any]) -> List[PlanStep]:
        """Plan for workspace booking scenario"""
        duration = context.get("duration_hours", 2)
        workspace_type = context.get("type", "premium")
        
        return [
            PlanStep(
                step_number=1,
                action="create_task",
                description="Create booking task in system",
                parameters={
                    "task_name": "Book premium workspace",
                    "metadata": {"duration": duration, "type": workspace_type}
                },
                dependencies=[],
                assigned_to="agent_nav"
            ),
            PlanStep(
                step_number=2,
                action="find_workspace",
                description="Search for available workspace",
                parameters={
                    "duration_hours": duration,
                    "type": workspace_type
                },
                dependencies=[1],
                assigned_to="agent_nav"
            ),
            PlanStep(
                step_number=3,
                action="request_payment",
                description="Process payment for booking",
                parameters={
                    "amount": 25.0 * duration,
                    "purpose": f"{workspace_type} workspace for {duration}h"
                },
                dependencies=[2],
                assigned_to="agent_nav"
            ),
            PlanStep(
                step_number=4,
                action="confirm_booking",
                description="Finalize workspace booking",
                parameters={
                    "workspace_id": "${step2.workspace_id}",
                    "payment_id": "${step3.payment_id}"
                },
                dependencies=[3],
                assigned_to="agent_nav"
            ),
            PlanStep(
                step_number=5,
                action="send_notification",
                description="Send confirmation to user",
                parameters={
                    "recipient": "user@example.com",
                    "message": "Workspace booking confirmed!"
                },
                dependencies=[4],
                assigned_to="agent_nav"
            )
        ]
    
    def _plan_research_task(self, context: Dict[str, Any]) -> List[PlanStep]:
        """Plan for research scenario"""
        topic = context.get("topic", "general")
        
        return [
            PlanStep(
                step_number=1,
                action="create_task",
                description="Create research task",
                parameters={"task_name": f"Research: {topic}", "metadata": context},
                dependencies=[],
                assigned_to="agent_nav"
            ),
            PlanStep(
                step_number=2,
                action="gather_information",
                description="Collect relevant information",
                parameters={"topic": topic, "sources": ["web", "database"]},
                dependencies=[1],
                assigned_to="agent_nav"
            ),
            PlanStep(
                step_number=3,
                action="analyze_data",
                description="Analyze gathered information",
                parameters={"analysis_type": "summary"},
                dependencies=[2],
                assigned_to="agent_nav"
            )
        ]
    
    def _plan_generic_task(self, goal: str, context: Dict[str, Any]) -> List[PlanStep]:
        """Generic planning fallback"""
        return [
            PlanStep(
                step_number=1,
                action="create_task",
                description=f"Execute: {goal}",
                parameters={"task_name": goal, "metadata": context},
                dependencies=[],
                assigned_to="agent_nav"
            )
        ]
    
    def delegate_to_nav(self, plan: ExecutionPlan) -> List[A2AMessage]:
        """
        Delegate execution to Agent Nav using A2A protocol
        
        Args:
            plan: Execution plan to delegate
            
        Returns:
            List of A2A messages sent to Agent Nav
        """
        print(f"\n[Agent Kai] 📤 Delegating plan to Agent Nav via A2A...")
        
        messages = []
        
        for step in plan.steps:
            message = self._create_a2a_message(
                to_agent="agent_nav",
                message_type="task_delegation",
                payload={
                    "plan_id": plan.plan_id,
                    "step": asdict(step),
                    "goal": plan.goal
                }
            )
            messages.append(message)
            self.message_history.append(message)
            
            print(f"[Agent Kai] → Step {step.step_number}: {step.action} → Agent Nav")
        
        print(f"[Agent Kai] ✓ Delegated {len(messages)} tasks to Agent Nav")
        
        return messages
    
    def _create_a2a_message(
        self,
        to_agent: str,
        message_type: str,
        payload: Dict[str, Any]
    ) -> A2AMessage:
        """Create an A2A message"""
        import uuid
        
        return A2AMessage(
            message_id="MSG-" + str(uuid.uuid4())[:8],
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def _display_plan(self, plan: ExecutionPlan):
        """Display plan in readable format"""
        print(f"\n{'='*60}")
        print(f"EXECUTION PLAN: {plan.plan_id}")
        print(f"Goal: {plan.goal}")
        print(f"{'='*60}")
        
        for step in plan.steps:
            deps = f" (depends on: {step.dependencies})" if step.dependencies else ""
            print(f"\nStep {step.step_number}: {step.action}{deps}")
            print(f"  Description: {step.description}")
            print(f"  Assigned to: {step.assigned_to}")
            print(f"  Parameters: {json.dumps(step.parameters, indent=4)}")
        
        print(f"\n{'='*60}\n")
    
    def receive_status_update(self, message: A2AMessage):
        """Receive status update from Agent Nav"""
        self.message_history.append(message)
        print(f"[Agent Kai] 📨 Status update from {message.from_agent}: {message.payload.get('status')}")


if __name__ == "__main__":
    # Test Agent Kai
    kai = AgentKai()
    
    print("\n=== Agent Kai Test ===\n")
    
    # Test planning
    plan = kai.receive_goal(
        "Book a premium workspace for 2 hours",
        context={"duration_hours": 2, "type": "premium"}
    )
    
    # Test delegation
    messages = kai.delegate_to_nav(plan)
    
    print(f"\n✓ Created {len(messages)} A2A messages for delegation")
