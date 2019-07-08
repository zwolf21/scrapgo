import logging

logger = logging.getLogger('codingforentrepreneurs')

stream_hander = logging.StreamHandler()
logger.addHandler(stream_hander)
file_handler = logging.FileHandler('codingforentrepreneurs.log')
logger.addHandler(file_handler)