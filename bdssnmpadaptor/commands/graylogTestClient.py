# -*- coding: future_fstrings -*-
from pygelf import GelfHttpHandler
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.addHandler(GelfHttpHandler(host='127.0.0.1', port=5000, compress=False))

logger.info('hello gelf')
