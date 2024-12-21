from polaris_subnet.base.config import PolarisBaseSettings # type: ignore
from typing import List

class MinerSettings(PolarisBaseSettings):
    host: str
    port: int
