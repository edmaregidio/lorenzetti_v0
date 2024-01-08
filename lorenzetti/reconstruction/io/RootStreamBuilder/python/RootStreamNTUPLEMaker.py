__all__ = ["RootStreamNTUPLEMaker"]

from GaugiKernel import Logger
from GaugiKernel.macros import *
from G4Kernel import treatPropertyValue


class RootStreamNTUPLEMaker( Logger ):

  __allow_keys = [
                  "EventKey",
                  "TruthKey",
                  "CellsKey",
                  "ClusterKey",
                  "RingerKey",
                  "RpRingerKey",
                  "OutputLevel", 
                  "NtupleName",
                  "InputFile",
                  "OutputNtupleName",
                  ]


  def __init__( self, name, **kw ): 
    
    Logger.__init__(self)
    import ROOT
    ROOT.gSystem.Load('liblorenzetti')
    from ROOT import RootStreamNTUPLEMaker
    self.__core = RootStreamNTUPLEMaker(name)

    for key, value in kw.items():
      self.setProperty( key,value )

    from ROOT import TFile, TTree 
    f = TFile( self.getProperty("InputFile"),"read")
    t = f.Get( self.getProperty("NtupleName"))
    self.__entries = t.GetEntries()


  def GetEntries(self):
    return self.__entries


  def core(self):
    return self.__core


  def setProperty( self, key, value ):
    if key in self.__allow_keys:
      setattr( self, '__' + key , value )
      self.core().setProperty( key, treatPropertyValue(value) )
    else:
      MSG_FATAL( self, "Property with name %s is not allow for %s object", key, self.__class__.__name__)

 
  def getProperty( self, key ):
    if key in self.__allow_keys:
      return getattr( self, '__' + key )
    else:
      MSG_FATAL( self, "Property with name %s is not allow for %s object", key, self.__class__.__name__)


  def merge(self, acc):
    acc.SetReader(self)
