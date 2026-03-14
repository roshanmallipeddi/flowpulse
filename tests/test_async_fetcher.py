import asyncio
from unittest.mock import patch

import aiohttp
import pytest

from src.pipeline.async_fetcher import AsyncDataFetcher


class MockResponse:
    def __init__(self, status=200, text_data="ok"):
        self.status = status
        self._text_data = text_data

    async def text(self):
        return self._text_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None


@pytest.mark.asyncio
async def test_fetch_success():
    fetcher = AsyncDataFetcher()
    urls = ["http://127.0.0.1:8000/success"]

    with patch.object(
        aiohttp.ClientSession,
        "get",
        return_value=MockResponse(status=200, text_data="success"),
    ):
        results = await fetcher.fetch_all(urls)

    assert len(results) == 1
    assert results[0]["url"] == urls[0]
    assert results[0]["status_code"] == 200
    assert results[0]["data"] == "success"
    assert results[0]["error"] is None


@pytest.mark.asyncio
async def test_retry_on_failure():
    fetcher = AsyncDataFetcher(retries=3)
    urls = ["http://127.0.0.1:8000/flaky"]

    responses = [
        MockResponse(status=500, text_data="server error"),
        MockResponse(status=500, text_data="server error"),
        MockResponse(status=200, text_data="recovered"),
    ]

    async def fake_sleep(seconds):
        return None

    with patch("asyncio.sleep", new=fake_sleep):
        with patch.object(
            aiohttp.ClientSession,
            "get",
            side_effect=responses,
        ):
            results = await fetcher.fetch_all(urls)

    assert len(results) == 1
    assert results[0]["url"] == urls[0]
    assert results[0]["status_code"] == 200
    assert results[0]["data"] == "recovered"
    assert results[0]["error"] is None


@pytest.mark.asyncio
async def test_timeout_handling():
    fetcher = AsyncDataFetcher(timeout=1)
    urls = ["http://127.0.0.1:8000/slow"]

    async def fake_sleep(seconds):
        return None

    with patch("asyncio.sleep", new=fake_sleep):
        with patch.object(
            aiohttp.ClientSession,
            "get",
            side_effect=asyncio.TimeoutError,
        ):
            results = await fetcher.fetch_all(urls)

    assert len(results) == 1
    assert results[0]["url"] == urls[0]
    assert results[0]["status_code"] is None
    assert results[0]["data"] is None
    assert results[0]["error"] == "timeout"


@pytest.mark.asyncio
async def test_rate_limiting():
    fetcher = AsyncDataFetcher(max_concurrent=2)
    urls = ["http://127.0.0.1:8000/success"] * 10

    with patch.object(
        aiohttp.ClientSession,
        "get",
        return_value=MockResponse(status=200, text_data="success"),
    ):
        results = await fetcher.fetch_all(urls)

    assert len(results) == 10
    assert all(r["status_code"] == 200 for r in results)
    assert all(r["error"] is None for r in results)
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
            side_effect=aiohttp.ClientError("forced failure"),
        ):
            async with aiohttp.ClientSession() as session:
                result = await fetcher.fetch(
                    session,
                    "http://127.0.0.1:8000/always_fail",
                )

    assert result["status_code"] is None
    assert result["data"] is None
    assert result["error"] is not None
    assert sleep_calls == [1, 2]