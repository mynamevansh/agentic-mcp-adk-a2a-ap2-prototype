# System Architecture Documentation

## Overview

This prototype demonstrates a **production-aligned multi-agent system** using Google's agentic stack:

- **MCP** (Model Context Protocol) - Standardized tool and context access
- **ADK** (Agent Development Kit) - Agent framework with planning and execution
- **A2A** (Agent-to-Agent) - Inter-agent communication protocol
- **AP2** (Agentic Payment Protocol) - Autonomous payment flows

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INPUT                          │
│                  "Book a workspace for 2h"                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    AGENT KAI (Planner)                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ • Goal Understanding                                  │  │
│  │ • Task Decomposition                                  │  │
│  │ • Multi-step Planning                                 │  │
│  │ • Creates: 5-step execution plan                      │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ A2A Messages
                         │ (Agent-to-Agent Protocol)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    AGENT NAV (Executor)                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ • Receives A2A task delegations                       │  │
│  │ • Orchestrates tool execution                         │  │
│  │ • Handles payment flows                               │  │
│  │ • Returns results                                     │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────┬─────────────────────────────┬───────────────────┘
            │                             │
            │ MCP Protocol                │ AP2 Protocol
            ▼                             ▼
┌───────────────────────────┐   ┌─────────────────────────────┐
│      MCP SERVER           │   │      AP2 PAYMENT MOCK       │
│  ┌─────────────────────┐  │   │  ┌───────────────────────┐  │
│  │ Tools:              │  │   │  │ Payment Flow:         │  │
│  │ • create_task       │  │   │  │ 1. Create Intent      │  │
│  │ • execute_action    │  │   │  │ 2. Authorize          │  │
│  │ • request_payment   │  │   │  │ 3. Confirm            │  │
│  └─────────────────────┘  │   │  │ 4. Return Receipt     │  │
│                           │   │  └───────────────────────┘  │
│  Context & State Mgmt     │   │  Risk Scoring & Security    │
└───────────────────────────┘   └─────────────────────────────┘
```

## Component Details

### 1. Agent Kai (Planner)

**File**: `agents/kai.py`

**Responsibilities**:
- Accept high-level user goals in natural language
- Decompose goals into structured, actionable steps
- Create execution plans with dependencies
- Delegate tasks to Agent Nav using A2A protocol
- Monitor execution progress (in production)

**Key Methods**:
- `receive_goal(goal, context)` - Process user input and create plan
- `_create_plan(goal, context)` - Planning algorithm
- `delegate_to_nav(plan)` - Send A2A messages to Agent Nav
- `receive_status_update(message)` - Handle execution updates

**Planning Algorithm**:
```python
Goal → Analysis → Step Decomposition → Dependency Resolution → Plan Creation
```

**Example Plan** (Workspace Booking):
1. Create task in system (MCP: create_task)
2. Find available workspace (MCP: execute_action)
3. Process payment (AP2: payment flow)
4. Confirm booking (MCP: execute_action)
5. Send notification (MCP: execute_action)

**ADK Concepts Implemented**:
- Agent lifecycle management
- Goal-oriented planning
- Memory and context (execution_context)
- Inter-agent communication (A2A)

---

### 2. Agent Nav (Executor)

**File**: `agents/nav.py`

**Responsibilities**:
- Receive task delegations via A2A messages
- Execute actions using MCP tools
- Handle AP2 payment flows end-to-end
- Resolve parameter dependencies between steps
- Return execution results

**Key Methods**:
- `receive_a2a_message(message)` - Process incoming A2A messages
- `_execute_action(step)` - Route actions to appropriate handlers
- `_handle_payment_flow(params)` - Complete AP2 payment (3 steps)
- `_resolve_parameters(params)` - Resolve cross-step references

**Execution Flow**:
```python
A2A Message → Parse Step → Resolve Params → Execute Action → Store Result → Return Status
```

**Parameter Resolution**:
Supports references like `${step2.workspace_id}` to use results from previous steps.

**ADK Concepts Implemented**:
- Task execution engine
- Tool orchestration
- State management (execution_context)
- Error handling and reporting

---

### 3. MCP Server

**File**: `mcp_server/server.py`

**Purpose**: Provide standardized tool access following Model Context Protocol

**Tools Exposed**:

1. **create_task(task_name, metadata)**
   - Creates and tracks tasks
   - Returns: task_id, status, timestamps
   
2. **execute_action(action_name, parameters)**
   - Generic action executor
   - Supports: find_workspace, confirm_booking, send_notification, etc.
   - Returns: action result with data
   
3. **request_payment(amount, purpose)**
   - Initiates payment request
   - Triggers AP2 payment flow
   - Returns: payment_id, status

**Action Handlers**:
- `_find_workspace` - Simulates workspace search
- `_confirm_booking` - Simulates booking confirmation
- `_send_notification` - Simulates notification delivery

**MCP Protocol Benefits**:
- Decouples tools from agent logic
- Enables tool reusability across agents
- Standardized interface for context and actions
- Easy to extend with new tools

---

### 4. AP2 Payment Mock

**File**: `ap2/payment_mock.py`

**Purpose**: Simulate secure agentic payment protocol

**Payment Flow**:

```
1. CREATE INTENT
   ├─ Generate payment_id
   ├─ Set amount, currency, purpose
   └─ Status: intent_created

2. AUTHORIZE
   ├─ Verify agent credentials (mocked)
   ├─ Calculate risk score
   ├─ Check spending limits (mocked)
   └─ Status: authorized

3. CONFIRM
   ├─ Process payment (mocked)
   ├─ Generate transaction_id
   ├─ Create receipt with confirmation_code
   └─ Status: completed
```

**Risk Scoring**:
- Base risk: 0.1
- Amount-based risk: amount / 1000 (capped at 0.3)
- Blocks payments with risk > 0.8

**Production Requirements**:
- Secure key management (HSM/KMS)
- Real payment gateway integration
- Fraud detection and prevention
- Compliance and audit logging
- Webhook notifications
- Idempotency for retries

---

### 5. A2A Protocol

**Implementation**: Dataclass in `agents/kai.py` and `agents/nav.py`

**Message Structure**:
```python
{
  "message_id": "MSG-xxx",
  "from_agent": "agent_kai",
  "to_agent": "agent_nav",
  "message_type": "task_delegation",
  "payload": {
    "plan_id": "PLAN-xxx",
    "step": {...},
    "goal": "..."
  },
  "timestamp": "2025-12-22T..."
}
```

**Message Types**:
- `task_delegation` - Kai → Nav: Execute this step
- `status_update` - Nav → Kai: Step completed/failed
- `result` - Nav → Kai: Final results

**Benefits**:
- Structured inter-agent communication
- Enables agent orchestration
- Supports async workflows (in production)
- Facilitates multi-agent collaboration

---

## Data Flow Example

**Scenario**: Book a premium workspace for 2 hours

### Step-by-Step Flow:

```
1. USER → "Book a premium workspace for 2 hours"
   
2. AGENT KAI
   ├─ Receives goal
   ├─ Creates 5-step plan
   └─ Sends 5 A2A messages to Agent Nav

3. AGENT NAV (Step 1)
   ├─ Receives: create_task
   ├─ Calls: MCP.create_task("Book workspace", {...})
   └─ Returns: task_id

4. AGENT NAV (Step 2)
   ├─ Receives: find_workspace
   ├─ Calls: MCP.execute_action("find_workspace", {duration: 2})
   └─ Returns: workspace_id, price=$50

5. AGENT NAV (Step 3)
   ├─ Receives: request_payment
   ├─ Calls: AP2.create_payment_intent($50, "Workspace booking")
   ├─ Calls: AP2.authorize_payment(payment_id)
   ├─ Calls: AP2.confirm_payment(payment_id)
   └─ Returns: transaction_id, confirmation_code

6. AGENT NAV (Step 4)
   ├─ Receives: confirm_booking
   ├─ Resolves: ${step2.workspace_id}, ${step3.payment_id}
   ├─ Calls: MCP.execute_action("confirm_booking", {...})
   └─ Returns: booking_id, confirmation_code

7. AGENT NAV (Step 5)
   ├─ Receives: send_notification
   ├─ Calls: MCP.execute_action("send_notification", {...})
   └─ Returns: notification_id

