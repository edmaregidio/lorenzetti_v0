__all__ = ['StringLogger']

from Gaugi.messenger import LoggingLevel
from Gaugi.gtypes  import EnumStringification
from Gaugi import retrieve_kw
import logging
from io import StringIO 

#
#   Copy/paste stuff from Gaugi default Logger
#
logging.addLevelName(LoggingLevel.VERBOSE, "VERBOSE")
logging.addLevelName(LoggingLevel.FATAL,    "FATAL" )

def verbose(self, message, *args, **kws):
  """
    Attempt to emit verbose message
  """
  if self.isEnabledFor(LoggingLevel.VERBOSE):
    self._log(LoggingLevel.VERBOSE, message, args, **kws)

class FatalError(RuntimeError):
  pass

def _getAnyException(args):
  exceptionType = [issubclass(arg,BaseException) if type(arg) is type else False for arg in args]
  Exc = None
  if any(exceptionType):
    # Check if any args message is the exception type that should be raised
    args = list(args)
    Exc = args.pop( exceptionType.index( True ) )
    args = tuple(args)
  return Exc, args

def warning(self, message, *args, **kws):
  Exc, args = _getAnyException(args)
  if self.isEnabledFor(LoggingLevel.WARNING):
    self._log(LoggingLevel.WARNING, message, args, **kws)
  if Exc is not None:
    if args:
      raise Exc(message % (args if len(args) > 1 else args[0]))
    else:
      raise Exc(message)

def error(self, message, *args, **kws):
  Exc, args = _getAnyException(args)
  if self.isEnabledFor(LoggingLevel.ERROR):
    self._log(LoggingLevel.ERROR, message, args, **kws)
  if Exc is not None:
    if args:
      raise Exc(message % (args if len(args) > 1 else args[0]))
    else:
      raise Exc(message)

def fatal(self, message, *args, **kws):
  """
    Attempt to emit fatal message
  """
  Exc, args = _getAnyException(args)
  if Exc is None: Exc = FatalError
  if self.isEnabledFor(LoggingLevel.FATAL):
    self._log(LoggingLevel.FATAL, message, args, **kws)
  if args:
    raise Exc(message % (args if len(args) > 1 else args[0]))
  else:
    raise Exc(message)

logging.Logger.verbose = verbose
logging.Logger.warning = warning
logging.Logger.error = error
logging.Logger.fatal = fatal
logging.Logger.critical = fatal

# This won't handle print and sys.stdout, but most of the cases are handled.
_nl = True

def nlStatus():
  global _nl
  return _nl

def resetNlStatus():
  global _nl
  _nl = True

class StreamHandler2( logging.StreamHandler ):
  """
  Just in case we need a bounded method for emiting without newlines.
  """

  def __init__(self, handler):
    """
    Copy ctor
    """
    logging.StreamHandler.__init__(self)
    self._name = handler._name
    self.level = handler.level
    self.formatter = handler.formatter
    self.stream = handler.stream
    # We use stream as carrier b/c other handlers may complicate things

  def emit_no_nl(self, record):
    """
    Monkey patching to emit a record without newline.
    """
    #print '\n record', record
    #print '\n record.__dict__', record.__dict__
    try:
      nl = record.nl
    except AttributeError:
      nl = True
    try:
      msg = self.format(record)
      stream = self.stream
      global _nl
      fs = ''
      if nl and not _nl:
        fs += '\n'
      _nl = nl
      fs += '%s'
      if nl: fs += '\n'

      if not hasattr(logging, '_unicode'):
        stream.write(fs % msg)
      elif not logging._unicode: #if no unicode support...
        stream.write(fs % msg)
      else:
        try:
          if (isinstance(msg, unicode) and
            getattr(stream, 'encoding', None)):
            ufs = unicode(fs)
            try:
              stream.write(ufs % msg)
            except UnicodeEncodeError:
              #Printing to terminals sometimes fails. For example,
              #with an encoding of 'cp1251', the above write will
              #work if written to a stream opened or wrapped by
              #the codecs module, but fail when writing to a
              #terminal even when the codepage is set to cp1251.
              #An extra encoding step seems to be needed.
              stream.write((ufs % msg).encode(stream.encoding))
          else:
            stream.write(fs % msg)
        except UnicodeError:
          stream.write(fs % msg.encode("UTF-8"))
      self.flush()
    except (KeyboardInterrupt, SystemExit):
      raise
    except:
      self.handleError(record)


def _getFormatter():
  class Formatter(logging.Formatter):
    import numpy as np
    gray, red, green, yellow, blue, magenta, cyan, white = ['0;%d' % int(d) for d in (30 + np.arange(8))]
    bold_black, bold_red, bold_green, bold_yellow, bold_blue, bold_magenta, bold_cyan, bold_white = ['1;%d' % d for d in 90 + np.arange(8)]
    gray = '1;30'
    reset_seq = "\033[0m"
    color_seq = "\033[%(color)sm"
    colors = {
               'VERBOSE':  gray,
               'DEBUG':    cyan,
               'INFO':     green,
               'WARNING':  bold_yellow,
               'ERROR':    red,
               'CRITICAL': bold_red,
               'FATAL':    bold_red,
             }

    def __init__(self, msg, use_color = False):
      if use_color:
        logging.Formatter.__init__(self, self.color_seq + msg + self.reset_seq )
      else:
        logging.Formatter.__init__(self, msg)
      self.use_color = use_color

    def format(self, record):
      if not(hasattr(record,'nl')):
        record.nl = True
      levelname = record.levelname
      if not 'color' in record.__dict__ and self.use_color and levelname in self.colors:
        record.color = self.colors[levelname]
      return logging.Formatter.format(self, record)
  import os, sys
  formatter = Formatter(
                       "%(asctime)s | Py.%(name)-33.33s %(levelname)7.7s %(message)s",
                       not(int(os.environ.get('RCM_NO_COLOR',1)) or not(sys.stdout.isatty()))
                       )
  return formatter

