import asyncio
import logging
from src.pipeline.async_fetcher import AsyncDataFetcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

async def main():
    urls = [
        "http://127.0.0.1:8000/success",
        "http://127.0.0.1:8000/flaky",
        "http://127.0.0.1:8000/slow"
    ]

    fetcher = AsyncDataFetcher()
    results = await fetcher.fetch_all(urls)

    for result in results:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())