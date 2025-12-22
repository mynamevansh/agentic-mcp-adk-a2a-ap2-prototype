# Web UI for Agentic System

## Overview

This is a **minimal observability dashboard** for the headless agentic system. It provides a web-based interface to visualize agent execution logs without modifying the core agent logic.

## Architecture Philosophy

### Why This Design?

This UI follows production patterns for agent infrastructure:

1. **Separation of Concerns**
   - Agent logic stays in `demo_flow.py` (headless)
   - UI is purely for visualization
   - No business logic in the frontend

2. **Headless-First**
   - System can run via CLI: `python demo_flow.py`
   - UI is an optional observability layer
   - Agents don't depend on the UI

3. **Production Pattern**
   - Mirrors real-world agent systems (e.g., Kubernetes Dashboard, Docker Desktop)
   - UI visualizes but doesn't control
   - Enables multiple interfaces (CLI, Web, API) to same core system

### What This UI Does

✅ Triggers agent execution  
✅ Displays execution logs  
✅ Shows execution status and timing  
✅ Provides system architecture overview  

### What This UI Does NOT Do

❌ Implement agent logic  
❌ Make planning decisions  
❌ Execute MCP tools  
❌ Handle payments  
❌ Store data  
❌ Manage state  

**All agent orchestration happens in `demo_flow.py`**

## File Structure

```
ui/
├── app.py                  # Flask backend (thin wrapper)
├── templates/
│   └── index.html          # Single-page UI
├── static/
│   └── style.css           # Minimal styling
└── README_UI.md            # This file
```

## Installation

### Prerequisites

- Python 3.9+
- Flask (will be installed)

### Install Dependencies

```bash
# From project root
pip install flask
```

Or update `requirements.txt`:
```bash
pip install -r requirements.txt
```

## Running the UI

### Start the Server

```bash
# From project root
cd ui
python app.py
```

You should see:
```
======================================================================
  AGENTIC SYSTEM - WEB UI
======================================================================

🚀 Starting observability dashboard...

📊 This UI visualizes the headless agent system
   - Agent logic runs in demo_flow.py (unchanged)
   - UI captures and displays execution logs
   - System can still run via CLI: python demo_flow.py

🌐 Open your browser to: http://localhost:5000

======================================================================
```

### Access the UI

Open your browser to:
```
http://localhost:5000
```

### Use the Dashboard

1. Click **"▶️ Run Agent Demo"**
2. Watch the logs appear in real-time
3. View execution status and timing
4. Click **"Clear Logs"** to reset

## How It Works

### Backend (`app.py`)

The Flask server provides a thin wrapper around `demo_flow.py`:

```python
@app.route('/run-demo', methods=['POST'])
def run_demo():
    # Execute demo_flow.py as subprocess
    result = subprocess.run(
        [sys.executable, 'demo_flow.py'],
        capture_output=True,
        text=True
    )
    
    # Return logs to frontend
    return jsonify({
        'success': True,
        'logs': result.stdout
    })
```

**Key Points:**
- Uses `subprocess.run()` to execute the existing script
- Captures stdout (all print statements)
- Returns logs as JSON
- No agent logic in the backend

### Frontend (`index.html`)

Simple single-page application:

```javascript
// Send POST request to backend
const response = await fetch('/run-demo', { method: 'POST' });
const data = await response.json();

// Display logs
logOutput.textContent = data.logs;
```

**Key Points:**
- One button to trigger execution
- One log panel to display results
- No frameworks (vanilla HTML/CSS/JS)
- Pure visualization, no logic

## System Flow

```
User clicks "Run Demo"
    ↓
Frontend sends POST /run-demo
    ↓
Backend executes: python demo_flow.py
    ↓
demo_flow.py runs (unchanged):
    - Agent Kai plans
    - Agent Nav executes
    - MCP tools called
    - AP2 payment processed
    ↓
Backend captures stdout logs
    ↓
Backend returns logs to frontend
    ↓
Frontend displays logs in UI
```

## Comparison: CLI vs Web UI

### CLI Execution
```bash
python demo_flow.py
```
- Direct execution
- Logs to terminal
- No overhead
- Scriptable

### Web UI Execution
```bash
python ui/app.py
# Then click button in browser
```
- Visual interface
- Logs in browser
- Shareable (send URL)
- Demo-friendly

**Both use the exact same agent system!**

## Production Deployment

For production use:

1. **Use a Production WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Add Authentication**
   ```python
   from flask_httpauth import HTTPBasicAuth
   # Add auth to /run-demo endpoint
   ```

3. **Add Rate Limiting**
   ```python
   from flask_limiter import Limiter
   # Prevent abuse
   ```

4. **Use Environment Variables**
   ```python
   import os
   PORT = os.getenv('PORT', 5000)
   ```

5. **Add Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   ```

## Extending the UI

### Add More Endpoints

```python
@app.route('/status', methods=['GET'])
def get_status():
    # Return system status
    pass

@app.route('/history', methods=['GET'])
def get_history():
    # Return execution history
    pass
```

### Add WebSocket for Real-Time Logs

```python
from flask_socketio import SocketIO
# Stream logs as they're generated
```

### Add Execution History

```python
# Store executions in SQLite
import sqlite3
# Track all runs
```

## Troubleshooting

### Port Already in Use
```bash
# Change port in app.py
app.run(port=5001)
```

### Cannot Find demo_flow.py
```bash
# Ensure you're running from ui/ directory
cd ui
python app.py
```

### Logs Not Appearing
- Check browser console for errors
- Verify backend is running
- Check that demo_flow.py works via CLI first

## Why This Matters for Recruiters

This UI demonstrates:

1. **Architectural Restraint**
   - Didn't over-engineer the UI
   - Kept focus on the agent system
   - Shows understanding of separation of concerns

2. **Production Patterns**
   - Headless-first design
   - Observability layer pattern
   - Microservices thinking

3. **Full-Stack Skills**
   - Backend: Flask, subprocess management
   - Frontend: HTML/CSS/JS (no framework needed)
   - System integration

4. **Real-World Thinking**
   - UI is optional, not required
   - System works with or without it
   - Multiple interfaces to same core

## Next Steps

- ✅ UI is working
- ✅ Agent system unchanged
- ✅ Both CLI and Web work
- 🚀 Ready to demo!

---

**Remember: The agent system is the star. This UI is just the stage lighting.** 🎭
