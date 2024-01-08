#!/usr/bin/env python

from Gaugi.messenger import LoggingLevel, Logger
import argparse
mainLogger = Logger.getModuleLogger("prometheus.merge")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

parser.add_argument('-i','--inputFiles', action='store', 
    dest='fList', required = True, nargs='+',
    help = "The input files.")

parser.add_argument('-o','--outputFile', action='store', 
    dest='output', required = True, default = 'merged.root',
    help = "The output file name.")

parser.add_argument('-nm','--nFilesPerMerge', action='store', 
    dest='nFilesPerMerge', required = False, default = 20, type=int,
    help = "The number of files per merge")

parser.add_argument('-mt','--numberOfThreads', action='store', 
    dest='mt', required = False, default = 8, type=int,
    help = "The number of threads")



import sys,os
if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)
args = parser.parse_args()

from Gaugi.mainloop import Merge
job = Merge(args.fList)
job.launch( args.output, args.nFilesPerMerge, args.mt)




