import argparse
import asyncio
import json
import os
import signal
import ssl
import sys
import time
import aiohttp
from communex.module.module import Module, endpoint
from communex.client import CommuneClient
from communex._common import get_node_url
from polaris_subnet.miner.allocate import ResourceAllocator
from polaris_subnet.miner.container import ContainerManager
from polaris_subnet.miner.http_server import ComputeServer
from polaris_subnet.utils.logging import setup_logging

class PolarisMiner(Module):
    def __init__(self,port: int = 8000):
        super().__init__()
        self.logger = setup_logging(log_file='polarise.log', level='INFO')
        self.logger.info("Logging setup complete.")
        self.logger.info("Initailizing the PolariseMiner............")
        self.container_manager =ContainerManager()
        self.allocator = ResourceAllocator()
        self.compute_port = 8082
        self.port=port
        self.server = ComputeServer(port=self.compute_port, allocator=self.allocator)
        self.is_running = False

    def start(self):
        self.logger.info(f"Starting PolarisMiner on port {self.port}...")
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        self.server.start()
        self.is_running = True
        self.logger.info("PolarisMiner is running.")

    def stop(self):
        self.logger.info("Stopping PolarisMiner...")
        self.server.stop()
        self.is_running = False
        self.logger.info("PolarisMiner stopped.")

    def handle_shutdown(self, signum, frame):
        self.logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.stop()
        sys.exit(0)



