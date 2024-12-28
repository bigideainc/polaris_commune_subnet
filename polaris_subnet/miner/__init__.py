import sys
import threading
import signal
import asyncio
import uvicorn
from loguru import logger
from multiprocessing import Event
from communex.module.module import Module
from communex.client import CommuneClient
from communex.module.client import ModuleClient
from communex.compat.key import classic_load_key
from communex.types import Ss58Address
from substrateinterface import Keypair
from communex.key import generate_keypair
from uvicorn import Server, Config
from communex._common import get_node_url
from polaris_subnet.miner._config import MinerSettings
from polaris_subnet.base.utils import get_netuid 
from polaris_subnet.miner.Polarisnode import PolarisMiner 
from polaris_subnet.miner.utils import fetch_container_data

class Miner(PolarisMiner):
    def __init__(self, key: Keypair, settings: MinerSettings = None) -> None:
        self.settings = settings or MinerSettings()
        super().__init__(port=settings.port)
        self.key = key
        self.c_client = CommuneClient(get_node_url(use_testnet=self.settings.use_testnet))
        self.netuid = get_netuid(self.c_client)
        # Print out key and UID information
        self.print_key_info()
        self.miner_uid= self.print_miner_uid()
    def print_key_info(self):
        """
        Prints out the key information (SS58 address, public key, etc.)
        on the network for the miner.
        """
        logger.info(f"Miner Key Information:")
        logger.info(f"SS58 Address: {self.key.ss58_address}")
        logger.info(f"Public Key (Hex): {self.key.public_key.hex()}")
        logger.info(f"Key Type: {self.key.crypto_type}")
        logger.info(f"Network UID: {self.netuid}")

    def print_miner_uid(self):
        """
        Prints out the miner's UID on the network based on its SS58 address.
        """
        try:
            # Get the map of keys (UID -> SS58 Address) for the network
            modules_keys = self.c_client.query_map_key(self.netuid)
            val_ss58 = self.key.ss58_address

            # Find the miner's UID by matching the SS58 address
            miner_uid = next(uid for uid, address in modules_keys.items() if address == val_ss58)

            logger.info(f"Miner UID on the network: {miner_uid}")
            return miner_uid

        except StopIteration:
            logger.error(f"Miner SS58 address {self.key.ss58_address} not found in the network.")
        except Exception as e:
            logger.error(f"Error retrieving miner UID: {e}")
    
    async def fetch_container_data_periodically(self, interval: int):
        """
        Periodically fetch and log container data every `interval` seconds.
        """
        while True:
            try:
                # Call the fetch_container_data function (imported or implemented)
                data = await fetch_container_data()
            except Exception as e:
                logger.error(f"Error in fetching container data: {e}")
            await asyncio.sleep(interval)
    
    async def serve_async(self):
        """
        Start the PolariseMiner and periodically fetch container data asynchronously.
        """
        from communex.module.server import ModuleServer

        logger.info("Starting PolariseMiner server...")
        self.start()
        logger.info("Registering PolariseMiner with Commune Subnet...")
        server = ModuleServer(self, self.key, subnets_whitelist=[self.netuid])
        app = server.get_fastapi_app()

        # Configure the Uvicorn server
        uvicorn_config = Config(app, host=self.settings.host, port=self.settings.port, log_level="info")
        uvicorn_server = Server(uvicorn_config)

        # Schedule periodic fetch task
        periodic_task = asyncio.create_task(self.fetch_container_data_periodically(interval=30))

        # Run both Uvicorn server and periodic task concurrently
        await asyncio.gather(
            uvicorn_server.serve(),
            periodic_task
        )
    # def serve(self):
    #     # """
    #     # Start the PolariseMiner and serve it on the specified port.
    #     # """
    #     # from communex.module.server import ModuleServer
    #     # try:
    #     #     logger.info("Starting PolariseMiner server...")
    #     #     self.start()
    #     #     logger.info("Registering PolariseMiner with Commune Subnet...")
    #     #     server = ModuleServer(self, self.key, subnets_whitelist=[self.netuid])
    #     #     app = server.get_fastapi_app()
    #     #     logger.info(f"Serving FastAPI on {self.settings.host}:{self.settings.port}...")
    #     #     uvicorn.run(app, host=self.settings.host, port=self.settings.port)
    #     # except Exception as e:
    #     #     logger.error(f"Error serving miner: {e}")
    #     # finally:
    #     #     self.stop()  # Cleanup resources when server stops
    #     asyncio.run(self.serve_async())
    def serve(self):
        """
        Wrapper to start the asynchronous server using an existing event loop.
        """
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If the loop is already running, schedule the async server
            loop.create_task(self.serve_async())
        else:
            # If no loop is running, start a new loop
            asyncio.run(self.serve_async())

if __name__ == "__main__":
    settings = MinerSettings(
        host="0.0.0.0",
        port=8080,
        use_testnet=True,
    )
    miner = Miner(key=classic_load_key("polaris-miner0"), settings=settings)
    miner.serve()
