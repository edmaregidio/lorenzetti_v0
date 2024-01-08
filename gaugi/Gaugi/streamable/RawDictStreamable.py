__all__ = ['RawDictStreamable', 'RawDictStreamer', 'RawDictCnv', 'mangle_attr',
           'LoggerStreamable', 'LoggerRawDictStreamer', 'checkAttrOrSetDefault',
           'isRawDictFormat', 'retrieveRawDict']

from Gaugi.messenger import Logger

mLogger = Logger.getModuleLogger( __name__ )

def mangle_attr(source, attr):
  """
  Simulate python private attritubutes mangling. Taken from:
  http://stackoverflow.com/a/7789483/1162884
  """
  # return public attrs unchanged
  if not attr.startswith("__") or attr.endswith("__") or '.' in attr:
    return attr
  # if source is an object, get the class
  if not hasattr(source, "__bases__"):
    source = source.__class__
  # mangle attr
  return "_%s%s" % (source.__name__.lstrip("_"), attr)

class RawDictStreamer( Logger ):
  """
  This is the default streamer class, responsible of converting python classes
  to raw dictionaries.
  """

  def __init__(self, transientAttrs = set(), toPublicAttrs = set(), **kw):
    "Initialize streamer and declare transient variables."
    Logger.__init__(self, kw)
    self.transientAttrs = set(transientAttrs) | {'_readVersion',}
    self.toPublicAttrs = set(toPublicAttrs)
    from Gaugi import checkForUnusedVars
    checkForUnusedVars( kw, self._logger.warning )

  def preCall(self, obj):
    "Overload this method if you want to make special treatments before streaming the object."
    pass

  def __call__(self, obj):
    "Return a raw dict object from itself"
    self.preCall(obj)
    raw = { key : val for key, val in obj.__dict__.items() if key not in self.transientAttrs }
    for searchKey in self.toPublicAttrs:
      publicKey = searchKey.lstrip('_')
      searchKey = mangle_attr(obj, searchKey)
      if searchKey in raw:
        self._verbose( "Transforming '%s' attribute to public attribute '%s'.",
                              searchKey,
                              publicKey )
        raw[publicKey] = raw.pop(searchKey)
      else:
        self._fatal("Cannot transform to public key attribute '%s'", searchKey, KeyError)
    for key, val in raw.items():
      try:
        streamable = issubclass( val.__metaclass__, RawDictStreamable)
      except AttributeError:
        streamable = False
      if not hasattr(val, "__bases__"):
        cl = val.__class__
      else:
        cl = val
      if streamable or isinstance( cl, RawDictStreamable):
        self._verbose( "Found a streamable instance of type '%s' on attribute named '%s'."
                     , cl.__name__
                     , key )
        raw[key] = val.toRawObj()
    from copy import copy
    raw = copy( raw )
    raw['class'] = obj.__class__.__name__
    raw['__module'] = obj.__class__.__module__
    try:
      raw['__version'] = raw.pop('_version')
    except KeyError:
      raw['__version'] = obj.__class__._version
    return self.treatDict( obj, raw )

  def treatDict(self, obj, raw):
    """
    Method dedicated to modifications on raw dictionary
    """
    return raw

  def deepCopyKey(self, raw, key):
    """
    Helper method for deepcopying dict key.
    """
    if key in raw:
      from copy import deepcopy
      raw[key] = deepcopy(raw[key])
    else:
      self._warning("Cannot deepcopy key(%s) as it does not exists on rawDict.", key)

