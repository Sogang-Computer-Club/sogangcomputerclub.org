import pytest
import requests
import time


BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def wait_for_api():
    """Wait for API to be ready"""
    max_retries = 30
    retry_interval = 2

    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                return
        except requests.exceptions.RequestException:
            pass

        if i < max_retries - 1:
            time.sleep(retry_interval)

    pytest.skip("API is not accessible. Make sure services are running with 'docker-compose up -d'")


class TestAPIEndToEnd:
    """End-to-end API tests against running server"""

    def test_health_check(self, wait_for_api):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")

        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "services" in data
        assert data["services"]["database"] == "healthy"

    def test_create_memo_e2e(self, wait_for_api):
        """Test creating a memo through the API"""
        memo_data = {
            "title": "E2E Test Memo",
            "content": "This is an end-to-end test memo",
            "tags": ["e2e", "integration"],
            "priority": 3,
            "category": "testing"
        }

        response = requests.post(f"{BASE_URL}/memos/", json=memo_data)

        assert response.status_code == 201

        data = response.json()
        assert data["title"] == memo_data["title"]
        assert data["content"] == memo_data["content"]
        assert "id" in data



    def test_get_memos_e2e(self, wait_for_api):
        """Test retrieving all memos"""
        response = requests.get(f"{BASE_URL}/memos/")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_full_memo_lifecycle(self, wait_for_api):
        """Test complete CRUD lifecycle of a memo"""

        # 1. Create a memo
        create_data = {
            "title": "Lifecycle Test Memo",
            "content": "Testing full CRUD lifecycle",
            "priority": 2
        }

        create_response = requests.post(f"{BASE_URL}/memos/", json=create_data)
        assert create_response.status_code == 201

        memo = create_response.json()
        memo_id = memo["id"]

        # 2. Read the created memo
        get_response = requests.get(f"{BASE_URL}/memos/{memo_id}")
        assert get_response.status_code == 200

        retrieved_memo = get_response.json()
        assert retrieved_memo["id"] == memo_id
        assert retrieved_memo["title"] == create_data["title"]

        # 3. Update the memo
        update_data = {
            "title": "Updated Lifecycle Test",
            "priority": 4,
            "is_favorite": True
        }

        update_response = requests.put(f"{BASE_URL}/memos/{memo_id}", json=update_data)
        assert update_response.status_code == 200

        updated_memo = update_response.json()
        assert updated_memo["title"] == update_data["title"]
        assert updated_memo["priority"] == update_data["priority"]
        assert updated_memo["is_favorite"] == update_data["is_favorite"]

        # 4. Delete the memo
        delete_response = requests.delete(f"{BASE_URL}/memos/{memo_id}")
        assert delete_response.status_code == 204

        # 5. Verify deletion
        verify_response = requests.get(f"{BASE_URL}/memos/{memo_id}")
        assert verify_response.status_code == 404

    def test_search_memos_e2e(self, wait_for_api):
        """Test searching memos"""

        # Create test memos
        test_memos = [
            {"title": "Search Test Python", "content": "Python programming"},
            {"title": "Search Test Docker", "content": "Docker containers"},
        ]

        created_ids = []
        for memo_data in test_memos:
            response = requests.post(f"{BASE_URL}/memos/", json=memo_data)
            if response.status_code == 201:
                created_ids.append(response.json()["id"])

        # Search for "Python"
        search_response = requests.get(f"{BASE_URL}/memos/search/?q=Python")
        assert search_response.status_code == 200

        results = search_response.json()
        assert len(results) >= 1

        # Verify search result contains "Python"
        found = any("Python" in memo["title"] or "Python" in memo["content"] for memo in results)
        assert found

        # Clean up - delete created memos
        for memo_id in created_ids:
            requests.delete(f"{BASE_URL}/memos/{memo_id}")

    def test_memo_validation_e2e(self, wait_for_api):
        """Test API validation errors"""

        # Missing required field
        invalid_data = {
            "title": "No content"
        }

        response = requests.post(f"{BASE_URL}/memos/", json=invalid_data)
        assert response.status_code == 422

        # Invalid priority
        invalid_priority = {
            "title": "Invalid Priority",
            "content": "Testing",
            "priority": 10  # Should be 1-4
        }

        response = requests.post(f"{BASE_URL}/memos/", json=invalid_priority)
        assert response.status_code == 422

    def test_memo_not_found_e2e(self, wait_for_api):
        """Test 404 responses for non-existent memos"""

        # Get non-existent memo
        response = requests.get(f"{BASE_URL}/memos/999999")
        assert response.status_code == 404

        # Update non-existent memo
        response = requests.put(f"{BASE_URL}/memos/999999", json={"title": "Updated"})
        assert response.status_code == 404

        # Delete non-existent memo
        response = requests.delete(f"{BASE_URL}/memos/999999")
        assert response.status_code == 404

    def test_pagination_e2e(self, wait_for_api):
        """Test pagination parameters"""

        # Create multiple memos
        created_ids = []
        for i in range(5):
            memo_data = {
                "title": f"Pagination Test {i}",
                "content": f"Content {i}"
            }
            response = requests.post(f"{BASE_URL}/memos/", json=memo_data)
            if response.status_code == 201:
                created_ids.append(response.json()["id"])

        # Test limit parameter
        response = requests.get(f"{BASE_URL}/memos/?limit=3")
        assert response.status_code == 200

        data = response.json()
        assert len(data) <= 3

        # Test skip parameter
        response = requests.get(f"{BASE_URL}/memos/?skip=2&limit=2")
        assert response.status_code == 200

        # Clean up
        for memo_id in created_ids:
            requests.delete(f"{BASE_URL}/memos/{memo_id}")

    def test_concurrent_requests(self, wait_for_api):
        """Test handling concurrent requests"""
        import concurrent.futures

        def create_memo(index):
            memo_data = {
                "title": f"Concurrent Test {index}",
                "content": f"Testing concurrency {index}"
            }
            response = requests.post(f"{BASE_URL}/memos/", json=memo_data)
            return response.status_code, response.json() if response.status_code == 201 else None

        # Create 10 memos concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_memo, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # Verify all requests succeeded
        successful = [r for r in results if r[0] == 201]
        assert len(successful) == 10

        # Clean up
        for status_code, data in results:
            if status_code == 201 and data:
                requests.delete(f"{BASE_URL}/memos/{data['id']}")
