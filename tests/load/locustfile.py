"""
간단한 트래픽 테스트 스크립트 (Locust)

실행 방법:
    # CLI 모드
    uv run locust -f tests/load/locustfile.py --host=http://localhost:8000

    # Web UI 모드 (http://localhost:8089)
    uv run locust -f tests/load/locustfile.py --host=http://localhost:8000 --web-host=0.0.0.0
"""

from locust import HttpUser, task, between
import random


class MemoAPIUser(HttpUser):
    """메모 API 사용자 시뮬레이션"""

    wait_time = between(1, 3)  # 요청 간 1~3초 대기

    def on_start(self):
        """테스트 시작 시 실행"""
        self.created_memo_ids = []

    @task(3)
    def health_check(self):
        """Health check 엔드포인트 (비중: 30%)"""
        self.client.get("/health")

    @task(5)
    def get_memos(self):
        """메모 목록 조회 (비중: 50%)"""
        self.client.get("/memos/")

    @task(1)
    def create_memo(self):
        """메모 생성 (비중: 10%)"""
        memo_data = {
            "title": f"Load Test Memo {random.randint(1, 10000)}",
            "content": f"This is a load test memo created at {random.randint(1, 10000)}",
            "priority": random.randint(1, 4),
        }

        response = self.client.post("/memos/", json=memo_data)

        if response.status_code == 201:
            memo_id = response.json().get("id")
            if memo_id:
                self.created_memo_ids.append(memo_id)

    @task(1)
    def get_single_memo(self):
        """단일 메모 조회 (비중: 10%)"""
        if self.created_memo_ids:
            memo_id = random.choice(self.created_memo_ids)
            self.client.get(f"/memos/{memo_id}")

    def on_stop(self):
        """테스트 종료 시 생성한 메모 정리"""
        for memo_id in self.created_memo_ids:
            try:
                self.client.delete(f"/memos/{memo_id}")
            except Exception:
                pass  # 정리 중 오류는 무시
