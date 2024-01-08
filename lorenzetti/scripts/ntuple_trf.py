#!/usr/bin/env python3

from GaugiKernel          import LoggingLevel, Logger
from GaugiKernel          import GeV
from G4Kernel             import *
import numpy as np
import argparse
import sys,os
pi = np.pi


mainLogger = Logger.getModuleLogger("job")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()


parser.add_argument('-i','--inputFile', action='store', dest='inputFile', required = False,
                    help = "The event input file generated by the Pythia event generator.")

parser.add_argument('-o','--outputFile', action='store', dest='outputFile', required = False,
                    help = "The reconstructed event file generated by lzt/geant4 framework.")

parser.add_argument('--nov','--numberOfEvents', action='store', dest='numberOfEvents', required = False, type=int, default=-1,
                    help = "The number of events to apply the reconstruction.")

parser.add_argument('-l', '--outputLevel', action='store', dest='outputLevel', required = False, type=str, default='INFO',
                    help = "The output level messenger.")




if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()

outputLevel = LoggingLevel.fromstring(args.outputLevel)

try:


  from GaugiKernel import ComponentAccumulator
  acc = ComponentAccumulator("ComponentAccumulator", args.outputFile)


  from RootStreamBuilder import RootStreamNTUPLEMaker, recordable
  NTUPLE = RootStreamNTUPLEMaker("NTUPLEMaker", 
                            InputFile       = args.inputFile,
                            CellsKey        = recordable("Cells"),
                            EventKey        = recordable("EventInfo"),
                            TruthKey        = recordable("Particles"),
                            ClusterKey      = recordable("Clusters"),
                            RingerKey       = recordable("Rings"),
                            RpRingerKey     = recordable("RpRings"),
                            NtupleName      = "physics",
                            OutputLevel     = outputLevel,
                            OutputNtupleName = "events",
                          )
  


  NTUPLE.merge(acc)
  
  acc.run(args.numberOfEvents)

  del acc
  sys.exit(0)
  
except  Exception as e:
  print(e)
  sys.exit(1)
