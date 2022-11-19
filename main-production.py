import waitress
import logging
from app import app

if __name__ == "__main__":
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    waitress.serve(app, host="0.0.0.0", port=80)
