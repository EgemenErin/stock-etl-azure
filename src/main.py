import logging
from extract import run_extraction
from transform import run_transformation
from load import run_load

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("ETL Pipeline Start")

    logger.info("Phase 1: Extract")
    run_extraction()

    logger.info("Phase 2: Transform")
    df = run_transformation()

    if df is None:
        logger.error("Transformation returned no data. Aborting load.")
        raise SystemExit(1)

    logger.info("Phase 3: Load")
    run_load(df)

    logger.info("ETL Pipeline Complete")