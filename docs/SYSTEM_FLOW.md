# System Flow Visualization

## Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER REQUEST                              │
│                "Book a premium workspace for 2 hours"               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Natural Language Goal
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        AGENT KAI (PLANNER)                          │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │  1. Goal Analysis                                               │ │
│ │     • Parse: "Book workspace"                                   │ │
│ │     • Extract: duration=2h, type=premium                        │ │
│ │                                                                 │ │
│ │  2. Plan Generation                                             │ │
│ │     • Step 1: Create task                                       │ │
│ │     • Step 2: Find workspace (depends on 1)                     │ │
│ │     • Step 3: Process payment (depends on 2)                    │ │
│ │     • Step 4: Confirm booking (depends on 3)                    │ │
│ │     • Step 5: Send notification (depends on 4)                  │ │
│ │                                                                 │ │
│ │  3. A2A Message Creation                                        │ │
│ │     • Generate 5 task delegation messages                       │ │
│ │     • Include: plan_id, step details, dependencies              │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ A2A Messages (5 messages)
                             │ Protocol: Agent-to-Agent
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        AGENT NAV (EXECUTOR)                         │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │  Message Processing Loop (5 iterations)                         │ │
│ │                                                                 │ │
│ │  For each A2A message:                                          │ │
│ │    1. Parse message payload                                     │ │
│ │    2. Extract step details                                      │ │
│ │    3. Resolve parameter references (${stepX.field})             │ │
│ │    4. Route to appropriate handler:                             │ │
│ │       • MCP tools (create_task, execute_action)                 │ │
│ │       • AP2 payment flow                                        │ │
│ │    5. Store result in execution context                         │ │
│ │    6. Return execution status                                   │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└───────────┬─────────────────────────────────┬───────────────────────┘
            │                                 │
            │ MCP Protocol                    │ AP2 Protocol
            ▼                                 ▼
┌───────────────────────────┐    ┌──────────────────────────────────┐
│      MCP SERVER           │    │       AP2 PAYMENT MOCK           │
│                           │    │                                  │
│  Step 1: create_task      │    │  Step 3: Payment Flow            │
│  ┌─────────────────────┐  │    │  ┌────────────────────────────┐  │
│  │ • Generate task_id  │  │    │  │ 1. Create Intent           │  │
│  │ • Store metadata    │  │    │  │    • payment_id: PAY-xxx   │  │
│  │ • Return: task_id   │  │    │  │    • amount: $50.00        │  │
│  └─────────────────────┘  │    │  │    • purpose: "Workspace"  │  │
│                           │    │  │                            │  │
│  Step 2: find_workspace   │    │  │ 2. Authorize               │  │
│  ┌─────────────────────┐  │    │  │    • auth_id: AUTH-xxx     │  │
│  │ • Search workspace  │  │    │  │    • risk_score: 0.15      │  │
│  │ • Calculate price   │  │    │  │    • authorized_by: nav    │  │
│  │ • Return: WS-xxx    │  │    │  │                            │  │
│  │   price: $50        │  │    │  │ 3. Confirm                 │  │
│  └─────────────────────┘  │    │  │    • txn_id: TXN-xxx       │  │
│                           │    │  │    • receipt_id: RCP-xxx   │  │
│  Step 4: confirm_booking  │    │  │    • confirmation: ABC123  │  │
│  ┌─────────────────────┐  │    │  └────────────────────────────┘  │
│  │ • Link workspace    │  │    │                                  │
│  │ • Link payment      │  │    │  Security Features:              │
│  │ • Generate code     │  │    │  • Risk scoring                  │
│  │ • Return: BK-xxx    │  │    │  • Authorization check           │
│  └─────────────────────┘  │    │  • Transaction logging           │
│                           │    │                                  │
│  Step 5: send_notification│    └──────────────────────────────────┘
│  ┌─────────────────────┐  │
│  │ • Format message    │  │
│  │ • Send to user      │  │
│  │ • Return: NT-xxx    │  │
│  └─────────────────────┘  │
│                           │
│  Tool Registry:           │
│  • create_task            │
│  • execute_action         │
│  • request_payment        │
└───────────────────────────┘

                             │
                             │ Results Flow
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         RESULTS AGGREGATION                         │
│                                                                     │
│  ✓ Task Created: task_id = xxxxxxxx                                │
│  ✓ Workspace Found: WS-12345678 @ Downtown Tech Hub ($50)          │
│  ✓ Payment Processed: TXN-xxxxxxxx (Confirmation: ABC12345)        │
│  ✓ Booking Confirmed: BK-12345678 (Code: XYZ123)                   │
│  ✓ Notification Sent: NT-12345678                                  │
│                                                                     │
│  Summary:                                                           │
│  • 5/5 tasks completed successfully                                │
│  • Total execution time: ~2-3 seconds                              │
│  • MCP tools called: 4 times                                       │
│  • AP2 payments: 1 transaction                                     │
│  • A2A messages: 5 delegations                                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Final Response
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            USER RESULT                              │
│                                                                     │
│  🎉 Workspace Booking Confirmed!                                    │
│                                                                     │
│  Workspace: WS-12345678                                             │
│  Location: Downtown Tech Hub                                        │
│  Duration: 2 hours                                                  │
│  Price: $50.00                                                      │
│  Booking Code: XYZ123                                               │
│  Payment: Confirmed (TXN-xxxxxxxx)                                  │
│  Confirmation: ABC12345                                             │
│                                                                     │
│  Check-in: 2025-12-22 18:00:00 UTC                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Timeline

