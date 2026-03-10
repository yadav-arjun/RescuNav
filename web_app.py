"""
Simple Web UI for RescuNav Rescue Simulation
"""

from flask import Flask, render_template, request, jsonify, Response
import subprocess
import threading
import queue
import time
import os
import sys

app = Flask(__name__)

# Queue for simulation logs
log_queue = queue.Queue()
simulation_running = False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Fake video upload endpoint"""
    time.sleep(2)  # Simulate upload time
    return jsonify({
        'status': 'success',
        'message': 'Video uploaded successfully',
        'filename': 'main.mp4'
    })

@app.route('/api/start_simulation', methods=['POST'])
def start_simulation():
    """Start the rescue simulation"""
    global simulation_running

    if simulation_running:
        return jsonify({'status': 'error', 'message': 'Simulation already running'})

    simulation_running = True

    # Clear the log queue
    while not log_queue.empty():
        try:
            log_queue.get_nowait()
        except queue.Empty:
            break

    # Start simulation in background thread
    thread = threading.Thread(target=run_simulation)
    thread.daemon = True
    thread.start()

    return jsonify({'status': 'success', 'message': 'Simulation started'})

def run_simulation():
    """Run the rescue simulation and capture output"""
    global simulation_running

    try:
        # Add initial log message
        log_queue.put('Initializing simulation subprocess...')
        
        # Run the simulation command
        # On Windows, we need to use sys.executable to get the correct Python path
        process = subprocess.Popen(
            [sys.executable, 'rescue_simulation.py', '--scenario', 'fire', '--iterations', '3', '--agents', '2'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )

        log_queue.put('Subprocess started, reading output...')

        # Stream output to queue in real-time
        while True:
            line = process.stdout.readline()
            if not line:
                # Check if process has ended
                if process.poll() is not None:
                    break
                continue
            
            log_queue.put(line.rstrip())

        # Get any remaining output
        remaining_output = process.stdout.read()
        if remaining_output:
            for line in remaining_output.split('\n'):
                if line.strip():
                    log_queue.put(line.rstrip())

        # Check for errors
        stderr_output = process.stderr.read()
        if stderr_output:
            log_queue.put('STDERR OUTPUT:')
            for line in stderr_output.split('\n'):
                if line.strip():
                    log_queue.put(line.rstrip())

        # Wait for process to complete
        return_code = process.wait()
        log_queue.put(f'Process completed with return code: {return_code}')
        log_queue.put('--- SIMULATION COMPLETE ---')

    except Exception as e:
        log_queue.put(f'ERROR: {str(e)}')
        import traceback
        log_queue.put(traceback.format_exc())

    finally:
        simulation_running = False

@app.route('/api/logs')
def stream_logs():
    """Stream simulation logs via Server-Sent Events"""
    def generate():
        # Send initial connection message
        yield f"data: Connected to log stream\n\n"
        
        # Wait for simulation to start (with timeout)
        wait_count = 0
        while not simulation_running and wait_count < 20:
            yield f"data: \n\n"  # heartbeat
            time.sleep(0.5)
            wait_count += 1
        
        if not simulation_running:
            yield f"data: Warning: Simulation did not start within 10 seconds\n\n"
        
        # Stream logs
        last_activity = time.time()
        timeout_seconds = 300  # 5 minute timeout
        
        while True:
            try:
                # Get log line with short timeout
                line = log_queue.get(timeout=0.5)
                yield f"data: {line}\n\n"
                last_activity = time.time()
                
                # Check if this is the completion message
                if "SIMULATION COMPLETE" in line:
                    # Wait a bit for any final messages
                    time.sleep(1)
                    # Drain remaining messages
                    while not log_queue.empty():
                        try:
                            line = log_queue.get_nowait()
                            yield f"data: {line}\n\n"
                        except queue.Empty:
                            break
                    break
                    
            except queue.Empty:
                # Send heartbeat to keep connection alive
                yield f"data: \n\n"
                
                # Check for timeout
                if time.time() - last_activity > timeout_seconds:
                    yield f"data: Stream timeout - no activity for {timeout_seconds} seconds\n\n"
                    break
                
                # Only break if simulation is done AND queue is empty
                if not simulation_running and log_queue.empty():
                    # Double check after a short wait
                    time.sleep(0.5)
                    if log_queue.empty():
                        yield f"data: Simulation ended, closing stream\n\n"
                        break

    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'
    })

@app.route('/api/status')
def get_status():
    """Get current simulation status"""
    return jsonify({
        'running': simulation_running,
        'queue_size': log_queue.qsize()
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    print("\n" + "="*70)
    print("RESCUNAV WEB UI")
    print("="*70)
    print("\nStarting web server...")
    print("Open your browser to: http://localhost:5000")
    print("\nPress Ctrl+C to stop")
    print("="*70 + "\n")

    app.run(debug=True, threaded=True, use_reloader=False)
