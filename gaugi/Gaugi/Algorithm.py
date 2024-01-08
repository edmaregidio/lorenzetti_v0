
__all__ = ['Algorithm']

from Gaugi.messenger import  Logger
from Gaugi.messenger.macros import *
from Gaugi.enumerations import StatusTool, StatusWTD
from Gaugi import EnumStringification
from Gaugi import NotSet
from Gaugi import StatusCode
from Gaugi import Property



# Base class used for all tools for this framework
class Algorithm( Logger ):

  def __init__(self, name):
    Logger.__init__(self)
    self._name = name
    # flags
    self._wtd  = StatusWTD.DISABLE
    self._status = StatusTool.ENABLE
    self._initialized = StatusTool.NOT_INITIALIZED
    self._finalized = StatusTool.NOT_FINALIZED
    # services and EDMs
    self._context   = NotSet
    self._storegateSvc = NotSet
    self._dataframe = NotSet

    # property 
    self.__property = {}




  #
  # Declare property
  #
  def declareProperty( self, key, value = None, comment = "" ):
    if not key in self.__property.keys():
      self.__property[ key ] = Property(key, value, comment)
      self.__dict__[key] = value
    else:
      MSG_FATAL( self, "Property with name %s was configure before.", key )


	#
	# Set the value of the property
	#	 
  def setProperty( self, key, value ):
    if key in self.__property:
      self.__property[key].setValue(value)
    else:
      MSG_FATAL( self, "Property with name %s is not in the %s object", key, self.__class__.__name__)


 	#
	# Get the value of the property
	#
  def getProperty( self, key ):
    if key in self.__property.keys():
      return self.__property[key].value()
    else:
      MSG_FATAL( self, "Property with name %s is not in the  %s object", key, self.__class__.__name__)




  def name(self):
    return self._name


  @property
  def dataframe(self):
    return self._dataframe


  @dataframe.setter
  def dataframe(self,v):
    self._dataframe = v


  def setContext( self, context ):
    self._context = context


  def getContext(self):
    return self._context


  def setStoreGateSvc(self,sg):
    self._storegateSvc=sg


  def getStoreGateSvc(self):
    return self._storegateSvc


  @property
  def storeSvc(self):
    if self._storegateSvc is not None:
      return self._storegateSvc
    else:
      MSG_FATAL( self, "Attempted to access storeSvc which wasn't set.")


  @storeSvc.setter
  def storeSvc(self, s):
    from Gaugi.storage import StoreGate
    if not isinstance(s, StoreGate):
      PRH_MSG_FATAL( self, "Attempted to set StoreGate to instance of non StoreGate type")
    self._storegateSvc=s



  def initialize(self):
    return StatusCode.SUCCESS


  def execute(self, context):
    self.setContext(context)
    self._wtd = StatusWTD.DISABLE
    return StatusCode.SUCCESS


  def finalize(self):
    return StatusCode.SUCCESS



  @property
  def wtd(self):
    "Retrieve the watch dog status"
    return self._wtd

  @wtd.setter
  def wtd(self, v):
    self._wtd = StatusWTD.retrieve(v)


  @property
  def status(self):
    return self._status



  def disable(self):
    MSG_INFO( self, 'Disable %s tool service.',self._name)
    self._status = StatusTool.DISABLE

  def enable(self):
    MSG_INFO( self, 'Enable %s tool service.',self._name)
    self._status = StatusTool.ENABLE



  def init_lock(self):
    self._initialized = StatusTool.IS_INITIALIZED

  def fina_lock(self):
    self._finalized = StatusTool.IS_FINALIZED



  def isInitialized(self):
    if self._initialized is StatusTool.IS_INITIALIZED:
      return True
    else:
      return False

  def isFinalized(self):
    if self._finalized is StatusTool.IS_FINALIZED:
      return True
    else:
      return False


