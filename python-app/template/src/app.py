from flask import Flask, jsonify
import datetime
import socket
import time
import os

app = Flask(__name__)

app_start_time = time.time()


@app.route("/api/v1/details")
def system_details():
    """
    Return system details and deployment information.
    This endpoint provides general information about the service.
    """
    return jsonify(
        {
            "time": datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"),
            "hostname": socket.gethostname(),
            "message": "You are doing well, human!!",
            "deployed_on": "kubernetes",
            "env": "${{ values.app_env }}",
            "app_name": "${{ values.app_name }}",
        }
    )


@app.route("/api/v1/healthz")
def health():
    """
    Health check endpoint for Kubernetes probes.
    
    This endpoint provides comprehensive health information including:
    - Service status
    - Uptime information
    - Current timestamp
    - Deployment details
    
    Returns:
        tuple: JSON response with health information and HTTP status code
    """
    current_time = time.time()
    uptime_seconds = int(current_time - app_start_time)
    
    # Calculate uptime in a human-readable format
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    
    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
    
    # Build health check response
    health_response = {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "uptime": uptime_str,
        "uptime_seconds": uptime_seconds,
        "service": {
            "name": "${{ values.app_name }}",
            "version": "1.0.0",  # You might want to make this configurable
            "environment": "${{ values.app_env }}"
        },
        "checks": {
            "api": "pass"
        },
        "deployment": {
            "platform": "kubernetes",
            "hostname": socket.gethostname(),
            "pod_ip": os.environ.get("POD_IP", "unknown"),
            "node_name": os.environ.get("NODE_NAME", "unknown")
        }
    }
    
    return jsonify(health_response), 200


if __name__ == "__main__":
    # Note: In production, you should use a proper WSGI server like gunicorn
    # Running on 0.0.0.0 is necessary for containerized environments
    app.run(host="0.0.0.0")