#!/usr/bin/env python3

from GaugiKernel          import LoggingLevel, Logger
from GaugiKernel          import GeV
from CaloClusterBuilder   import CaloClusterMaker
from CaloRingsBuilder     import CaloRingsMaker, CaloRpRingsMaker
from CaloCell.CaloDefs    import CaloSampling
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


  from RootStreamBuilder import RootStreamESDReader, recordable
  ESD = RootStreamESDReader("ESDReader", 
                            InputFile       = args.inputFile,
                            CellsKey        = recordable("Cells"),
                            EventKey        = recordable("EventInfo"),
                            TruthKey        = recordable("Particles"),
                            NtupleName      = "CollectionTree",
                          )
  ESD.merge(acc)


  # build cluster for all seeds
  cluster = CaloClusterMaker( "CaloClusterMaker",
                              CellsKey        = recordable("Cells"),
                              EventKey        = recordable("EventInfo"),
                              ClusterKey      = recordable("Clusters"),
                              TruthKey        = recordable("Particles"),
                              EtaWindow       = 0.4,
                              PhiWindow       = 0.4,
                              MinCenterEnergy = 1*GeV, 
                              Alpha           = 2.02,
                              Beta            = 0.38,
                              Kappa           = 1,
                              Gamma           = 1,
                              HistogramPath   = "Expert/Clusters",
                              OutputLevel     = outputLevel )

  rings   = CaloRingsMaker(   "CaloRingsMaker",
                              RingerKey     = recordable("Rings"),
                              ClusterKey    = recordable("Clusters"),
                              DeltaEtaRings = [0.025,0.00325, 0.025, 0.050, 0.1, 0.1, 0.2 ],
                              DeltaPhiRings = [pi/32, pi/32, pi/128, pi/128, pi/128, pi/32, pi/32, pi/32],
                              NRings        = [8, 64, 8, 8, 4, 4, 4],
                              LayerRings = [
                                [CaloSampling.PSB, CaloSampling.PSE],
                                [CaloSampling.EMB1, CaloSampling.EMEC1],
                                [CaloSampling.EMB2, CaloSampling.EMEC2],
                                [CaloSampling.EMB3, CaloSampling.EMEC3],
                                [CaloSampling.HEC1, CaloSampling.TileCal1, CaloSampling.TileExt1],
                                [CaloSampling.HEC2, CaloSampling.TileCal2, CaloSampling.TileExt2],
                                [CaloSampling.HEC3, CaloSampling.TileCal3, CaloSampling.TileExt3],
                              ],
                              HistogramPath = "Expert/Rings",
                              OutputLevel   = outputLevel)
  
  rprings   = CaloRpRingsMaker(   "CaloRpRingsMaker",
                              RingerKey     = recordable("RpRings"),
                              ClusterKey    = recordable("Clusters"),
                              DeltaEtaRings = [0.025,0.00325, 0.025, 0.050, 0.1, 0.1, 0.2 ],
                              DeltaPhiRings = [pi/32, pi/32, pi/128, pi/128, pi/128, pi/32, pi/32, pi/32],
                              NRings        = [8, 64, 8, 8, 4, 4, 4],
                              LayerRings = [
                                [CaloSampling.PSB, CaloSampling.PSE],
                                [CaloSampling.EMB1, CaloSampling.EMEC1],
                                [CaloSampling.EMB2, CaloSampling.EMEC2],
                                [CaloSampling.EMB3, CaloSampling.EMEC3],
                                [CaloSampling.HEC1, CaloSampling.TileCal1, CaloSampling.TileExt1],
                                [CaloSampling.HEC2, CaloSampling.TileCal2, CaloSampling.TileExt2],
                                [CaloSampling.HEC3, CaloSampling.TileCal3, CaloSampling.TileExt3],
                              ],
                              HistogramPath = "Expert/RpRings",
                              RpInit = [0, 8, 72, 80, 88, 92, 96],
                              Alpha  = 2.02,
                              Beta   = 0.38,
                              OutputLevel   = outputLevel)

  from RootStreamBuilder import RootStreamAODMaker
  AOD = RootStreamAODMaker( "RootStreamAODMaker",
                            InputCellsKey        = recordable("Cells"),
                            InputEventKey        = recordable("EventInfo"),
                            InputTruthKey        = recordable("Particles"),
                            InputRingerKey       = recordable("Rings"),
                            InputRpRingerKey     = recordable("RpRings"),
                            InputClusterKey      = recordable("Clusters"),
                            OutputCellsKey       = recordable("Cells"),
                            OutputEventKey       = recordable("EventInfo"),
                            OutputTruthKey       = recordable("Particles"),
                            OutputRingerKey      = recordable("Rings"),
                            OutputRpRingerKey    = recordable("RpRings"),
                            OutputClusterKey     = recordable("Clusters"),
                            DumpCells            = True,
                            OutputLevel          = outputLevel)
      
  # sequence
  acc+= cluster
  acc+= rings
  acc+= rprings
  acc+= AOD

  acc.run(args.numberOfEvents)

  del acc
  sys.exit(0)
  
except  Exception as e:
  print(e)
  sys.exit(1)
