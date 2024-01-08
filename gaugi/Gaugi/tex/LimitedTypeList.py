
__all__ = ['LimitedTypeList',  'NotAllowedType']

import re
_lMethodSearch=re.compile("_LimitedTypeList__(\S+)")

class LimitedTypeList (type):
  """
    LimitedTypeList metaclass create lists which only accept declared types.

    One LimitedTypeList class must specify _acceptedTypes property as a tuple,
    which will be the only types accepted by the list.

    In case a class inherits from another classes that declare _acceptedTypes 
    and it does not declare this class attribute, then the first base class
    _acceptedTypes will be used.

    If none of the inherited classes define the __init__ method, the list 
    init method will be used. In case you have a inherited class with __init__
    method (case where the base class has __metaclass__ set to LimitedTypeList)
    and want to enforce that this class will use their own __init__ method, then
    set _useLimitedTypeList__init__ to True. If you do so, then the __init__ you declare
    will be overridden by the LimitedTypeList.
  """

  # TODO Add boolean to flag if the class can hold itself

  def __new__(cls, name, bases, dct):
    if not any( [ issubclass(base, list) for base in bases ] ):
      bases = (list,) + bases 
    import inspect
    import sys
    hasBaseInit = any([hasattr(base,'__init__') for base in bases if base.__name__ not in 
                                                                    ("list", "object", "Logger", "LoggerStreamable",)])
    for localFcnName, fcn in inspect.getmembers( sys.modules[__name__], inspect.isfunction):
      m = _lMethodSearch.match(localFcnName)
      if m:
        fcnName = m.group(1)
        if not fcnName in dct:
          if hasBaseInit and fcnName == '__init__' and not dct.get('_useLimitedTypeList__init__', False):
            continue
          dct[fcnName] = fcn
    return type.__new__(cls, name, bases, dct)

  def __init__(cls, name, bases, dct):
    ## Take care to _acceptedTypes be in the right specification
    if not '_acceptedTypes' in dct:
      for base in bases:
        if hasattr(base, '_acceptedTypes'):
          acceptedTypes = base._acceptedTypes
          break
      dct['_acceptedTypes'] = acceptedTypes
    else:
      acceptedTypes = dct['_acceptedTypes']
    if not type(acceptedTypes) is tuple:
      raise ValueError("_acceptedTypes must be declared as a tuple.")
    if not acceptedTypes:
      raise ValueError("_acceptedTypes cannot be empty.")
    return type.__init__(cls, name, bases, dct)

  def __call__(cls, *args, **kw):
    return type.__call__(cls, *args, **kw)


def _LimitedTypeList__setitem(self, k, var):
  """
    Default override setitem
  """
  # This is default overload for list setitem, checking if item is accepted
  if not isinstance(var, self._acceptedTypes):
    raise NotAllowedType(self, var, self._acceptedTypes)
  list.setitem(self, k, var)

def _LimitedTypeList__append(self, var):
  """
    Default append method
  """
  # This is default overload for list append, checking if item is accepted
  if not isinstance(var, self._acceptedTypes):
    raise NotAllowedType( self, var, self._acceptedTypes)
  list.append(self,var)

#def _LimitedTypeList__pop(self, index = -1):
#  """
#    Default append method
#  """
#  if self.__class__.__name__ == "_TexObjectContextManager":
#    print ":: poping ", repr(self[index]), " from TexObjectContextManager ::"
#    import traceback
#    print "STACK:", ''.join(traceback.format_stack())
#  list.pop(self, index)
#
def _LimitedTypeList__extend(self, var):
  """
    Default append method
  """
  # This is default overload for list append, checking if item is accepted
  if not isinstance(var, self._acceptedTypes):
    raise NotAllowedType( self, var, self._acceptedTypes)
  list.extend(self,var)

def _LimitedTypeList____add__(self, var):
  """
    Default __add__ method
  """
  if type(var) in (list, tuple, type(self)):
    for value in var:
      if not isinstance(value, self._acceptedTypes):
        raise NotAllowedType( self, value, self._acceptedTypes )
  else:
    if not isinstance(var, self._acceptedTypes):
      raise NotAllowedType( self, var, self._acceptedTypes)
    var = [ var ]
  # This is default overload for list iadd, checking if item is accepted
  copy = list.__add__(self, var)
  return copy 

# Uncomment this in case you want to have LimitedTypeLists Specifying its type
#def _LimitedTypeList____str__(self):
#  """
#    Default __str__ method
#  """
#  return '< ' + self.__class__.__name__ + list.__str__(self) + ' >'

#def _LimitedTypeList____repr__(self):
#  """
#    Default __repr__ method
#  """
#  return '< ' + self.__class__.__name__ + list.__repr__(self) + ' >'

def _LimitedTypeList____iadd__( self, var, *args ):
  """
    Default __iadd__ method
  """
#  if self.__class__.__name__ == "_TexObjectContextManager":
#    print ":: adding ", repr(var), " to TexObjectContextManager ::"
#    import traceback
#    print "STACK:", ''.join(traceback.format_stack())
  for arg in args:
    if not isinstance( arg, self._acceptedTypes ):
      raise NotAllowedType( self, arg, self._acceptedTypes )
  if type(var) in (list, tuple, type(self)):
    for value in var:
      if not isinstance( value, self._acceptedTypes ):
        raise NotAllowedType( self, value, self._acceptedTypes )
  else:
    if not isinstance(var, self._acceptedTypes):
      raise NotAllowedType( self, var, self._acceptedTypes)
    var = [ var ]
  # This is default overload for list iadd, checking if item is accepted
  list.__iadd__(self, var)
  if args:
    list.__iadd__(self, args)
  return self


def _LimitedTypeList____init__( self, *args ):
  """
    Default __init__ method
  """
  if args:
    self.__iadd__(*args)

def _LimitedTypeList____call__( self ):
  """
    Default __call__ method.
    Yield holden objects.
  """
  for obj in self:
    yield obj

class NotAllowedType(ValueError):
  """
    Raised by LimitedTypeList to sign that it was attempted to add an item to the
    list which is not an allowedType instance.
  """
  def __init__( self , obj, input_, allowedTypes ):
    ValueError.__init__(self, ("Attempted to add to %s an object (type=%s) which is not an "
      "instance from the allowedTypes: %s!") % (obj.__class__.__name__, type(input_),allowedTypes,) )


