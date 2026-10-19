
import logging
import os

from app import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

try:
    logger.info("Starting Flask application")

    app = create_app()

    app.secret_key = os.environ.get("FLASK_SECRET_KEY")

    if not app.secret_key:
        raise RuntimeError(
            "FLASK_SECRET_KEY is missing. Set it in your .env file."
        )

    logger.info("Flask application created successfully")

    if __name__ == "__main__":
        logger.info("Running Flask server")

        app.run(
            host="0.0.0.0",
            port=5000,
            debug=True,
            use_reloader=False
        )

except Exception:
    logger.exception("Failed to start application")
    raise
