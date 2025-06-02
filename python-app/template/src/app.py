from flask import Flask, jsonify, request
import datetime
import socket
import time
import os
import logging
import json
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import functools

# Initialize Flask app
app = Flask(__name__)

# Configure logging based on environment
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Application metadata
app_start_time = time.time()
app_version = os.environ.get("APP_VERSION", "1.0.0")
environment = os.environ.get("ENVIRONMENT", "dev")

# Prometheus metrics
request_count = Counter(
    "app_requests_total", "Total number of requests", ["method", "endpoint", "status"]
)
request_duration = Histogram(
    "app_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
)
health_status = Gauge(
    "app_health_status", "Health status of the application (1 = healthy, 0 = unhealthy)"
)

# Environment-specific configuration
ENV_CONFIGS = {
    "dev": {
        "debug": True,
        "features": {
            "rate_limiting": False,
            "detailed_errors": True,
            "profiling": True,
        },
    },
    "qa": {
        "debug": False,
        "features": {
            "rate_limiting": True, 
            "detailed_errors": True, 
            "profiling": True
        },
    },
    "uat": {
        "debug": False,
        "features": {
            "rate_limiting": True,
            "detailed_errors": False,
            "profiling": False,
        },
    },
    "production": {
        "debug": False,
        "features": {
            "rate_limiting": True,
            "detailed_errors": False,
            "profiling": False,
        },
    },
}


def get_env_config():
    """Get configuration for current environment"""
    environment = os.environ.get("ENVIRONMENT", "dev")
    return ENV_CONFIGS.get(environment, ENV_CONFIGS["dev"])


def track_metrics(func):
    """Decorator to track request metrics"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        status = 200
        try:
            result = func(*args, **kwargs)
            if isinstance(result, tuple):
                status = result[1]
            return result
        except Exception as e:
            status = 500
            raise e
        finally:
            duration = time.time() - start_time
            endpoint = request.endpoint or "unknown"
            method = request.method
            request_count.labels(method=method, endpoint=endpoint, status=status).inc()
            request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    return wrapper


@app.route("/api/v1/details")
@track_metrics
def system_details():
    """
    Return system details and deployment information.
    This endpoint provides general information about the service.
    """
    logger.info(f"Details endpoint called from {request.remote_addr}")

    response = {
        "time": datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"),
        "hostname": socket.gethostname(),
        "message": "You are doing well, human!!",
        "deployed_on": "kubernetes",
        "env": environment,
        "app_name": "${{ values.app_name }}",
        "version": app_version,
        "features": get_env_config()["features"],
    }

    # Add debug information for non-production environments
    if environment in ["dev", "qa"]:
        response["debug"] = {
            "pod_name": os.environ.get("POD_NAME", "unknown"),
            "pod_ip": os.environ.get("POD_IP", "unknown"),
            "node_name": os.environ.get("NODE_NAME", "unknown"),
            "namespace": os.environ.get("POD_NAMESPACE", "unknown"),
        }

    return jsonify(response)


@app.route("/api/v1/healthz")
@track_metrics
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

    # Perform health checks
    health_checks = {
        "api": "pass",
        "memory": check_memory_usage(),
        "disk": check_disk_usage() if environment != "dev" else "skipped",
    }

    # Determine overall health
    is_healthy = all(
        check == "pass" or check == "skipped" for check in health_checks.values()
    )
    health_status.set(1 if is_healthy else 0)

    # Build health check response
    health_response = {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "uptime": uptime_str,
        "uptime_seconds": uptime_seconds,
        "service": {
            "name": "${{ values.app_name }}",
            "version": app_version,
            "environment": environment,
        },
        "checks": health_checks,
        "deployment": {
            "platform": "kubernetes",
            "hostname": socket.gethostname(),
            "pod_ip": os.environ.get("POD_IP", "unknown"),
            "node_name": os.environ.get("NODE_NAME", "unknown"),
        },
    }

    status_code = 200 if is_healthy else 503

    logger.debug(f"Health check: {health_response['status']}")

    return jsonify(health_response), status_code


@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


@app.route("/api/v1/ready")
@track_metrics
def readiness():
    """
    Readiness probe endpoint.
    Checks if the application is ready to serve traffic.
    """
    # Add any initialization checks here
    ready_checks = {"initialized": True, "dependencies": check_dependencies()}

    is_ready = all(ready_checks.values())

    response = {
        "ready": is_ready,
        "checks": ready_checks,
        "timestamp": datetime.datetime.now().isoformat(),
    }

    return jsonify(response), 200 if is_ready else 503


def check_memory_usage():
    """Check if memory usage is within acceptable limits"""
    try:
        import psutil

        memory_percent = psutil.virtual_memory().percent
        return "pass" if memory_percent < 90 else "warn"
    except:
        return "unknown"


def check_disk_usage():
    """Check if disk usage is within acceptable limits"""
    try:
        import psutil

        disk_percent = psutil.disk_usage("/").percent
        return "pass" if disk_percent < 85 else "warn"
    except:
        return "unknown"


def check_dependencies():
    """Check if external dependencies are available"""
    # Add checks for databases, external services, etc.
    # For now, we'll assume everything is okay
    return True


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    response = {
        "error": "Not Found",
        "message": "The requested resource was not found",
        "path": request.path,
        "timestamp": datetime.datetime.now().isoformat(),
    }

    if get_env_config()["features"]["detailed_errors"]:
        response["suggestion"] = "Check the API documentation for valid endpoints"

    return jsonify(response), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")

    response = {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "timestamp": datetime.datetime.now().isoformat(),
    }

    if get_env_config()["features"]["detailed_errors"]:
        response["details"] = str(error)

    return jsonify(response), 500


# Initialize the application
def init_app():
    """Initialize the application"""
    logger.info(
        f"Starting ${{values.app_name}} version {app_version} in {environment} environment"
    )
    logger.info(f"Configuration: {json.dumps(get_env_config(), indent=2)}")
    health_status.set(1)


# Call init_app when the module is imported
init_app()

if __name__ == "__main__":
    # Note: In production, use a proper WSGI server like gunicorn
    port = int(os.environ.get("PORT", 5000))
    debug = get_env_config()["debug"]

    if environment == "dev":
        # Enable Flask debug mode and profiling for development
        from werkzeug.middleware.profiler import ProfilerMiddleware

        if get_env_config()["features"]["profiling"]:
            app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir="./profile")

    app.run(host="0.0.0.0", port=port, debug=debug)
