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
        self.logger = setup_logging()
        self.logger.info("Initailizing the PolariseMiner............")
        self.container_manager =ContainerManager()
        self.allocator = ResourceAllocator()
        self.compute_port = 8080
        self.port=port
        self.server = ComputeServer(port=self.compute_port, allocator=self.allocator)

    def start(self) -> None:
        """
        Start the PolariseMiner server.
        """
        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                self.logger.info(f"Starting PolariseMiner on port {self.port} (Attempt {attempt+1})...")
                self.server.start()
                self.logger.info("PolariseMiner is running.")
                break
            except Exception as e:
                self.logger.error(f"Failed to start PolariseMiner: {e}")
                if attempt == retry_attempts - 1:
                    raise
                self.logger.info("Retrying...")

    
    def stop(self) -> None:
        """
        Stop the PolariseMiner server.
        """
        self.logger.info("Stopping PolariseMiner...")
        self.server.stop()
        self.logger.info("PolariseMiner stopped.")
        # self.container_manager.cleanup()
        self.logger.info("PolariseMiner stopped.")




