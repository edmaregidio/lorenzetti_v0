#!/usr/bin/env python

from Gaugi.messenger import LoggingLevel, Logger
import argparse

mainLogger = Logger.getModuleLogger("prometheus.job")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

parser.add_argument('-i','--inputFiles', action='store', 
    dest='fList', required = True, nargs='+',
    help = "The input files.")

parser.add_argument('-c','--command', action='store', 
    dest='command', required = True,
    help = "The command job")

parser.add_argument('-mt','--numberOfThreads', action='store', 
    dest='mt', required = False, default = 8, type=int,
    help = "The number of threads")



import sys,os
if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)
args = parser.parse_args()


from Gaugi.mainloop import Parallel
job = Parallel(args.fList)
job.launch( args.command, args.mt)