```
T+0ms    │ User submits goal
         │
T+50ms   │ Agent Kai receives goal
         │ ├─ Analyzes intent
         │ ├─ Generates 5-step plan
         │ └─ Creates A2A messages
         │
T+100ms  │ Agent Nav receives Message 1
         │ ├─ Calls MCP: create_task
         │ └─ Returns task_id
         │
T+200ms  │ Agent Nav receives Message 2
         │ ├─ Calls MCP: find_workspace
         │ └─ Returns workspace details
         │
T+300ms  │ Agent Nav receives Message 3
         │ ├─ Initiates AP2 payment
         │ ├─ Creates payment intent
         │ ├─ Authorizes payment (risk check)
         │ ├─ Confirms payment
         │ └─ Returns receipt
         │
T+400ms  │ Agent Nav receives Message 4
         │ ├─ Resolves ${step2.workspace_id}
         │ ├─ Resolves ${step3.payment_id}
         │ ├─ Calls MCP: confirm_booking
         │ └─ Returns booking confirmation
         │
T+500ms  │ Agent Nav receives Message 5
         │ ├─ Calls MCP: send_notification
         │ └─ Returns notification status
         │
T+550ms  │ Results aggregated
         │ └─ Final response to user
```

## Component Interaction Matrix

```
┌──────────────┬─────────┬─────────┬────────────┬──────────┐
│              │ Kai     │ Nav     │ MCP Server │ AP2      │
├──────────────┼─────────┼─────────┼────────────┼──────────┤
│ Kai          │    -    │  A2A    │     -      │    -     │
│ Nav          │  A2A    │    -    │    MCP     │   AP2    │
│ MCP Server   │    -    │  MCP    │     -      │    -     │
│ AP2          │    -    │  AP2    │     -      │    -     │
└──────────────┴─────────┴─────────┴────────────┴──────────┘

Legend:
  A2A = Agent-to-Agent Protocol
  MCP = Model Context Protocol
  AP2 = Agentic Payment Protocol
```

## Message Format Examples

### A2A Message (Kai → Nav)
```json
{
  "message_id": "MSG-a1b2c3d4",
  "from_agent": "agent_kai",
  "to_agent": "agent_nav",
  "message_type": "task_delegation",
  "payload": {
    "plan_id": "PLAN-12345678",
    "step": {
      "step_number": 3,
      "action": "request_payment",
      "description": "Process payment for booking",
      "parameters": {
        "amount": 50.0,
        "purpose": "premium workspace for 2h"
      },
      "dependencies": [2],
      "assigned_to": "agent_nav"
    },
    "goal": "Book a premium workspace for 2 hours"
  },
  "timestamp": "2025-12-22T16:10:42Z"
}
```

### MCP Request
```json
{
  "tool": "execute_action",
  "parameters": {
    "action_name": "find_workspace",
    "parameters": {
      "duration_hours": 2,
      "type": "premium"
    }
  }
}
```

### MCP Response
```json
{
  "success": true,
  "action_name": "find_workspace",
  "data": {
    "workspace_id": "WS-12345678",
    "type": "premium",
    "duration_hours": 2,
    "price_per_hour": 25.0,
    "total_price": 50.0,
    "location": "Downtown Tech Hub",
    "amenities": ["WiFi", "Desk", "Coffee"]
  },
  "timestamp": "2025-12-22T16:10:42.200Z"
}
```

### AP2 Payment Receipt
```json
{
  "success": true,
  "receipt_id": "RCP-a1b2c3d4",
  "payment_id": "PAY-x1y2z3w4",
  "transaction_id": "TXN-m5n6o7p8",
  "amount": 50.0,
  "currency": "USD",
  "status": "completed",
  "completed_at": "2025-12-22T16:10:42.350Z",
  "confirmation_code": "ABC12345",
  "purpose": "premium workspace for 2h"
}
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────┐
│              Error Occurs in Any Component          │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  Catch Exception   │
         └────────┬───────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  Log Error Details │
         └────────┬───────────┘
                  │
                  ▼
         ┌────────────────────┐
         │ Return Error Result│
         │ {                  │
         │   success: false,  │
         │   error: "...",    │
         │   step: X          │
         │ }                  │
         └────────┬───────────┘
                  │
                  ▼
         ┌────────────────────┐
         │ Agent Nav Reports  │
         │ Failure to Kai     │
         └────────┬───────────┘
                  │
                  ▼
         ┌────────────────────┐
         │ User Receives      │
         │ Error Message      │
         └────────────────────┘
```

## State Management

```
Agent Kai State:
├─ plans: Dict[plan_id, ExecutionPlan]
├─ message_history: List[A2AMessage]
└─ agent_id: str

Agent Nav State:
├─ executions: Dict[execution_id, TaskExecution]
├─ execution_context: Dict[step_ref, result]
├─ message_history: List[A2AMessage]
└─ agent_id: str

MCP Server State:
├─ tasks: Dict[task_id, Task]
└─ action_handlers: Dict[action_name, callable]

AP2 State:
├─ payment_intents: Dict[payment_id, PaymentIntent]
├─ authorizations: Dict[auth_id, PaymentAuthorization]
└─ receipts: Dict[receipt_id, PaymentReceipt]
```

---

**This visualization demonstrates the complete system architecture and data flow for the agentic prototype.**