# create console handler and set level to notset
def _getConsoleHandler(handler = None):
  import sys
  if handler is None:
    ch = logging.StreamHandler( sys.__stdout__ )
  else:
    ch = logging.StreamHandler(  handler  )
  ch.setLevel( logging.NOTSET ) #  Minimal level in which the ch will print
  # add formatter to ch
  ch.setFormatter(_getFormatter())
  return ch

def _setOutputLevel(self, value):
  logging.Logger.setLevel(self, value)
  self._ringercore_logger_parent._level = value


class StringLogger( object ):
  """
    Simple class for giving inherited classes logging capability as well as the
    possibility for being serialized by pickle.
    Logger will keep its logging level even after unpickled.
  """

  _formatter = _getFormatter()
  _stringIO = StringIO()
  _ch = _getConsoleHandler(_stringIO)

  def getLevel(self):
    if hasattr( self, '_level' ):
      return LoggingLevel.tostring( self._level )
    else:
      return LoggingLevel.INFO

  def setLevel(self, value):
    from Gaugi.gtypes import NotSet
    if value not in (None, NotSet):
      self._level = LoggingLevel.retrieve( value )
      if self._logger.level != self._level:
        self._logger.setLevel(self._level)
      #masterLevel.unhandle( self._logger )

  level = property( getLevel, setLevel )

  @classmethod
  def getModuleLogger(cls, logName, logDefaultLevel = None):
    """
      Retrieve logging stream handler using logName and add a handler
      to stdout if it does not have any handlers yet.
      Format logging stream handler to output in the same format used by Athena
      messages.
    """
    # Retrieve root logger
    rootLogger = logging.getLogger()
    rootHandlers = rootLogger.handlers
    for rH in rootHandlers:
      if isinstance(rH,logging.StreamHandler):
        rH.setFormatter(cls._formatter)
        # This may not be the desired behavior in some cases, but this fixes
        # the streamer created by ipython notebook
        import sys
        if rH.stream is sys.stderr:
          rH.stream = sys.stdout
    # Retrieve the logger
    logger = logging.getLogger( logName )
    # Retrieve handles:
    # TODO allow to set handlers filters
    handlers = logger.handlers
    if not cls._ch in handlers:
      # add ch to logger
      logger.addHandler(cls._ch)
    if logDefaultLevel is not None: # Override this log level until next change of masterLevel value
      logger.setLevel( logDefaultLevel )
    return logger

  #
  # Methods for StringIO
  #
  def getOutput(self):
    return self._stringIO.getvalue()

  def flushOutput(self):
    self._stringIO.truncate(0)
    return self._stringIO.seek(0)

  def __init__(self, d = {}, **kw ):
    """
      Retrieve from args the logger, or create it using default configuration.
    """

    d.update( kw )
    from Gaugi import retrieve_kw
    from Gaugi.gtypes import NotSet
    if 'level' in d:
      if d['level'] not in (None, NotSet):
        self._level = LoggingLevel.retrieve( retrieve_kw(d, 'level') )
      else:
        d.pop('level')
    self._logger = retrieve_kw(d,'logger', None)  or \
        self.getModuleLogger( d.pop('logName', self.__class__.__name__), LoggingLevel.retrieve( self.getLevel() ) )
    self._logger.verbose('Initialiazing %s', self.__class__.__name__)
    self._logger._ringercore_logger_parent = self
    if self._logger.level != LoggingLevel.MUTE:
      import types
      self._logger.setLevel = types.MethodType( _setOutputLevel, self._logger )
    else:
      self.level = LoggingLevel.MUTE
    def check_add( f ):
      fname = f.__name__
      self.__dict__['_' + fname] =  f
    #l = self._logger
    #for f in ( l.verbose, l.debug, l.info
    #         , l.warning, l.error, l.critical
    #         , l.fatal ):
    #  check_add(f)

  def __getattr__(self, attr):
    if attr.startswith('_') and  attr.lstrip('_') in ( 'verbose', 'debug', 'info'
                                                     , 'warning', 'error', 'critical'
                                                     , 'fatal'):
      return getattr( self._logger, attr.lstrip('_') )
    raise AttributeError( 'AttributeError was raised inside an instance of Logger class while attempting to get: %s' % attr )

  def __getstate__(self):
    """
      Makes logger invisible for pickle
    """
    odict = self.__dict__.copy() # copy the dict since we change it
    if '_logger' in odict: del odict['_logger']         # remove logger entry
    return odict

  def __setstate__(self, d):
    """
      Add logger to object if it doesn't have one:
    """
    self.__dict__.update(d)   # update attributes
    try:
      if self._logger is None: # Also add a logger if it is set to None
        self._logger = self.getModuleLogger(self.__class__.__name__, self.level )
    except AttributeError:
      self._logger = self.getModuleLogger(self.__module__, self.level )
    self._logger.setLevel( self.level )