import asyncio
import aiohttp
import logging
from datetime import datetime, timezone

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ContainerLogger")

async def fetch_container_data():
    url = "https://orchestrator-gekh.onrender.com/api/v1/containers/miner/UhsJfZCngizQoslnKWoL"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                print(data)
                process_container_data(data)
            else:
                logger.error(f"Failed to fetch data. HTTP status code: {response.status}")

def process_container_data(data):
    current_date = datetime.now(timezone.utc).date()
    print(current_date)
    total_containers = 0
    active_containers = 0
    terminated_containers = 0

    for container in data:
        created_at = datetime.fromisoformat(container["created_at"][:-1]).date()
        if created_at == current_date:
            total_containers += 1
            if container["status"] == "active":
                active_containers += 1
            elif container["status"] == "terminated":
                terminated_containers += 1

    logger.info(f"Total containers today: {total_containers}")
    logger.info(f"Active containers today: {active_containers}")
    logger.info(f"Terminated containers today: {terminated_containers}")
