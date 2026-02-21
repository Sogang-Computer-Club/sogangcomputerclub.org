"""
간단한 성능 테스트 스크립트

실행 방법:
    uv run python tests/load/performance_test.py
"""

import asyncio
import time
import statistics
import httpx


BASE_URL = "http://localhost:8000"


async def measure_endpoint_performance(
    endpoint: str, method: str = "GET", json_data=None, iterations: int = 100
):
    """엔드포인트 성능 측정"""
    response_times = []

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        for _ in range(iterations):
            start_time = time.time()

            if method == "GET":
                response = await client.get(endpoint)
            elif method == "POST":
                response = await client.post(endpoint, json=json_data)

            end_time = time.time()

            if response.status_code in [200, 201]:
                response_times.append((end_time - start_time) * 1000)  # ms 단위

    if response_times:
        return {
            "endpoint": endpoint,
            "method": method,
            "iterations": iterations,
            "avg_ms": round(statistics.mean(response_times), 2),
            "min_ms": round(min(response_times), 2),
            "max_ms": round(max(response_times), 2),
            "median_ms": round(statistics.median(response_times), 2),
            "stdev_ms": round(statistics.stdev(response_times), 2)
            if len(response_times) > 1
            else 0,
        }

    return None


async def measure_concurrent_requests(endpoint: str, concurrent_users: int = 10):
    """동시 요청 처리 성능 측정"""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        start_time = time.time()

        tasks = [client.get(endpoint) for _ in range(concurrent_users)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()

        successful = sum(
            1
            for r in responses
            if isinstance(r, httpx.Response) and r.status_code == 200
        )

        return {
            "endpoint": endpoint,
            "concurrent_users": concurrent_users,
            "total_time_ms": round((end_time - start_time) * 1000, 2),
            "successful_requests": successful,
            "failed_requests": concurrent_users - successful,
            "requests_per_second": round(concurrent_users / (end_time - start_time), 2),
        }


async def main():
    """성능 테스트 실행"""
    print("=" * 60)
    print("성능 테스트 시작")
    print("=" * 60)
    print()

    # 1. 개별 엔드포인트 성능 테스트
    print("1. 엔드포인트 응답 시간 측정 (100회 반복)")
    print("-" * 60)

    endpoints = [
        ("/health", "GET", None),
        ("/memos/", "GET", None),
        (
            "/memos/",
            "POST",
            {"title": "Performance Test", "content": "Testing performance"},
        ),
    ]

    for endpoint, method, json_data in endpoints:
        result = await measure_endpoint_performance(endpoint, method, json_data)
        if result:
            print(f"\n{method} {endpoint}")
            print(f"  평균: {result['avg_ms']} ms")
            print(f"  중앙값: {result['median_ms']} ms")
            print(f"  최소: {result['min_ms']} ms")
            print(f"  최대: {result['max_ms']} ms")
            print(f"  표준편차: {result['stdev_ms']} ms")

    print()
    print("=" * 60)

    # 2. 동시 요청 처리 테스트
    print("\n2. 동시 요청 처리 성능")
    print("-" * 60)

    concurrent_tests = [10, 50, 100]

    for num_users in concurrent_tests:
        result = await measure_concurrent_requests("/health", num_users)
        print(f"\n동시 사용자: {num_users}명")
        print(f"  총 소요 시간: {result['total_time_ms']} ms")
        print(f"  성공한 요청: {result['successful_requests']}")
        print(f"  실패한 요청: {result['failed_requests']}")
        print(f"  초당 요청 수: {result['requests_per_second']} req/s")

    print()
    print("=" * 60)
    print("성능 테스트 완료")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
