import logging

# Here we are setting up a logging configuration which stores logs information in app.log file we created and it stores current date and time, level name, messsage.
def setup_logger():
    logging.basicConfig(
        filename="app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger()