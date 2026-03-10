// Global state
let animationRunning = false;
let buildingAnimationId = null;
let agentAnimationId = null;
let fireParticles = [];
let agent = null;

// File upload handling
document.getElementById('videoFile').addEventListener('change', async function(e) {
    if (e.target.files.length === 0) return;

    const file = e.target.files[0];

    // Hide placeholder
    document.getElementById('uploadPlaceholder').style.display = 'none';
    document.getElementById('uploadProgress').style.display = 'block';

    // Simulate upload progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 20;
        if (progress > 100) progress = 100;
        document.getElementById('progressFill').style.width = progress + '%';

        if (progress >= 100) {
            clearInterval(progressInterval);
            setTimeout(() => {
                document.getElementById('uploadProgress').style.display = 'none';
                document.getElementById('uploadSuccess').style.display = 'block';

                // Enable step 2
                document.getElementById('step2').style.opacity = '1';
                document.getElementById('step2').style.pointerEvents = 'auto';
                document.getElementById('step1').classList.add('active');

                addLog('Video uploaded successfully: main.mp4', 'success');
            }, 500);
        }
    }, 200);
});

// Start simulation
async function startSimulation() {
    const btn = document.getElementById('startBtn');
    btn.disabled = true;
    btn.textContent = 'Running...';

    addLog('='.repeat(70), 'info');
    addLog('Starting rescue simulation...', 'info');
    addLog('Scenario: FIRE | Iterations: 3 | Agents: 2', 'info');
    addLog('='.repeat(70), 'info');

    // Enable step 3
    document.getElementById('step3').style.opacity = '1';
    document.getElementById('step3').style.pointerEvents = 'auto';
    document.getElementById('step2').classList.add('active');

    // Start fire visualization
    setTimeout(() => {
        startFireVisualization();
    }, 1000);

    // Connect to log stream
    const eventSource = new EventSource('/api/logs');
    let hasReceivedData = false;
    let completionDetected = false;
    let connectionTimeout;

    // Set a timeout to detect if no data is received
    connectionTimeout = setTimeout(() => {
        if (!hasReceivedData) {
            addLog('No data received after 15 seconds - checking status...', 'warning');
            checkSimulationStatus();
        }
    }, 15000);

    eventSource.onopen = function() {
        addLog('Connected to simulation stream', 'success');
    };

    eventSource.onmessage = function(event) {
        if (event.data.trim()) {
            hasReceivedData = true;
            clearTimeout(connectionTimeout);
            addLog(event.data);
        }

        // Check for completion
        if (event.data.includes('SIMULATION COMPLETE') || event.data.includes('--- SIMULATION COMPLETE ---')) {
            completionDetected = true;
            eventSource.close();
            btn.textContent = 'Completed';
            addLog('Simulation finished successfully!', 'success');

            // Enable step 4
            setTimeout(() => {
                document.getElementById('step4').style.opacity = '1';
                document.getElementById('step4').style.pointerEvents = 'auto';
                document.getElementById('step3').classList.add('active');
                startAgentVisualization();
            }, 1000);
        }
    };

    eventSource.onerror = function(error) {
        console.log('EventSource error:', error);
        clearTimeout(connectionTimeout);
        eventSource.close();
        
        if (completionDetected) {
            addLog('Stream closed after completion', 'info');
        } else if (hasReceivedData) {
            addLog('Connection interrupted - checking status...', 'warning');
            checkSimulationStatus();
        } else {
            addLog('Failed to connect to simulation stream', 'error');
            addLog('Try refreshing the page and starting again', 'warning');
            btn.disabled = false;
            btn.textContent = 'Start Simulation';
        }
    };

    // Start the simulation
    try {
        const response = await fetch('/api/start_simulation', {
            method: 'POST'
        });
        const data = await response.json();

        if (data.status !== 'success') {
            addLog('ERROR: ' + data.message, 'error');
            btn.disabled = false;
            btn.textContent = 'Start Simulation';
        }
    } catch (error) {
        addLog('ERROR: ' + error.message, 'error');
        btn.disabled = false;
        btn.textContent = 'Start Simulation';
    }
}

// Fire visualization
function startFireVisualization() {
    const canvas = document.getElementById('buildingCanvas');
    const ctx = canvas.getContext('2d');

    // Initialize fire particles
    fireParticles = [];
    for (let i = 0; i < 100; i++) {
        fireParticles.push({
            x: Math.random() * 200 + 200,
            y: canvas.height - 100 - Math.random() * 100,
            size: Math.random() * 8 + 2,
            speedY: -Math.random() * 3 - 1,
            speedX: Math.random() * 2 - 1,
            life: Math.random() * 100
        });
    }

    animationRunning = true;

    function animate() {
        if (!animationRunning) return;

        // Clear canvas
        ctx.fillStyle = 'rgba(0, 0, 0, 0.9)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw building
        ctx.strokeStyle = '#444';
        ctx.lineWidth = 2;

        // 4 floors
        for (let i = 0; i < 4; i++) {
            const y = canvas.height - (i + 1) * 100;
            ctx.strokeRect(50, y, 500, 100);

            // Floor label
            ctx.fillStyle = '#888';
            ctx.font = '14px Arial';
            ctx.fillText(`Floor ${i}`, 10, y + 50);
        }

        // Stairwell
        ctx.fillStyle = 'rgba(76, 175, 80, 0.3)';
        ctx.fillRect(280, 0, 40, canvas.height);

        // Update and draw fire particles
        fireParticles.forEach(p => {
            p.y += p.speedY;
            p.x += p.speedX;
            p.life -= 1;

            // Reset particle if dead
            if (p.life <= 0 || p.y < 0) {
                p.x = Math.random() * 200 + 200;
                p.y = canvas.height - 100 - Math.random() * 100;
                p.life = 100;
            }

            // Draw particle
            const alpha = p.life / 100;
            const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size);
            gradient.addColorStop(0, `rgba(255, 255, 100, ${alpha})`);
            gradient.addColorStop(0.5, `rgba(255, 100, 0, ${alpha * 0.8})`);
            gradient.addColorStop(1, `rgba(255, 0, 0, ${alpha * 0.3})`);

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        });

        // Child position (top floor)
        ctx.fillStyle = '#9C27B0';
        ctx.beginPath();
        ctx.arc(450, 50, 15, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 20px Arial';
        ctx.fillText('👶', 440, 58);

        buildingAnimationId = requestAnimationFrame(animate);
    }

    animate();
}

// Agent visualization
function startAgentVisualization() {
    const canvas = document.getElementById('agentCanvas');
    const ctx = canvas.getContext('2d');

    // Agent starting position
    agent = {
        x: 100,
        y: canvas.height - 50,
        targetFloor: 0,
        currentFloor: 0,
        phase: 'goingUp1',  // goingUp1, waitTop, goingDown, goingUp2, waitTop2, goingDown2
        waitTimer: 0
    };

    const path = [];  // Store agent path

    function animate() {
        // Clear canvas
        ctx.fillStyle = 'rgba(0, 0, 0, 0.95)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw building
        ctx.strokeStyle = '#444';
        ctx.lineWidth = 2;

        for (let i = 0; i < 4; i++) {
            const y = canvas.height - (i + 1) * 100;
            ctx.strokeRect(50, y, 500, 100);
        }

        // Stairwell
        ctx.fillStyle = 'rgba(76, 175, 80, 0.2)';
        ctx.fillRect(280, 0, 40, canvas.height);

        // Draw path
        ctx.strokeStyle = 'rgba(33, 150, 243, 0.5)';
        ctx.lineWidth = 3;
        ctx.beginPath();
        for (let i = 0; i < path.length; i++) {
            if (i === 0) {
                ctx.moveTo(path[i].x, path[i].y);
            } else {
                ctx.lineTo(path[i].x, path[i].y);
            }
        }
        ctx.stroke();

        // Update agent position
        const speed = 2;

        if (agent.phase === 'goingUp1') {
            // Go to middle floor (floor 1-2)
            const targetY = canvas.height - 200;
            if (agent.y > targetY) {
                agent.y -= speed;
            } else {
                agent.phase = 'waitTop';
                agent.waitTimer = 60; // Wait 1 second (60 frames)
            }
        } else if (agent.phase === 'waitTop') {
            agent.waitTimer--;
            if (agent.waitTimer <= 0) {
                agent.phase = 'goingDown';
            }
        } else if (agent.phase === 'goingDown') {
            // Go back down
            const targetY = canvas.height - 50;
            if (agent.y < targetY) {
                agent.y += speed;
            } else {
                agent.phase = 'goingUp2';
            }
        } else if (agent.phase === 'goingUp2') {
            // Go to top floor
            const targetY = 50;
            if (agent.y > targetY) {
                agent.y -= speed;
            } else {
                agent.phase = 'waitTop2';
                agent.waitTimer = 60;
            }
        } else if (agent.phase === 'waitTop2') {
            agent.waitTimer--;
            if (agent.waitTimer <= 0) {
                agent.phase = 'goingDown2';
            }
        } else if (agent.phase === 'goingDown2') {
            // Go back to bottom
            const targetY = canvas.height - 50;
            if (agent.y < targetY) {
                agent.y += speed;
            } else {
                // Restart
                agent.phase = 'goingUp1';
            }
        }

        // Add to path
        path.push({x: agent.x, y: agent.y});
        if (path.length > 300) path.shift();

        // Draw agent
        ctx.fillStyle = '#2196F3';
        ctx.beginPath();
        ctx.arc(agent.x, agent.y, 12, 0, Math.PI * 2);
        ctx.fill();

        // Agent icon
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 16px Arial';
        ctx.fillText('🤖', agent.x - 8, agent.y + 5);

        // Stats
        const stats = document.getElementById('agentStats');
        stats.innerHTML = `
            <strong>Agent Status:</strong><br>
            Phase: ${agent.phase}<br>
            Height: ${Math.round(canvas.height - agent.y)}px<br>
            Path Length: ${path.length} points
        `;

        agentAnimationId = requestAnimationFrame(animate);
    }

    animate();
}

// Toggle animation
function toggleAnimation() {
    animationRunning = !animationRunning;
    const btn = event.target;
    btn.textContent = animationRunning ? '⏸️ Pause' : '▶️ Play';
    if (animationRunning) {
        startFireVisualization();
    }
}

// Reset animation
function resetAnimation() {
    fireParticles = [];
    if (animationRunning) {
        startFireVisualization();
    }
}

// Log management
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('logContainer');
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    entry.textContent = message;
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

function clearLogs() {
    const logContainer = document.getElementById('logContainer');
    logContainer.innerHTML = '<div class="log-entry log-info">Logs cleared.</div>';
}

// Check simulation status
async function checkSimulationStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.running) {
            addLog(`Simulation is still running (${data.queue_size} messages queued)`, 'info');
            addLog('Waiting for output...', 'info');
            
            // Try to reconnect after a delay
            setTimeout(() => {
                addLog('Attempting to reconnect...', 'info');
                location.reload();
            }, 5000);
        } else {
            addLog('Simulation has stopped', 'warning');
            addLog('Check console for errors or try running again', 'info');
        }
    } catch (error) {
        addLog('Could not check simulation status: ' + error.message, 'error');
    }
}

// Initialize
window.onload = function() {
    console.log('RescuNav Web UI loaded');
};
