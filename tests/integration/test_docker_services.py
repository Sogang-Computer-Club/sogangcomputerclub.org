import pytest
import subprocess
import time
import requests
import redis
from aiokafka.admin import AIOKafkaAdminClient
import asyncio


def run_docker_command(command: str) -> tuple[int, str, str]:
    """Run a docker-compose command and return exit code, stdout, stderr"""
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


@pytest.fixture(scope="module")
def docker_services():
    """Ensure docker services are running"""
    # Check if services are already running
    returncode, stdout, stderr = run_docker_command("docker-compose ps --services --filter status=running")

    running_services = stdout.strip().split('\n') if stdout.strip() else []
    required_services = {'backend', 'postgres', 'redis', 'kafka', 'zookeeper'}

    if not required_services.issubset(set(running_services)):
        pytest.skip("Docker services are not running. Start them with 'docker-compose up -d'")

    # Wait for services to be healthy
    time.sleep(5)

    yield

    # Cleanup is handled manually, not tearing down services


class TestDockerServices:
    """Test Docker Compose services status"""

    def test_docker_compose_services_running(self, docker_services):
        """Test that all required services are running"""
        returncode, stdout, stderr = run_docker_command("docker-compose ps --services --filter status=running")

        assert returncode == 0, f"Failed to get docker services: {stderr}"

        running_services = stdout.strip().split('\n')
        required_services = ['backend', 'postgres', 'redis', 'kafka', 'zookeeper']

        for service in required_services:
            assert service in running_services, f"Service {service} is not running"

    def test_backend_container_healthy(self, docker_services):
        """Test that Backend container is healthy"""
        returncode, stdout, stderr = run_docker_command("docker-compose ps backend")

        assert returncode == 0
        assert "Up" in stdout or "running" in stdout.lower()

    def test_postgres_container_healthy(self, docker_services):
        """Test that PostgreSQL container is healthy"""
        returncode, stdout, stderr = run_docker_command("docker-compose ps postgres")

        assert returncode == 0
        assert "Up" in stdout or "running" in stdout.lower()

    def test_redis_container_healthy(self, docker_services):
        """Test that Redis container is healthy"""
        returncode, stdout, stderr = run_docker_command("docker-compose ps redis")

        assert returncode == 0
        assert "Up" in stdout or "running" in stdout.lower()

    def test_kafka_container_healthy(self, docker_services):
        """Test that Kafka container is healthy"""
        returncode, stdout, stderr = run_docker_command("docker-compose ps kafka")

        assert returncode == 0
        assert "Up" in stdout or "running" in stdout.lower()

    def test_zookeeper_container_healthy(self, docker_services):
        """Test that Zookeeper container is healthy"""
        returncode, stdout, stderr = run_docker_command("docker-compose ps zookeeper")

        assert returncode == 0
        assert "Up" in stdout or "running" in stdout.lower()
