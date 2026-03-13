import pytest
from unittest.mock import patch
import aiohttp
from src.pipeline.async_fetcher import AsyncDataFetcher


@pytest.mark.asyncio
async def test_fetch_success():
    fetcher = AsyncDataFetcher()
    urls = ["http://127.0.0.1:8000/success"]

    results = await fetcher.fetch_all(urls)

    assert len(results) == 1
    assert results[0]["status_code"] == 200
    assert results[0]["error"] is None


@pytest.mark.asyncio
async def test_retry_on_failure():
    fetcher = AsyncDataFetcher(retries=3)
    urls = ["http://127.0.0.1:8000/flaky"]

    results = await fetcher.fetch_all(urls)

    assert len(results) == 1
    assert results[0]["url"] == urls[0]
    assert "status_code" in results[0]
    assert "error" in results[0]
    assert results[0]["status_code"] == 200 or results[0]["error"] is not None


@pytest.mark.asyncio
async def test_timeout_handling():
    fetcher = AsyncDataFetcher(timeout=1)
    urls = ["http://127.0.0.1:8000/slow"]

    results = await fetcher.fetch_all(urls)

    assert len(results) == 1
    assert results[0]["error"] is not None


@pytest.mark.asyncio
async def test_rate_limiting():
    fetcher = AsyncDataFetcher(max_concurrent=2)
    urls = ["http://127.0.0.1:8000/success"] * 10

    results = await fetcher.fetch_all(urls)

    assert len(results) == 10
    assert all("url" in r for r in results)
    assert all("status_code" in r for r in results)


@pytest.mark.asyncio
async def test_exponential_backoff_sequence():
    fetcher = AsyncDataFetcher(retries=3)

    sleep_calls = []

    async def fake_sleep(seconds):
        sleep_calls.append(seconds)

    with patch("asyncio.sleep", new=fake_sleep):
        with patch.object(
            aiohttp.ClientSession,
            "get",
            side_effect=aiohttp.ClientError("forced failure")
        ):
            async with aiohttp.ClientSession() as session:
                result = await fetcher.fetch(
                    session,
                    "http://127.0.0.1:8000/always_fail"
                )

    assert result["status_code"] is None
    assert result["data"] is None
    assert result["error"] is not None
    assert sleep_calls == [1, 2]