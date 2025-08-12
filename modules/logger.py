from loguru import logger
import datetime

def log(message):
    asctime = str(datetime.datetime.now())

    LOG_FORMAT = asctime + " " + str(message)
    logger.info(message)