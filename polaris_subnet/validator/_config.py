from polaris_subnet.base.config import PolarisBaseSettings
from typing import List

class ValidatorSettings(PolarisBaseSettings):
    call_timeout: int = 60
    host: str = "0.0.0.0"
    port: int = 8000
    iteration_interval: int = 800
    max_allowed_weights: int=420
    subnet_name: str ="mosaic"
    logging_level: str ="INFO"