class RawDictCnv( Logger ):
  """
  This is the default converter class: it transforms raw dictionaries saved
  using RawDictStreamer into python classes.
  """
  # FIXME: class should be __class. How to treat __class so that matlab can
  # read it as well?

  baseAttrs = {'class' , '__version', '__module'}

  def __init__(self, ignoreAttrs = set(), toProtectedAttrs = set(), ignoreRawChildren = False, **kw ):
    """
      -> ignoreAttrs: not consider this attributes on the dictionary values.
      -> toProtectedAttrs: change public attributes to protected or private
        attributes. That is, suppose the dictionary value is 'val' and the class
        value should be _val or __val, then add toProtectedAttrs = ['_val'] or
        '__val'.
      -> ignoreRawChildren: Do not attempt to conver raw children to higher level object.
    """
    Logger.__init__(self, kw)
    ignoreAttrs = list(set(ignoreAttrs) | RawDictCnv.baseAttrs)
    import re
    self.ignoreAttrs = [re.compile(ignoreAttr) for ignoreAttr in ignoreAttrs]
    self.toProtectedAttrs = set(toProtectedAttrs)
    self.ignoreRawChildren = ignoreRawChildren
    from Gaugi import checkForUnusedVars
    checkForUnusedVars( kw, self._logger.warning )

  def _searchAttr(self, val):
    return [protectedAttr.lstrip('_') for protectedAttr in self.toProtectedAttrs].index(val)

  def preCall(self, obj, d):
    "Overload this method if you want to make special treatments before streaming the object."
    return obj, d

  def __call__(self, obj, d):
    """
    Add information to python class from dictionary d
    """
    obj, d = self.preCall(obj, d)
    try:
      obj._readVersion = d['__version']
    except KeyError:
      obj._readVersion = 0
    for k in d:
      if any([bool(ignoreAttr.match(k)) for ignoreAttr in self.ignoreAttrs]): 
        continue
      try:
        # We only load val if it is not in ignoredAttr
        val = d[k]
        nK = mangle_attr( self.__class__, 
                          list(self.toProtectedAttrs)[self._searchAttr(k)] 
                        )
        if not self.ignoreRawChildren:
          obj.__dict__[nK] = retrieveRawDict( val, logger = self._logger )
        else:
          obj.__dict__[nK] = val
        continue
      except ValueError:
        pass
      if not self.ignoreRawChildren:
        obj.__dict__[k] = retrieveRawDict( val, logger = self._logger )
      else:
        obj.__dict__[k] = val
    ret = self.treatObj( obj, d )
    return ret

  def treatObj( self, obj, d ):
    """
    Overload this method to treat the python object
    """
    return obj

  def __getstate__(self):
    """
      Makes logger invisible for pickle
    """
    odict = Logger.__getstate__(self)
    #def getStr(i):
    #  if isinstance(i, re
    if 'ignoreAttrs' in odict:
      s = odict['ignoreAttrs']
      def getStr(c):
        try:
          return  c.pattern
        except AttributeError:
          return c
      odict['ignoreAttrs'] = [getStr(v) for v in s]
    return odict

  def __setstate__(self, d):
    """
      Add logger to object if it doesn't have one:
    """
    v = d.pop('ignoreAttrs')
    self.__dict__['ignoreAttrs'] = [re.compile(s) for s in v]
    Logger.__setstate__(self,d)


def isRawDictFormat( d ):
  """
  Returns if dictionary is on streamed raw dictionary format.
  """
  isRawDictFormat = False
  if type(d) is dict and \
      all( baseAttr in d for baseAttr in RawDictCnv.baseAttrs ):
    isRawDictFormat = True
  return isRawDictFormat


def retrieveRawDict( val, logger = mLogger ):
  """
  Transform rawDict to an instance from its respective python class
  """
  if isRawDictFormat( val ):
    try:
      from Gaugi import str_to_class
      logger.verbose( "Converting rawDict to an instance of type '%s'." % val['class'] )
      cls = str_to_class( val['__module'], val['class'] )
      val = cls.fromRawObj( val )
    except KeyError as e:
      logger.error("Couldn't convert rawDict to an instance of type '%s'!\n Reason: %s", val['class'], e)
  return val

import re
_lMethodSearch=re.compile("_RawDictStreamable__(\S+)")