8. USER ← Results summary with booking confirmation
```

---

## Technology Choices

### Why MCP?
- **Standardization**: Common protocol for tool access
- **Decoupling**: Tools independent of agent implementation
- **Reusability**: Same tools work across different agents
- **Extensibility**: Easy to add new tools without changing agents

### Why ADK?
- **Structure**: Provides agent lifecycle and patterns
- **Planning**: Built-in support for goal decomposition
- **Memory**: Context management across interactions
- **Orchestration**: Enables multi-agent systems

### Why A2A?
- **Delegation**: Enables task distribution across agents
- **Scalability**: Supports complex multi-agent workflows
- **Flexibility**: Agents can specialize in different roles
- **Collaboration**: Structured communication protocol

### Why AP2?
- **Autonomy**: Agents can transact without manual intervention
- **Security**: Proper authorization and risk management
- **Compliance**: Audit trails and regulatory alignment
- **Trust**: Enables real-world agent commerce

---

## Limitations (Prototype)

1. **No Persistent Storage**
   - All state is in-memory
   - Production needs: PostgreSQL, Redis

2. **Synchronous Execution**
   - Tasks execute sequentially
   - Production needs: Async queue (Celery, RQ)

3. **Mock AP2**
   - No real payment processing
   - Production needs: Stripe, blockchain integration

4. **No Authentication**
   - No user auth or agent credentials
   - Production needs: OAuth, JWT, API keys

5. **Limited Error Handling**
   - Basic try/catch only
   - Production needs: Retries, circuit breakers, fallbacks

6. **No Observability**
   - Print statements only
   - Production needs: OpenTelemetry, logging, metrics

---

## Production Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Add PostgreSQL for persistent storage
- [ ] Implement comprehensive error handling
- [ ] Add structured logging (structlog)
- [ ] Create unit and integration tests
- [ ] Add API authentication

### Phase 2: Scale (Weeks 3-4)
- [ ] Implement async task queue
- [ ] Add Redis for caching and state
- [ ] Support concurrent users
- [ ] Add rate limiting and quotas
- [ ] Implement monitoring and alerts

### Phase 3: Integrations (Weeks 5-6)
- [ ] Integrate real payment gateway (Stripe)
- [ ] Connect to production MCP servers
- [ ] Add LLM integration for dynamic planning
- [ ] Implement webhook system
- [ ] Add admin dashboard

### Phase 4: Advanced (Weeks 7-8)
- [ ] Multi-agent collaboration (>2 agents)
- [ ] Agent learning and optimization
- [ ] Dynamic tool discovery
- [ ] Advanced payment flows (escrow, recurring)
- [ ] Compliance and audit system

---

## Security Considerations

### Current (Prototype)
- No authentication
- No encryption
- No input validation
- Mock payment system

### Production Requirements
1. **Authentication & Authorization**
   - API keys for agents
   - OAuth for users
   - Role-based access control (RBAC)

2. **Encryption**
   - TLS for all communications
   - Encrypted storage for sensitive data
   - Key management (AWS KMS, HashiCorp Vault)

3. **Input Validation**
   - Sanitize all user inputs
   - Validate agent messages
   - Rate limiting and DDoS protection

4. **Payment Security**
   - PCI DSS compliance
   - Secure key storage
   - Transaction signing
   - Fraud detection

5. **Audit & Compliance**
   - Complete audit logs
   - Immutable transaction records
   - Regulatory compliance (GDPR, etc.)
   - Incident response plan

---

## Performance Considerations

### Current Performance
- Synchronous execution: ~1-2s per step
- In-memory state: Fast but not persistent
- No caching: Repeated calls not optimized

### Production Optimizations
1. **Async Processing**
   - Use Celery/RQ for background tasks
   - Parallel execution where possible
   - Streaming results for long-running tasks

2. **Caching**
   - Redis for frequently accessed data
   - Cache MCP tool results
   - Cache agent plans for similar goals

3. **Database Optimization**
   - Connection pooling
   - Query optimization
   - Read replicas for scaling

4. **Load Balancing**
   - Multiple agent instances
   - Horizontal scaling
   - Auto-scaling based on load

---

## Testing Strategy

### Unit Tests
- Test each agent method independently
- Mock MCP and AP2 dependencies
- Test parameter resolution logic
- Test error handling paths

### Integration Tests
- Test complete flows end-to-end
- Test A2A message passing
- Test MCP tool integration
- Test AP2 payment flow

### Performance Tests
- Load testing with multiple concurrent users
- Stress testing payment flows
- Latency measurements for each component

### Security Tests
- Penetration testing
- Input fuzzing
- Authentication bypass attempts
- Payment fraud scenarios

---

## Deployment Architecture (Production)

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
    ┌────────▼────────┐          ┌───────▼────────┐
    │  Agent Kai      │          │  Agent Kai     │
    │  Instance 1     │          │  Instance 2    │
    └────────┬────────┘          └───────┬────────┘
             │                            │
    ┌────────▼────────────────────────────▼────────┐
    │            Message Queue (RabbitMQ)          │
    └────────┬────────────────────────────┬────────┘
             │                            │
    ┌────────▼────────┐          ┌───────▼────────┐
    │  Agent Nav      │          │  Agent Nav     │
    │  Instance 1     │          │  Instance 2    │
    └────────┬────────┘          └───────┬────────┘
             │                            │
    ┌────────▼────────────────────────────▼────────┐
    │              MCP Server Cluster              │
    └────────┬────────────────────────────┬────────┘
             │                            │
    ┌────────▼────────┐          ┌───────▼────────┐
    │   PostgreSQL    │          │  Redis Cache   │
    │   (Primary)     │          │                │
    └─────────────────┘          └────────────────┘
```

---

## Monitoring & Observability

### Metrics to Track
- Agent response time
- Task success/failure rate
- Payment success rate
- MCP tool latency
- Queue depth
- Error rates by type

### Logging
- Structured logs (JSON)
- Correlation IDs for tracing
- Log levels: DEBUG, INFO, WARN, ERROR
- Centralized log aggregation (ELK, Datadog)

### Alerts
- High error rates
- Payment failures
- Slow response times
- Queue backlog
- System resource exhaustion

---

## Conclusion

This prototype demonstrates a **production-aligned architecture** using Google's agentic stack. While simplified for demonstration, it follows the correct architectural patterns and can be extended to production with the roadmap outlined above.

**Key Achievements**:
✓ Multi-agent system with clear role separation
✓ Standardized tool access via MCP
✓ Structured inter-agent communication via A2A
✓ Autonomous payment flows via AP2
✓ Clean, readable, demo-friendly code
✓ Comprehensive documentation

**Next Steps**: Follow the production roadmap to add persistence, security, scalability, and real integrations.
