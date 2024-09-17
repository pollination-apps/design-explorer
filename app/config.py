import os
from pathlib import Path

assets_path = Path(__file__).parent.joinpath('assets')
pollination_path = Path(__file__).parent.joinpath('pollination')
base_path = os.getenv('POLLINATION_API_URL', 'https://api.staging.pollination.cloud')
