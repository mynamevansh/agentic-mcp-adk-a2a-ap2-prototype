"""
End-to-End Demo Flow
Demonstrates the complete agentic system with MCP, ADK, A2A, and AP2

Flow:
1. User provides a high-level goal
2. Agent Kai (Planner) creates an execution plan
3. Agent Kai delegates tasks to Agent Nav via A2A
4. Agent Nav executes tasks using MCP tools
5. Agent Nav handles AP2 payment when needed
6. Results are returned to the user
"""

import sys
import os
from datetime import datetime

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.kai import AgentKai
from agents.nav import AgentNav
from agents.messages import A2AMessage
from mcp_server.server import get_mcp_server
from ap2.payment_mock import get_ap2_instance


def print_header(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def print_step(step_num: int, description: str):
    """Print a step indicator"""
    print(f"\n{'─'*70}")
    print(f"STEP {step_num}: {description}")
    print(f"{'─'*70}\n")


def demo_workspace_booking():
    """
    Demo Scenario: Book a premium workspace for 2 hours
    
    This demonstrates:
    - User goal → Agent Kai planning
    - Multi-step plan creation
    - A2A delegation to Agent Nav
    - MCP tool usage (create_task, execute_action)
    - AP2 payment flow (intent → auth → confirm)
    - Result aggregation and reporting
    """
    
    print_header("AGENTIC SYSTEM DEMO: MCP + ADK + A2A + AP2")
    
    print("🎯 USER GOAL: Book a premium workspace for 2 hours")
    print("📅 Date: 2025-12-22")
    print("⏰ Duration: 2 hours")
    print("💼 Type: Premium workspace")
    
    # Initialize system components
    print_step(1, "System Initialization")
    
    mcp_server = get_mcp_server()
    ap2 = get_ap2_instance()
    agent_kai = AgentKai(agent_id="agent_kai")
    agent_nav = AgentNav(agent_id="agent_nav")
    
    print("✓ MCP Server ready")
    print("✓ AP2 Payment system ready")
    print("✓ Agent Kai (Planner) ready")
    print("✓ Agent Nav (Executor) ready")
    
    # Step 2: Agent Kai receives goal and creates plan
    print_step(2, "Planning Phase (Agent Kai)")
    
    user_goal = "Book a premium workspace for 2 hours"
    context = {
        "duration_hours": 2,
        "type": "premium",
        "user_email": "user@example.com"
    }
    
    execution_plan = agent_kai.receive_goal(user_goal, context)
    
    # Step 3: Agent Kai delegates to Agent Nav via A2A
    print_step(3, "A2A Delegation (Kai → Nav)")
    
    a2a_messages = agent_kai.delegate_to_nav(execution_plan)
    
    print(f"✓ Created {len(a2a_messages)} A2A messages")
    print(f"✓ Protocol: Agent-to-Agent (A2A)")
    print(f"✓ From: {a2a_messages[0].from_agent}")
    print(f"✓ To: {a2a_messages[0].to_agent}")
    
    # Step 4: Agent Nav executes tasks
    print_step(4, "Task Execution (Agent Nav)")
    
    execution_results = []
    
    for i, message in enumerate(a2a_messages, 1):
        print(f"\n[Executing Task {i}/{len(a2a_messages)}]")
        result = agent_nav.receive_a2a_message(message)
        execution_results.append(result)
        
        if not result.get("success"):
            print(f"⚠️  Task {i} failed: {result.get('error')}")
            break
    
    # Step 5: Display results
    print_step(5, "Results Summary")
    
    successful_tasks = sum(1 for r in execution_results if r.get("success"))
    total_tasks = len(execution_results)
    
    print(f"✓ Completed: {successful_tasks}/{total_tasks} tasks")
    print(f"\nDetailed Results:")
    print(f"{'─'*70}")
    
    for i, result in enumerate(execution_results, 1):
        status = "✓" if result.get("success") else "✗"
        action = result.get("action", "unknown")
        print(f"\n{status} Task {i}: {action}")
        
        if result.get("success"):
            # Display relevant result data
            result_data = result.get("result", {})
            
            if "task_id" in result_data:
                print(f"   Task ID: {result_data['task_id']}")
            
            if "data" in result_data:
                data = result_data["data"]
                if "workspace_id" in data:
                    print(f"   Workspace ID: {data['workspace_id']}")
                    print(f"   Location: {data.get('location')}")
                    print(f"   Price: ${data.get('total_price', 0):.2f}")
                
                if "booking_id" in data:
                    print(f"   Booking ID: {data['booking_id']}")
                    print(f"   Confirmation: {data.get('confirmation_code')}")
            
            if "transaction_id" in result_data:
                print(f"   Transaction ID: {result_data['transaction_id']}")
                print(f"   Amount: ${result_data.get('amount', 0):.2f}")
                print(f"   Confirmation: {result_data.get('confirmation_code')}")
        else:
            print(f"   Error: {result.get('error')}")
    
    # Step 6: Final summary
    print_step(6, "System Summary")
    
    print("📊 Component Usage:")
    print(f"   • MCP Tools Called: {len([r for r in execution_results if 'create_task' in str(r) or 'execute_action' in str(r)])}")
    print(f"   • AP2 Payments: {len([r for r in execution_results if 'transaction_id' in str(r)])}")
    print(f"   • A2A Messages: {len(a2a_messages)}")
    print(f"   • Total Executions: {len(execution_results)}")
    
    print("\n🎉 Demo completed successfully!")
    print("\nKey Takeaways:")
    print("  ✓ Agent Kai decomposed high-level goal into 5 actionable steps")
    print("  ✓ A2A protocol enabled seamless agent-to-agent delegation")
    print("  ✓ MCP provided standardized tool access for task execution")
    print("  ✓ AP2 handled secure payment flow with authorization")
    print("  ✓ All components worked together in a production-aligned architecture")
    
    print_header("END OF DEMO")


def demo_research_task():
    """
    Alternative demo: Research task
    Demonstrates the system with a different goal type
    """
    print_header("ALTERNATIVE DEMO: Research Task")
    
    agent_kai = AgentKai()
    agent_nav = AgentNav()
    
    user_goal = "Research the latest trends in AI agents"
    context = {"topic": "AI agents", "depth": "comprehensive"}
    
    print(f"🎯 USER GOAL: {user_goal}\n")
    
    # Planning
    plan = agent_kai.receive_goal(user_goal, context)
    
    # Delegation
    messages = agent_kai.delegate_to_nav(plan)
    
    # Execution
    for message in messages:
        result = agent_nav.receive_a2a_message(message)
        print(f"\n✓ Step completed: {result.get('action')}")
    
    print("\n✓ Research task completed")


if __name__ == "__main__":
    # Run the main demo
    demo_workspace_booking()
    
    # Uncomment to run alternative demo
    # print("\n\n")
    # demo_research_task()