def checkAttrOrSetDefault( key, dct, bases, defaultType ):
  """
  Check if class factory attribute exists and is a defaultType instance. 
  Otherwise set it to defaultType.
  """
  if not key in dct:
    dct[key] = defaultType()
    for base in bases:
      if key in base.__dict__:
        dct[key] = getattr(base,key)
  else:
    if not isinstance(dct[key], defaultType):
      if type(dct[key]) is type:
        dct[key] = dct[key]()
      if not isinstance(dct[key], defaultType):
        raise ValueError("%s must be a %s instance." % (key, defaultType.__name__,) )

class RawDictStreamable( type ):
  """
  Class factory which adds streaming to python raw dictionary capability when
  using the _streamerObj attribute which should inherit from the
  RawDictStreamer class. When not specified, it is set to a standard
  RawDictStreamer instance.
  
  The dict can be transformed back into the python class using the _cnvObj
  attribute which must inherit from the RawDictCnv class. When not specified,
  it is set to a standard RawDictCnv instance.

  The version is specified using the _version attribute. Default value is 0.
  """

  def __new__(cls, name, bases, dct):
    import inspect
    import sys
    for localFcnName, fcn in inspect.getmembers( sys.modules[__name__], \
        inspect.isfunction):
      m = _lMethodSearch.match(localFcnName)
      if m:
        fcnName = m.group(1)
        if not fcnName in dct:
          dct[fcnName] = fcn
    ## Take care to _streamerObj and _cnvObj be in the right specification
    checkAttrOrSetDefault( '_streamerObj', dct, bases, RawDictStreamer )
    checkAttrOrSetDefault( '_cnvObj',      dct, bases, RawDictCnv      )
    if not '_version' in dct:
      dct['_version'] = 1
    if not type(dct['_version']) is int:
      raise ValueError("_version must be declared as an int.")
    dct['_readVersion'] = 0
    return type.__new__(cls, name, bases, dct)

  def fromRawObj(cls, obj, workOnCopy = False, **kw):
    """
      Builds an instance of this class using RawDict obj.
      -> workOnCopy: if set to false, it will change the input rawDict values,
      otherwise work on a deep copy.
      -> kw: Changes attributes from RawDictCnv object.
    """
    from copy import deepcopy
    if workOnCopy:
      obj = deepcopy( obj )
    self = cls()
    # NOTE: We always replace the cnvObj by the one available in the class to
    # ensure that it will behave as desired in case it is used to read an 
    # object twice, though this will probably very rarely (if ever) be used.
    self._cnvObj = deepcopy(cls._cnvObj)
    if kw:
      for key, val in kw.items():
        setattr( self._cnvObj, key, val)
    self = self.buildFromDict( obj )
    # Delete instance specific converter
    if kw: del self._cnvObj
    return self

def _RawDictStreamable__toRawObj(self):
  "Return a raw dict object from itself"
  raw = self._streamerObj( self )
  return raw

def _RawDictStreamable__buildFromDict(self, d):
  self = self._cnvObj( self, d )
  return self

class LoggerRawDictStreamer(RawDictStreamer):
  """
  Deal logger object streaming. All streaming Logger objects should have
  _streamerObj inheriting from this class.
  """
  
  transientAttrs = {'_logger','_level'}

  def __init__(self, transientAttrs = set(), toPublicAttrs = set(), **kw):
    transientAttrs = set(transientAttrs) | LoggerRawDictStreamer.transientAttrs
    RawDictStreamer.__init__(self, transientAttrs, toPublicAttrs, **kw)


# Extend support ti python 2 and 3 for metaclass
# See: https://stackoverflow.com/questions/22409430/portable-meta-class-between-python2-and-python3
import six
#class LoggerStreamable( Logger, metaclass=RawDictStreamable ): # Python 3 style
class LoggerStreamable( six.with_metaclass(RawDictStreamable, Logger) ):
  """
  Logger class with RawDictStreamer capabilities.
  """
  #__metaclass__ = RawDictStreamable # python 2 style
  _streamerObj = LoggerRawDictStreamer
  _version = 1

  def __init__(self, d = {}, **kw): 
    #RawDictStreamable.__init__(self, d, **kw)
    Logger.__init__(self, d, **kw)

