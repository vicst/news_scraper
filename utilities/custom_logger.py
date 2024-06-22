import inspect
import logging
from datetime import date, datetime
import os
import sys


def customLogger(logLevel=logging.DEBUG, logs_dir_name="Logs"):
    """
    Creates the logger object
    Parameters
    ----------
    logLevel
    logs_dir

    Returns
    -------

    """
    root_path = os.path.split(os.path.dirname(__file__))[0]
    logs_dir = os.path.join(root_path, "output")
    #print("Logs will be saved to: " + logs_dir)
    # Create log dir if doesn't exists
    if not os.path.exists(logs_dir):
        os.mkdir(logs_dir)

    log_file = os.path.join(logs_dir, "automation_" + str(date.today()) + ".log")

    # Gets the name of the class / method from where this method is called
    loggerName = inspect.stack()[1][3]
    logger = logging.getLogger(loggerName)
    # By default, log all messages
    logger.setLevel(logging.DEBUG)

    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setLevel(logLevel)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger




