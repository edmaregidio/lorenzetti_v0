__all__ = ["Property"]


#
# Property obejct
#
class Property( object ):


  #
  # Constructor
  #
  def __init__( self, name, value = None, comment = ""):

    self.__name = name
    self.__value = value
    self.__comment = comment


  #
  # Get the proeperty description
  #
  def comment(self):
    return self.__coment


  #
  # Get the property value
  #
  def value(self):
    return self.__value

  #
  # Check if the value is notset
  #
  def isValid(self):
    return False if self.__value is None else True


  #
  # Set the property value
  #
  def setValue(self, value):
    self.__value = value


