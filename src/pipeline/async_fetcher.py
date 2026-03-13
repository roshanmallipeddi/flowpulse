import asyncio
import aiohttp
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class AsyncDataFetcher:
    def __init__(self, timeout: int = 30, max_concurrent: int = 10, retries: int = 3):
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.retries = retries
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        error = None

        async with self.semaphore:
            for attempt in range(1, self.retries + 1):
                try:
                    logger.info(f"Sending request to {url} (attempt {attempt})")

                    async with session.get(url, timeout=self.timeout) as response:
                        data = await response.text()

                        logger.info(
                            f"Received response from {url} with status {response.status} "
                            f"on attempt {attempt}"
                        )

                        if 500 <= response.status < 600:
                            error = f"server error {response.status}"
                            logger.warning(
                                f"{url} returned retryable server error {response.status} "
                                f"on attempt {attempt}"
                            )

                            if attempt < self.retries:
                                backoff = 2 ** (attempt - 1)
                                logger.info(f"Retrying {url} in {backoff}s")
                                await asyncio.sleep(backoff)
                                continue

                            logger.error(
                                f"Exhausted retries for {url}. Final status: {response.status}"
                            )
                            return {
                                "url": url,
                                "status_code": response.status,
                                "data": data,
                                "error": error,
                            }

                        logger.info(f"Request to {url} succeeded on attempt {attempt}")
                        return {
                            "url": url,
                            "status_code": response.status,
                            "data": data,
                            "error": None,
                        }

                except asyncio.TimeoutError:
                    error = "timeout"
                    logger.warning(f"Timeout while fetching {url} on attempt {attempt}")

                except Exception as e:
                    error = str(e)
                    logger.warning(f"Error fetching {url} on attempt {attempt}: {e}")

                if attempt < self.retries:
                    backoff = 2 ** (attempt - 1)
                    logger.info(f"Retrying {url} in {backoff}s")
                    await asyncio.sleep(backoff)

            logger.error(f"Exhausted retries for {url}. Final error: {error}")
            return {
                "url": url,
                "status_code": None,
                "data": None,
                "error": error,
            }

    async def fetch_all(self, urls: List[str]) -> List[Dict[str, Any]]:
        logger.info(f"Starting concurrent fetch for {len(urls)} URLs")

        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.create_task(self.fetch(session, url)) for url in urls]
            results = await asyncio.gather(*tasks)

        logger.info("Completed concurrent fetch for all URLs")
        return results