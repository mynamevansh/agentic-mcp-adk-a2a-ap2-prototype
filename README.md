# Agentic MCP-ADK-A2A-AP2 Prototype

A production-aligned prototype demonstrating Google's agentic stack: **MCP** (Model Context Protocol), **ADK** (Agent Development Kit), **A2A** (Agent-to-Agent communication), and **AP2** (Agentic Payment Protocol).

## 🎯 Overview

This prototype implements a **multi-agent system** where:
- **Agent Kai** (Planner) receives high-level goals and creates execution plans
- **Agent Nav** (Executor) performs actions using MCP tools and handles payments
- **MCP Server** provides tools and context for agent operations
- **AP2** enables secure agentic payment flows (mocked but protocol-aligned)

## 🏗️ Architecture

```
User Input
    ↓
Agent Kai (Planner - ADK)
    ↓ [A2A Message]
Agent Nav (Executor - ADK)
    ↓
MCP Server (Tools + Context)
    ↓
AP2 Payment Flow (Mock)
```

### Why These Technologies?

#### **MCP (Model Context Protocol)**
- **Purpose**: Standardized protocol for AI agents to access tools and context
- **Why**: Decouples tool implementation from agent logic, enabling reusable, composable tools
- **Usage**: Our MCP server exposes task management, action execution, and payment request tools

#### **ADK (Agent Development Kit)**
- **Purpose**: Framework for building autonomous agents with planning and execution capabilities
- **Why**: Provides structured agent lifecycle, memory, and decision-making primitives
- **Usage**: Both Kai and Nav are ADK-based agents with distinct roles and capabilities

#### **A2A (Agent-to-Agent Communication)**
- **Purpose**: Protocol for structured inter-agent messaging and delegation
- **Why**: Enables agent orchestration, task delegation, and collaborative problem-solving
- **Usage**: Kai delegates execution tasks to Nav using structured A2A messages

#### **AP2 (Agentic Payment Protocol)**
- **Purpose**: Secure, autonomous payment flows for AI agents
- **Why**: Enables agents to transact on behalf of users with proper authorization
- **Usage**: Nav initiates payments when tasks require financial transactions

## 📁 Project Structure

```
agentic-mcp-adk-a2a-ap2-prototype/
├── agents/
│   ├── kai.py              # Planner Agent (ADK)
│   └── nav.py              # Executor Agent (ADK)
├── mcp_server/
│   └── server.py           # MCP Tool Server
├── ap2/
│   └── payment_mock.py     # AP2 Payment Mock
├── demo_flow.py            # End-to-End Demo
├── requirements.txt        # Python Dependencies
├── README.md               # This file
└── docs/
    └── architecture.md     # Detailed Architecture
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip or uv package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/mynamevansh/agentic-mcp-adk-a2a-ap2-prototype.git
cd agentic-mcp-adk-a2a-ap2-prototype

# Install dependencies
pip install -r requirements.txt
```

### Run the Demo

```bash
python demo_flow.py
```

### Expected Output

The demo will show:
1. **User Goal** → Agent Kai receives the request
2. **Planning Phase** → Kai breaks down the goal into steps
3. **A2A Delegation** → Kai sends tasks to Nav
4. **MCP Tool Execution** → Nav calls MCP tools
5. **AP2 Payment Flow** → Payment intent, authorization, confirmation
6. **Completion** → Final status and results

## 🎬 Demo Scenario

**User Goal**: "Book a premium workspace for 2 hours"

**Flow**:
1. Kai plans: Create task → Find workspace → Request payment → Confirm booking
2. Kai delegates to Nav via A2A
3. Nav executes:
   - Calls `create_task` (MCP)
   - Calls `execute_action` with "find_workspace" (MCP)
   - Initiates `request_payment` for $50 (MCP → AP2)
   - Confirms booking after payment authorization
4. AP2 mock simulates secure payment flow
5. Results returned to user

## 🔧 Component Details

### Agent Kai (Planner)
- **Role**: Strategic planning and task decomposition
- **Capabilities**:
  - Accepts natural language goals
  - Breaks goals into actionable steps
  - Delegates to Agent Nav using A2A protocol
  - Monitors execution progress

### Agent Nav (Executor)
- **Role**: Task execution and tool orchestration
- **Capabilities**:
  - Receives A2A task messages
  - Calls MCP tools to perform actions
  - Handles AP2 payment flows
  - Returns execution status and results

### MCP Server
- **Tools Exposed**:
  - `create_task(task_name, metadata)` - Task creation and tracking
  - `execute_action(action_name, parameters)` - Generic action executor
  - `request_payment(amount, purpose)` - Payment initiation

### AP2 Mock
- **Payment Flow**:
  1. **Intent Creation** - Generate payment intent with amount and purpose
  2. **Authorization** - Simulate user/agent authorization
  3. **Confirmation** - Return payment receipt with transaction ID

## 🎓 Key Learnings

### What Works Well
- **Separation of Concerns**: Planner vs. Executor roles are clear
- **Tool Abstraction**: MCP makes tools reusable across agents
- **A2A Messaging**: Structured delegation enables scalability
- **Payment Integration**: AP2 mock shows how agents can transact

### Prototype Limitations
- **No Persistent Storage**: In-memory state only
- **Mock AP2**: Real AP2 would require secure key management and blockchain/payment gateway integration
- **Single-User**: No multi-tenancy or user authentication
- **Synchronous Flow**: No async task queuing or parallel execution
- **Limited Error Handling**: Basic error propagation only

## 🚧 Next Steps (Production Roadmap)

### Phase 1: Robustness
- [ ] Add persistent storage (SQLite/PostgreSQL)
- [ ] Implement comprehensive error handling and retries
- [ ] Add logging and observability (OpenTelemetry)
- [ ] Create unit and integration tests

### Phase 2: Real Integrations
- [ ] Integrate real AP2 payment gateway
- [ ] Connect to production MCP servers
- [ ] Add authentication and authorization
- [ ] Implement rate limiting and quotas

### Phase 3: Scale
- [ ] Add async task queue (Celery/RQ)
- [ ] Support multiple concurrent users
- [ ] Implement agent memory and learning
- [ ] Add web UI for monitoring and control

### Phase 4: Advanced Features
- [ ] Multi-agent collaboration (more than 2 agents)
- [ ] Dynamic tool discovery and registration
- [ ] Agent reputation and trust scoring
- [ ] Advanced payment flows (escrow, recurring, conditional)

## 📚 Additional Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [ADK Documentation](https://github.com/google/adk)
- [A2A Protocol](https://github.com/google/a2a)
- [AP2 Overview](https://github.com/google/ap2)

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

Built by Vansh as a production-aligned prototype for demonstrating Google's agentic stack.

---

**Note**: This is a prototype designed for demonstration and learning. For production use, implement proper security, error handling, monitoring, and testing as outlined in the "Next Steps" section.
