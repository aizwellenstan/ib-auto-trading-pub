from loguru import logger
import datetime

def log(message):
    asctime = str(datetime.datetime.now())

    LOG_FORMAT = asctime + " " + str(message)
    logger.add("Main.log", 
                format=LOG_FORMAT, 
                level="INFO", 
                rotation="5 MB")
    logger.info(message)