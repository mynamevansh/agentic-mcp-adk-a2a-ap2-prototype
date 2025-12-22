"""
Flask Web UI for Agentic System Observability

ARCHITECTURE PHILOSOPHY:
This UI is intentionally thin and serves as a "window" into the headless
agentic system. It does NOT contain any business logic, agent orchestration,
or decision-making capabilities.

WHY THIS DESIGN?
1. Separation of Concerns: Agent logic remains in demo_flow.py (headless)
2. Production Pattern: Real agent systems run independently of UIs
3. Observability: UI is purely for monitoring and visualization
4. Flexibility: System can run via CLI OR web interface without changes

REAL-WORLD ANALOGY:
This is like Kubernetes Dashboard or Docker Desktop - they visualize
what's happening in the underlying system but don't control the logic.

The agent system (demo_flow.py) is the "engine"
This UI is the "dashboard"
"""

from flask import Flask, render_template, jsonify
import subprocess
import sys
import os
from datetime import datetime, timezone

app = Flask(__name__)

# Get the project root directory (parent of ui/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@app.route('/')
def index():
    """
    Serve the main UI page
    
    This is a simple HTML page with:
    - One button to trigger agent execution
    - One log panel to display results
    
    No complex frontend framework needed - this is intentionally minimal
    to keep focus on the agent system, not the UI.
    """
    return render_template('index.html')


@app.route('/run-demo', methods=['POST'])
def run_demo():
    """
    Execute the headless agent system and capture logs
    
    IMPORTANT: This endpoint does NOT implement agent logic.
    It simply:
    1. Runs the existing demo_flow.py script
    2. Captures stdout (logs)
    3. Returns logs to the frontend
    
    The agent orchestration, planning, execution, and payment flows
    all happen in demo_flow.py - this endpoint is just a wrapper.
    
    WHY THIS APPROACH?
    - Agent logic stays independent and testable
    - UI can be added/removed without affecting core system
    - Follows microservices pattern: agents are the service, UI is a client
    - Enables multiple interfaces (CLI, Web, API) to same agent system
    """
    try:
        # Record execution start time
        start_time = datetime.now(timezone.utc)
        
        # Execute demo_flow.py as a subprocess
        # This keeps agent execution isolated and captures all output
        result = subprocess.run(
            [sys.executable, 'demo_flow.py'],
            cwd=PROJECT_ROOT,  # Run from project root
            capture_output=True,
            text=True,
            encoding='utf-8',  # Ensure proper Unicode handling for emojis
            errors='replace',  # Replace problematic characters instead of failing
            timeout=30  # Prevent hanging
        )
        
        # Record execution end time
        end_time = datetime.now(timezone.utc)
        execution_time = (end_time - start_time).total_seconds()
        
        # Check if execution was successful
        if result.returncode == 0:
            # Success: return logs and metadata
            return jsonify({
                'success': True,
                'logs': result.stdout,
                'execution_time': execution_time,
                'timestamp': start_time.isoformat(),
                'message': 'Agent system executed successfully'
            })
        else:
            # Error: return error logs
            return jsonify({
                'success': False,
                'logs': result.stderr or result.stdout,
                'execution_time': execution_time,
                'timestamp': start_time.isoformat(),
                'message': 'Agent system execution failed'
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'logs': 'Execution timeout after 30 seconds',
            'message': 'Agent system execution timed out'
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'logs': str(e),
            'message': f'Error executing agent system: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    
    Useful for monitoring and deployment verification
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Agentic System UI',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })


if __name__ == '__main__':
    print("="*70)
    print("  AGENTIC SYSTEM - WEB UI")
    print("="*70)
    print("\n🚀 Starting observability dashboard...")
    print("\n📊 This UI visualizes the headless agent system")
    print("   - Agent logic runs in demo_flow.py (unchanged)")
    print("   - UI captures and displays execution logs")
    print("   - System can still run via CLI: python demo_flow.py")
    print("\n🌐 Open your browser to: http://localhost:5000")
    print("\n" + "="*70 + "\n")
    
    # Run Flask development server
    # In production, use gunicorn or similar WSGI server
    app.run(
        host='0.0.0.0',  # Allow external access
        port=5000,
        debug=True  # Enable auto-reload during development
    )
