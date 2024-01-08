

__all__ = [
           #PromeTHeus_MSG_LEVEL
           "MSG_VERBOSE",
           "MSG_DEBUG",
           "MSG_INFO",
           "MSG_WARNING",
           "MSG_ERROR",
           "MSG_FATAL",
           "MSG_STR_INFO",
           "MSG_STR_WARNING",
           "MSG_STR_ERROR"
           ]

def MSG_VERBOSE( self, msg, *args):
  self._logger.verbose(msg,*args)

def MSG_DEBUG( self, msg, *args):
  self._logger.debug(msg,*args)

def MSG_INFO( self, msg, *args):
  self._logger.info(msg,*args)

def MSG_WARNING( self, msg, *args):
  self._logger.warning(msg,*args)

def MSG_ERROR( self, msg, *args):
  self._logger.error(msg,*args)

def MSG_FATAL( self, msg, *args):
  self._logger.fatal(msg,*args)

def MSG_STR_INFO (logger, msg, *args):
  logger._logger.info(msg, *args)

def MSG_STR_WARNING (logger, msg, *args):
  logger._logger.warning(msg, *args)

def MSG_STR_ERROR (logger, msg, *args):
  logger._logger.error(msg, *args)
