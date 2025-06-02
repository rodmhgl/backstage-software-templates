import pytest
import json
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get("/api/v1/healthz")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "uptime" in data
    assert data["service"]["name"] == "${{ values.app_name }}"


def test_details_endpoint(client):
    """Test the details endpoint"""
    response = client.get("/api/v1/details")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert "time" in data
    assert "hostname" in data
    assert data["message"] == "You are doing well, human!!"
    assert data["app_name"] == "${{ values.app_name }}"
    assert "features" in data


def test_ready_endpoint(client):
    """Test the readiness endpoint"""
    response = client.get("/api/v1/ready")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["ready"] == True
    assert "checks" in data


def test_metrics_endpoint(client):
    """Test the Prometheus metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"app_requests_total" in response.data
    assert b"app_health_status" in response.data

def test_environment_config():
    """Test environment configuration loading"""
    from app import get_env_config, ENV_CONFIGS

    # Store original environment variable if it exists
    original_env = os.environ.get("ENVIRONMENT", None)
    
    try:
        # Test production config
        os.environ["ENVIRONMENT"] = "production"
        config = get_env_config()
        assert config["debug"] == False
        assert config["features"]["detailed_errors"] == False

        # Test default dev config
        os.environ["ENVIRONMENT"] = "dev"
        config = get_env_config()
        assert config["debug"] == True
        assert config["features"]["detailed_errors"] == True
    
    finally:
        # Restore original environment or remove if it wasn't set
        if original_env is not None:
            os.environ["ENVIRONMENT"] = original_env
        else:
            if "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
