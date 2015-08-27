import logging
logger = logging.getLogger('uvcsite.nva.oauth2_client')

def log(message, summary='', severity=logging.DEBUG):
    logger.log(severity, '%s %s', summary, message)
