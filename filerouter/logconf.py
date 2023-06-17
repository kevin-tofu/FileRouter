import logging

format="%(asctime)s [%(filename)s:%(lineno)d] %(levelname)-8s %(message)s"
# logging.root.setLevel(logging.INFO)
logging.root.setLevel(logging.ERROR)
# logging.root.setLevel(logging.DEBUG)
# log.setLevel(logging.ERROR)
# logging.basicConfig(filename='error.log', level=logging.ERROR)
# logging.basicConfig(level=logging.INFO, format=format)
logging.basicConfig(level=logging.ERROR, format=format)
# logging.basicConfig(level=logging.DEBUG, format=format)

frouterlogger = logging.getLogger
