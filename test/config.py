import os
from dataclasses import dataclass

APP_VERSION = os.getenv('APP_VERSION', 'v0'),
APP_AUTHOR = os.getenv('APP_AUTHOR', 'kevin')
APP_DATA_PATH = os.getenv('APP_DATA_PATH', './temp')

APP_PORT = int(os.getenv('APP_PORT', 80))

@dataclass
class Config:
    app_version: str
    app_author: str
    app_port: int
    app_data_path: str

config_org = Config(
    app_version=APP_VERSION,
    app_author=APP_AUTHOR,
    app_port=APP_PORT,
    app_data_path=APP_DATA_PATH
)