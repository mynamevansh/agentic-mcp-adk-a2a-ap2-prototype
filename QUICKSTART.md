# Quick Start Guide

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/mynamevansh/agentic-mcp-adk-a2a-ap2-prototype.git
cd agentic-mcp-adk-a2a-ap2-prototype
```

2. **Install dependencies** (optional - no external dependencies required for basic demo):
```bash
pip install -r requirements.txt
```

Note: The prototype runs with Python standard library only. The requirements.txt lists dependencies for production enhancements.

## Running the Demo

### Main Demo (Workspace Booking)
```bash
python demo_flow.py
```

This will demonstrate:
- ✓ Agent Kai creating a 5-step execution plan
- ✓ A2A delegation from Kai to Nav
- ✓ MCP tool calls (create_task, execute_action)
- ✓ AP2 payment flow (intent → authorization → confirmation)
- ✓ Complete booking with confirmation code

### Test Individual Components

**Test MCP Server**:
```bash
python mcp_server/server.py
```

**Test AP2 Payment**:
```bash
python ap2/payment_mock.py
```

**Test Agent Kai**:
```bash
python agents/kai.py
```

**Test Agent Nav**:
```bash
python agents/nav.py
```

## Expected Output

When you run `python demo_flow.py`, you should see:

```
======================================================================
  AGENTIC SYSTEM DEMO: MCP + ADK + A2A + AP2
======================================================================

🎯 USER GOAL: Book a premium workspace for 2 hours
📅 Date: 2025-12-22
⏰ Duration: 2 hours
💼 Type: Premium workspace

──────────────────────────────────────────────────────────────────────
STEP 1: System Initialization
──────────────────────────────────────────────────────────────────────

[MCP Server] Initialized with tools: create_task, execute_action, request_payment
[AP2 Mock] Payment protocol initialized
[Agent Kai] 🧠 Planner agent initialized (ID: agent_kai)
[Agent Nav] ⚡ Executor agent initialized (ID: agent_nav)
✓ MCP Server ready
✓ AP2 Payment system ready
✓ Agent Kai (Planner) ready
✓ Agent Nav (Executor) ready

──────────────────────────────────────────────────────────────────────
STEP 2: Planning Phase (Agent Kai)
──────────────────────────────────────────────────────────────────────

[Agent Kai] 📋 Received goal: 'Book a premium workspace for 2 hours'
[Agent Kai] 🤔 Analyzing and creating execution plan...
[Agent Kai] ✓ Plan created with 5 steps

============================================================
EXECUTION PLAN: PLAN-xxxxxxxx
Goal: Book a premium workspace for 2 hours
============================================================

Step 1: create_task
  Description: Create booking task in system
  Assigned to: agent_nav
  Parameters: {...}

Step 2: find_workspace (depends on: [1])
  Description: Search for available workspace
  Assigned to: agent_nav
  Parameters: {...}

Step 3: request_payment (depends on: [2])
  Description: Process payment for booking
  Assigned to: agent_nav
  Parameters: {...}

Step 4: confirm_booking (depends on: [3])
  Description: Finalize workspace booking
  Assigned to: agent_nav
  Parameters: {...}

Step 5: send_notification (depends on: [4])
  Description: Send confirmation to user
  Assigned to: agent_nav
  Parameters: {...}

──────────────────────────────────────────────────────────────────────
STEP 3: A2A Delegation (Kai → Nav)
──────────────────────────────────────────────────────────────────────

[Agent Kai] 📤 Delegating plan to Agent Nav via A2A...
[Agent Kai] → Step 1: create_task → Agent Nav
[Agent Kai] → Step 2: find_workspace → Agent Nav
[Agent Kai] → Step 3: request_payment → Agent Nav
[Agent Kai] → Step 4: confirm_booking → Agent Nav
[Agent Kai] → Step 5: send_notification → Agent Nav
[Agent Kai] ✓ Delegated 5 tasks to Agent Nav

──────────────────────────────────────────────────────────────────────
STEP 4: Task Execution (Agent Nav)
──────────────────────────────────────────────────────────────────────

[Executing Task 1/5]
[Agent Nav] 📨 Received A2A message from agent_kai
[Agent Nav] 🎯 Executing Step 1: create_task
[MCP Server] ✓ Task created: Book premium workspace
[Agent Nav] ✓ Step 1 completed successfully

[Executing Task 2/5]
[Agent Nav] 📨 Received A2A message from agent_kai
[Agent Nav] 🎯 Executing Step 2: find_workspace
[MCP Server] Executing action: find_workspace
[MCP Server] ✓ Action completed: find_workspace
[Agent Nav] ✓ Step 2 completed successfully

