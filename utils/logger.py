import logging
import os
from datetime import datetime

if not os.path.exists("logs"):
    os.makedirs("logs")

log_filename = f"logs/scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger()
