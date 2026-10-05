from dataclasses import dataclass

from client import KimaiAPIClient


@dataclass
class AppContext:
    api: KimaiAPIClient