[Executing Task 3/5]
[Agent Nav] 📨 Received A2A message from agent_kai
[Agent Nav] 🎯 Executing Step 3: request_payment
[Agent Nav] 💳 Initiating AP2 payment flow
[AP2 Mock] 💳 Payment intent created: PAY-xxxxxxxx
[AP2 Mock] ✓ Payment authorized: PAY-xxxxxxxx
[AP2 Mock] ✓ Payment completed: PAY-xxxxxxxx
[Agent Nav] ✓ Payment completed successfully
[Agent Nav] ✓ Step 3 completed successfully

[Executing Task 4/5]
[Agent Nav] 📨 Received A2A message from agent_kai
[Agent Nav] 🎯 Executing Step 4: confirm_booking
[MCP Server] Executing action: confirm_booking
[MCP Server] ✓ Action completed: confirm_booking
[Agent Nav] ✓ Step 4 completed successfully

[Executing Task 5/5]
[Agent Nav] 📨 Received A2A message from agent_kai
[Agent Nav] 🎯 Executing Step 5: send_notification
[MCP Server] Executing action: send_notification
[MCP Server] ✓ Action completed: send_notification
[Agent Nav] ✓ Step 5 completed successfully

──────────────────────────────────────────────────────────────────────
STEP 5: Results Summary
──────────────────────────────────────────────────────────────────────

✓ Completed: 5/5 tasks

Detailed Results:
──────────────────────────────────────────────────────────────────────

✓ Task 1: create_task
   Task ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

✓ Task 2: find_workspace
   Workspace ID: WS-xxxxxxxx
   Location: Downtown Tech Hub
   Price: $50.00

✓ Task 3: request_payment
   Transaction ID: TXN-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   Amount: $50.00
   Confirmation: XXXXXXXX

✓ Task 4: confirm_booking
   Booking ID: BK-xxxxxxxx
   Confirmation: XXXXXX

✓ Task 5: send_notification

──────────────────────────────────────────────────────────────────────
STEP 6: System Summary
──────────────────────────────────────────────────────────────────────

📊 Component Usage:
   • MCP Tools Called: 4
   • AP2 Payments: 1
   • A2A Messages: 5
   • Total Executions: 5

🎉 Demo completed successfully!

Key Takeaways:
  ✓ Agent Kai decomposed high-level goal into 5 actionable steps
  ✓ A2A protocol enabled seamless agent-to-agent delegation
  ✓ MCP provided standardized tool access for task execution
  ✓ AP2 handled secure payment flow with authorization
  ✓ All components worked together in a production-aligned architecture

======================================================================
  END OF DEMO
======================================================================
```

## Understanding the Output

### Key Components Demonstrated

1. **Agent Kai (Planner)**
   - Receives: "Book a premium workspace for 2 hours"
   - Creates: 5-step execution plan with dependencies
   - Delegates: Tasks to Agent Nav via A2A messages

2. **Agent Nav (Executor)**
   - Receives: 5 A2A task delegation messages
   - Executes: Each step using MCP tools or AP2
   - Returns: Results for each step

3. **MCP Server**
   - Provides: create_task, execute_action tools
   - Handles: Workspace search, booking confirmation, notifications

4. **AP2 Payment**
   - Creates: Payment intent for $50
   - Authorizes: Payment with risk scoring
   - Confirms: Payment with transaction ID and confirmation code

### Data Flow

```
User Goal
  → Agent Kai (Planning)
    → A2A Messages (Delegation)
      → Agent Nav (Execution)
        → MCP Tools (Actions)
        → AP2 (Payments)
          → Results
```

## Customizing the Demo

### Change the Goal

Edit `demo_flow.py` and modify:

```python
user_goal = "Your custom goal here"
context = {
    "duration_hours": 3,  # Change duration
    "type": "standard",   # Change workspace type
    "user_email": "your@email.com"
}
```

### Add New Actions

1. Add action handler in `mcp_server/server.py`:
```python
def _your_action(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    # Your logic here
    return {"result": "success"}

# Register in __init__
self.action_handlers["your_action"] = self._your_action
```

2. Update planning logic in `agents/kai.py` to include your action

### Test Different Scenarios

Uncomment the alternative demo in `demo_flow.py`:

```python
if __name__ == "__main__":
    demo_workspace_booking()
    
    # Uncomment to run alternative demo
    print("\n\n")
    demo_research_task()
```

## Troubleshooting

### Import Errors
Make sure you're running from the project root directory:
```bash
cd agentic-mcp-adk-a2a-ap2-prototype
python demo_flow.py
```

### Python Version
Requires Python 3.9+. Check your version:
```bash
python --version
```

### Module Not Found
Ensure `__init__.py` files exist in:
- `agents/`
- `mcp_server/`
- `ap2/`

## Next Steps

1. **Read the Architecture**: See `docs/architecture.md` for detailed system design
2. **Explore Components**: Run individual component tests
3. **Modify and Experiment**: Try different goals and scenarios
4. **Production Path**: Follow the roadmap in `docs/architecture.md`

## Support

For issues or questions:
- Check `docs/architecture.md` for detailed documentation
- Review component code for implementation details
- Examine demo output for debugging information

---

**Happy Coding! 🚀**
