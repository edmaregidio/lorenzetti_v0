__all__ = ['save', 'load', 'expandFolders', 'mkdir_p',
           'getExtension', 'checkExtension', 'changeExtension',
           'ensureExtension', 'appendToFileName', 'prependToFileName',
           'prependAppendToFileName', 'findFile',
           'getMD5','checkFile', 'WriteMethod', 'cat_files_py',
           'getFiles', 'expandPath', 'BadFilePath',
           'LockFile']

import numpy as np
import pickle as cPickle
import gzip
import tarfile
import tempfile
import os
import sys
import shutil
import signal
from time import sleep, time

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
  basestring
except NameError:
  basestring = str

class BadFilePath(ValueError): pass


# Python 3 fix
def convert(data):
  if isinstance(data, bytes):  return data.decode()
  if isinstance(data, dict):   return dict(map(convert, data.items()))
  if isinstance(data, tuple):  return tuple(map(convert, data))
  if isinstance(data, list):   return list(map(convert, data))
  return data




def expandPath(path):
  " Returns absolutePath path expanding variables and user symbols "
  if not isinstance( path, basestring):
    raise BadFilePath(path)
  try:
    return os.path.abspath( os.path.join(os.path.dirname(path), os.readlink( os.path.expanduser( os.path.expandvars( path ) ) ) ) )
  except OSError:
    return os.path.abspath( os.path.expanduser( os.path.expandvars( path ) ) )





def expandFolders( pathList, filters = None, logger = None, level = None):
  """
    Expand all folders to the contained files using the filters on pathList

    Input arguments:

    -> pathList: a list containing paths to files and folders;
    filters;
    -> filters: return a list for each filter with the files contained on the
    list matching the filter glob.
    -> logger: whether to print progress using logger;
    -> level: logging level to print messages with logger;

    WARNING: This function is extremely slow and will severely decrease
    performance if used to expand base paths with several folders in it.
  """
  if not isinstance( pathList, (list,tuple,) ):
    pathList = [pathList]
  from glob import glob
  if filters is None:
    filters = ['*']
  if not( type( filters ) in (list,tuple,) ):
    filters = [ filters ]
  retList = [[] for idx in range(len(filters))]
  from Gaugi.utilities import progressbar, traverse
  pathList = list(traverse([glob(path) if '*' in path else path for path in traverse(pathList,simple_ret=True)],simple_ret=True))
  for path in progressbar( pathList, len(pathList), 'Expanding folders: ', 60, 50,
                           True if logger is not None else False, logger = logger,
                           level = level):
    path = expandPath( path )
    if not os.path.exists( path ):
      raise ValueError("Cannot reach path '%s'" % path )
    if os.path.isdir(path):
      for idx, filt in enumerate(filters):
        cList = filter(lambda x: not(os.path.isdir(x)), [ f for f in glob( os.path.join(path,filt) ) ])
        if cList:
          retList[idx].extend(cList)
      folders = [ os.path.join(path,f) for f in os.listdir( path ) if os.path.isdir( os.path.join(path,f) ) ]
      if folders:
        recList = expandFolders( folders, filters )
        if len(filters) is 1:
          recList = [recList]
        for l in recList:
          retList[idx].extend(l)
    else:
      for idx, filt in enumerate(filters):
        if path in glob( os.path.join( os.path.dirname( path ) , filt ) ):
          retList[idx].append( path )
  if len(filters) is 1:
    retList = retList[0]
  return retList




def getExtension( filename, nDots = None):
  """
    Get file extension.

    Inputs:
    -> filename;
    -> nDots: the maximum number of dots extesions should have.
  """
  filename = filename.split('.')
  lParts = len(filename)
  if nDots is None: nDots = (lParts - 1)
  nDots = - nDots
  if nDots <= -lParts: nDots = - (lParts - 1)
  if nDots > -1:
    return ''
  return '.'.join(filename[nDots:])

def checkExtension( filename, ext, ignoreNumbersAfterExtension = True):
  """
    Check if file matches extension(s) ext. If checking for multiple
    extensions, use | to separate the extensions.
  """
  return bool(__extRE(ext, ignoreNumbersAfterExtension).match( filename ))







from Gaugi.messenger import Logger

class LockFile( Logger ):
  """
  Simple lock file
  """

  def __init__( self, path ):
    self.path = path
    if self.exists():
      self.path = None
      raise IOError( "Cannot create .lock file, file %s already exists." % self.path, self.path )
    open( self.path, 'w' ).close()
    self._prevSignal = signal.getsignal(signal.SIGTERM)
    signal.signal( signal.SIGTERM, self._abort )

  def exists( self ):
    return os.path.isfile( self.path )

  def _abort( self, signum, frame ):
    self.delete()
    if self._prevSignal: self._prevSignal(signum, frame )

  def delete( self ):
    if self.exists(): os.remove( self.path )

  def __del__( self ):
    self.delete()


def watchLock(filename):
  logger = Logger.getModuleLogger( "watchLock" )
  lockFileName = os.path.join( os.path.join( os.path.dirname(filename), '.' + os.path.basename(filename) + '.lock' ) )
  firstMsg = True
  while os.path.exists( lockFileName ):
    if firstMsg:
      logger.warning("Waiting other process to unlock file %s...", lockFileName )
      firstMsg = False
    sleep(1)
  lockFile = LockFile( lockFileName )
  return lockFile



def save(o, filename, **kw):
  """
    Save an object to disk.
  """
  compress = kw.pop( 'compress', True  )
  protocol = kw.pop( 'protocol', -1    )
  lock     = kw.pop( 'lock',     True  )
  dryrun   = kw.pop( 'dryrun',   False )
  if not isinstance(filename, str):
    raise("Filename must be a string!")
  filename = expandPath( filename )
  dirplace = os.path.dirname(filename)
  if not os.path.isdir( dirplace ) and dirplace:
    mkdir_p( dirplace )
  if type(protocol) is str:
    if protocol == "mat":
      filename = ensureExtension(filename, 'mat')
      if dryrun: return filename
      try:
        import scipy.io
        if lock: lockFile = watchLock( filename )
        scipy.io.savemat( filename, o)
      except ImportError as e:
        raise ImportError( "Exporting data in matlab extension is not available. Reason: %s" % e )
    elif protocol == "savez_compressed":
      filename = ensureExtension(filename, 'npz')
      if dryrun: return filename
      if lock: lockFile = watchLock( filename )
      if type(o) is dict:
        np.savez_compressed(filename, **o)
      else:
        if not isinstance(o, (list,tuple) ):
          o = (o,)
        np.savez_compressed(filename, *o)
    elif protocol == "savez":
      filename = ensureExtension(filename, 'npz')
      if dryrun: return filename
      if lock: lockFile = watchLock( filename )
      if type(o) is dict:
        np.savez(filename, **o)
      else:
        if not isinstance(o, (list,tuple) ):
          o = (o,)
        np.savez(filename, *o)
    elif protocol == "save":
      filename = ensureExtension(filename, 'npy')
      if dryrun: return filename
      if lock: lockFile = watchLock( filename )
      np.save(filename, o)
    else:
      raise ValueError("Unknown protocol '%s'" % protocol)
  elif type(protocol) is int:
    if compress:
      filename = ensureExtension(filename, 'pic.gz')
      if dryrun: return filename
      if lock: lockFile = watchLock( filename )
      f = gzip.GzipFile(filename, 'wb')
    else:
      filename = ensureExtension(filename, 'pic')
      if dryrun: return filename
      if lock: lockFile = watchLock( filename )
      f = open(filename, 'w')
    cPickle.dump(o, f, protocol)
    f.close()
  if lock:
    lockFile.delete()
  return filename



def load(filename, decompress = 'auto', allowTmpFile = True, useHighLevelObj = False,
         useGenerator = False, tarMember = None, ignore_zeros = True,
         extractAll = False, eraseTmpTarMembers = True,
         returnFileName = False, returnFileMember = False,
         logger = None):
  """
    Loads an object from disk.

    -> decompress: what protocol should be used to decompress the file.
    -> allowTmpFile: if to allow temporary files to improve loading speed.
    -> useHighLevelObj: automatic convert rawDicts to their python
       representation (not currently supported for numpy files.
    -> useGenerator: This option changes the behavior when loading a tarball
       file with multiple members. Instead returning a collection with all
       contents within the file, it will return a generator allowing each file
       to be read individually, thus reducing the amount of memory used in the
       process.
    -> tarMember: the tarMember in the tarfile to read. When not specified: read
    all.
    -> ignore_zeros: whether to ignore zeroed regions when reading tarfiles or
    not. This property is important for reading only one file from merged files
    in a fast manner.
    -> extractAll: expand every tar file members at once
    -> eraseTmpTarMembers: whether to erase tar members after reading them
    -> returnFileName: whether to return file name
    -> returnFileMember: whether to return file member object at the tar file
  """
  filename = expandPath( filename )
  transformDataRawData = __TransformDataRawData( useHighLevelObj, returnFileName, returnFileMember )
  if not os.path.isfile( filename ):
    raise ValueError("Cannot reach file %s" % filename )
  if checkExtension( filename, 'npy|npz'):
    #o = transformDataRawData( np.load(filename,mmap_mode='r'), filename, None )
    #return [o] if useGenerator else o
    return dict(np.load(filename))
  else:
    if decompress == 'auto':
      if checkExtension( filename, 'tar.gz|tgz' ):
        decompress = 'tgz'
      elif checkExtension( filename, 'gz|gzip' ):
        decompress = 'gzip'
      elif checkExtension( filename, 'tar' ):
        decompress = 'tar'
      elif checkExtension( filename, '.pic' ):
        decompress = False
      else:
        raise RuntimeError("It is not possible to read format: '.%s'. Input file was: '%s'." % (
          getExtension(filename, None),
          filename) )
    if decompress == 'gzip':
      f = gzip.GzipFile(filename, 'rb')
    elif decompress in ('tgz', 'tar'):
      args = (allowTmpFile, transformDataRawData,
              tarMember, extractAll, eraseTmpTarMembers,
              ignore_zeros, logger,)
      if decompress == 'tar':
        o = __load_tar(filename, 'r:', *args)
      else:
        o = __load_tar(filename, 'r:gz', *args)
      if not useGenerator:
        #o = list(map(lambda x: x[0], o))
        o = list(o)
        if len(o) == 1: o = o[0]
      return o
    else:
      f = open(filename,'r')

    try: # python 3
      o = cPickle.load(f,encoding='bytes')
      f.close()
      o = transformDataRawData( o, filename, None )
      # This is necessary for python 3
      o = convert(o)
    except: # python 2
      try:
          o = cPickle.load(f)
      except:
          import pickle5 as cPickle5
          o = cPickle5.load(f)
      f.close()
      o = transformDataRawData( o, filename, None )

    return [o] if useGenerator else o
  # end of (if filename)
# end of (load)




def __load_tar(filename, mode, allowTmpFile, transformDataRawData, tarMember,
               extractAll, eraseTmpTarMembers, ignore_zeros, logger = None):
  """
  Internal method for reading tarfiles
  """
  #useSubprocess = False
  useSubprocess = True
  if tarMember is None:
    f = tarfile.open(filename, mode, ignore_zeros = ignore_zeros)
    if not extractAll:
      if logger:
        logger.info("Retrieving tar file members (%s)...", "full" if ignore_zeros else "fast")
      memberList = f.getmembers()
  elif type(tarMember) in (tarfile.TarInfo, str):
    useSubprocess = True
    memberList = [tarMember]
  else:
    raise TypeError("tarMember argument must be TarInfo or None.")
  for entry in memberList if not extractAll else [None]:
    if allowTmpFile:
      tmpFolderPath=tempfile.mkdtemp()
      if useSubprocess:
        from subprocess import Popen, PIPE, CalledProcessError
        from Gaugi.utilities import is_tool
        tar_cmd = 'gtar' if is_tool('gtar') else 'tar'
        # TODO This will crash if someday someone uses a member in file that is
        # not in root path at the tarfile.
        if extractAll:
          start = time()
          logger.info("Proceeding to untar all members.")
          process_args = (tar_cmd, '--verbose', '-xvzif', filename,)
          untar_ps = Popen(process_args, stdout = PIPE, bufsize = 1,
                          cwd = tmpFolderPath)
          memberList = []
          with untar_ps.stdout:
            while True:
              outputLine = untar_ps.stdout.readline().strip('\n')
              if outputLine == '':
                if untar_ps.poll() is not None:
                  break
              else:
                memberList.append(outputLine)
                logger.debug(outputLine)
          return_code = untar_ps.wait()
          if return_code != 0:
            raise CalledProcessError(return_code, process_args)
          from re import compile
          rexp = compile('\s+')
          memberList = [(int(size), name) for _, _, size, _, _, name in map(lambda member: rexp.split(member), memberList)]
          end = time()
          logger.info("Untar file content took %.2fs", end - start )
        else:
          memberName = entry.name if type(entry) is tarfile.TarInfo else entry
          untar_ps = Popen((tar_cmd, '--verbose', '-xvzif', filename, memberName,
                           ), stdout = PIPE, bufsize = 1, cwd = tmpFolderPath)
          with untar_ps.stdout:
            from re import compile
            rexp = compile('\s+')
            for line in iter(untar_ps.stdout.readline, b''):
              line = line.strip('\n')
              _, _, size, _, _, name = rexp.split(line)
              memberList = [(int(size), name)]
              break
        for entry in memberList:
          memberSize, memberName = (entry.size, entry.name, ) if type(entry) is tarfile.TarInfo else entry
          oFile = os.path.join( tmpFolderPath, memberName )
          while not os.path.isfile( oFile ):
            sleep(0.001)
          while os.path.getsize( oFile ) != memberSize:
            sleep(0.001)
          if not extractAll:
            untar_ps.kill()
            untar_ps.wait()
          os.listdir( tmpFolderPath )
          with open( oFile ) as f_member:
            data = transformDataRawData( cPickle.load(f_member), oFile if extractAll else filename, memberName )
            yield data
        if extractAll:
          break
      if eraseTmpTarMembers:
        shutil.rmtree(tmpFolderPath)
    else:
      fileobj = f.extractfile(entry)
      if checkExtension( entry.name, 'gz|gzip' ):
        fio = StringIO.StringIO( fileobj.read() )
        fileobj = gzip.GzipFile( fileobj = fio )
      yield transformDataRawData( cPickle.load(fileobj), filename, memberName )
  if not useSubprocess:
    f.close()
# end of (load_tar)



class __TransformDataRawData( object ):
  """
  Transforms raw data if requested to use high level object
  """

  def __init__(self, useHighLevelObj, returnFileName, returnFileMember,):
    self.useHighLevelObj = useHighLevelObj
    self.returnFileName = returnFileName
    self.returnFileMember = returnFileMember

  def __call__(self, o, fname, tmember):
    """
    Run transformation
    """
    if self.useHighLevelObj:
      from Gaugi.streamable.RawDictStreamable import retrieveRawDict
      from numpy.lib.npyio import NpzFile
      if type(o) is NpzFile:
        o = dict(o)
      o = retrieveRawDict( o )
    from Gaugi.utilities import appendToOutput
    o = appendToOutput( o, self.returnFileName,   fname   )
    o = appendToOutput( o, self.returnFileMember, tmember )
    return o



def __extRE(ext, ignoreNumbersAfterExtension = True):
  """
  Returns a regular expression compiled object that will search for
  extension ext
  """
  import re
  if not isinstance( ext, (list,tuple,)): ext = ext.split('|')
  ext = [e[1:] if e[0] == '.' else e for e in ext]
  # remove all first dots
  return re.compile(r'(.*)\.(' + r'|'.join(ext) + r')' + \
                    (r'(\.[0-9]*|)' if ignoreNumbersAfterExtension else '()') + r'$')



def ensureExtension( filename, extL, ignoreNumbersAfterExtension = True ):
  """
  Ensure that filename extension is extL, else adds its extension.

  Extension extL may start with '.' or not. In case it does not, a dot will be
  added.

  A '|' may be specified to treat multiple extensions. In case either one of
  the extensions specified is found, nothing will be changed in the output,
  else the first extension will be added to the file.
  """
  if isinstance(extL, basestring) and '|' in extL:
    extL = extL.split('|')
  if not isinstance(extL, (list,tuple)):
    extL = [extL]
  extL = ['.' + e if e[0] != '.' else e for e in extL]

  # FIXME: This can be returned earlier by using filter
  if any([checkExtension(filename, ext, ignoreNumbersAfterExtension) for ext in extL]):
    return filename

  # FIXME We should check every extension and see how many composed matches we had before doing this
  ext = extL[0]
  composed = ext.split('.')
  if not composed[0]: composed = composed[1:]
  lComposed = len(composed)
  if lComposed > 1:
    for idx in range(lComposed):
      if filename.endswith( '.'.join(composed[0:idx+1]) ):
        filename += '.' + '.'.join(composed[idx+1:])
        break
    else:
      filename += ext
  else:
    filename += ext
  return filename



def changeExtension( filename, newExtension, knownFileExtensions = ['tgz', 'tar.gz', 'tar.xz','tar',
                                                                    'pic.gz', 'pic.xz', 'pic',
                                                                    'npz', 'npy', 'root'],
                      retryExtensions = ['gz', 'xz'],
                      moreFileExtensions = [],
                      moreRetryExtensions = [],
                      ignoreNumbersAfterExtension = True,
                    ):
  """
  Append string to end of file name but keeping file extension in the end.

  Inputs:
    -> filename: the filename path;
    -> newExtension: the extension to be used by the file;
    -> knownFileExtensions: the known file extensions, use to override all file extensions;
    -> retryExtensions: some extensions are inside other extensions, e.g.
    tar.gz and .gz. This makes regexp operator | to match the smaller
    extension, so the easiest solution is to retry the smaller extensions after
    checking the larger ones.
    -> moreFileExtensions: add more file extensions to consider without overriding all file extensions;
    -> moreRetryExtensions: add more extensions to consider while retrying without overriding the retryExtensions;
    -> ignoreNumbersAfterExtension: whether to ignore numbers after the file extensions or not.

  Output:
    -> the filename with the string appended.
  """
  knownFileExtensions.extend( moreFileExtensions )
  def repStr( newExt ):
    return r'\g<1>' + ( newExt if newExt.startswith('.') else ( '.' + newExt ) )
  str_ = __extRE( knownFileExtensions )
  m = str_.match( filename )
  if m:
    return str_.sub( repStr(newExtension), filename )
  str_ = __extRE( retryExtensions )
  m = str_.match( filename )
  if m:
    return str_.sub( repStr(newExtension), filename )
  else:
    return filename + newExtension



def prependAppendToFileName( filename, prependStr, appendStr, knownFileExtensions = ['tgz', 'tar.gz', 'tar.xz','tar',
                                                                                     'pic.gz', 'pic.xz', 'pic',
                                                                                     'npz', 'npy', 'root','pdf','jpg','jpeg'],
                      retryExtensions = ['gz', 'xz'],
                      moreFileExtensions = [],
                      moreRetryExtensions = [],
                      ignoreNumbersAfterExtension = True,
                      separator = '_'):


  filename = prependToFileName( prependStr, filename, separator )
  filename = appendToFileName( filename, appendStr, knownFileExtensions,
                      retryExtensions,
                      moreFileExtensions,
                      moreRetryExtensions,
                      ignoreNumbersAfterExtension,
                      separator )
  return filename



def prependToFileName( prependStr, filename, separator = '_'):
  """
  Prepend string to file name
  """
  if prependStr.endswith(separator): separator = ''
  return os.path.dirname(filename) + prependStr + separator + os.path.basename(filename)



def appendToFileName( filename, appendStr, knownFileExtensions = ['tgz', 'tar.gz', 'tar.xz','tar',
                                                                  'pic.gz', 'pic.xz', 'pic',
                                                                  'npz', 'npy', 'root','pdf','jpg','jpeg'],
                      retryExtensions = ['gz', 'xz'],
                      moreFileExtensions = [],
                      moreRetryExtensions = [],
                      ignoreNumbersAfterExtension = True,
                      separator = '_'):
  """
  Append string to file name but keeping file extension in the end.

  Inputs:
    -> filename: the filename path;
    -> appendStr: the string to be added to the filename;
    -> knownFileExtensions: the known file extensions, use to override all file extensions;
    -> retryExtensions: some extensions are inside other extensions, e.g.
    tar.gz and .gz. This makes regexp operator | to match the smaller
    extension, so the easiest solution is to retry the smaller extensions after
    checking the larger ones.
    -> moreFileExtensions: add more file extensions to consider without overriding all file extensions;
    -> moreRetryExtensions: add more extensions to consider while retrying without overriding the retryExtensions;
    -> ignoreNumbersAfterExtension: whether to ignore numbers after the file extensions or not.
    -> separator: a string to add as separator

  Output:
    -> the filename with the string appended.
  """
  knownFileExtensions.extend( moreFileExtensions )
  def repStr( lSep ):
    return r'\g<1>' + lSep + appendStr + r'.\g<2>' + r'\g<3>'
  str_ = __extRE(knownFileExtensions)
  m = str_.match(filename)
  if m:
    lSep = ''
    if not(m.group(1).endswith(separator) or appendStr.startswith(separator)):
      lSep = separator
    return str_.sub(repStr(lSep), filename)
  str_ = __extRE(retryExtensions)
  m = str_.match(filename)
  if m:
    lSep = ''
    if not(m.group(1).endswith(separator) or appendStr.startswith(separator)):
      lSep = separator
    return str_.sub(repStr(lSep), filename)
  else:
    return filename + ( separator if not(filename.endswith(separator) or appendStr.startswith(separator)) else '') + appendStr



def getMD5(filepath):
  """
  Get files md5 hash
  """
  import os.path
  import hashlib
  md5_returned = ''
  with open(os.path.expandvars(filepath),'rb') as file_to_check:
    # read contents of the file
    data = file_to_check.read()
    # pipe contents of the file through
    md5_returned = hashlib.md5(data).hexdigest()
  return md5_returned



def checkFile(filepath, md5sum = None):
  """
  Checks if file exists and if md5sum matches
  """
  import os.path
  filepath = os.path.expandvars(filepath)
  return os.path.isfile(filepath) and \
         (
           md5sum is None or
           getMD5(filepath) == md5sum
         )


from Gaugi import EnumStringification
class WriteMethod( EnumStringification ):
  """
    Specificate how to write files on cat_files_py
  """
  _ignoreCase = True
  Readlines = 0
  Read = 1
  ShUtil = 2


#@timed
def cat_files_py(flist, ofile, op, logger = None, level = None):
  """
    cat files using python.

    taken from: https://gist.github.com/dimo414/2993381
  """
  op = WriteMethod.retrieve( op )
  if not isinstance(flist, (list, tuple)):
    flist = [flist]
  from Gaugi.messenger import LoggingLevel
  if level is None: level = LoggingLevel.INFO
  with open(ofile, 'wb') as out:
    from Gaugi import progressbar
    for fname in progressbar(flist, len(flist), prefix="Merging: ",
                             disp = True if logger is not None else False, step = 10,
                             logger = logger, level = level ):
      with open(fname,'rb') as f:
        if op is WriteMethod.Readlines:
          out.writelines(f.readlines())
        elif op is WriteMethod.Read:
          out.write(f.read())
        elif op is WriteMethod.ShUtil:
          import shutil
          shutil.copyfileobj(f, out)
      # end of with open(fname)
    # end of for fname in progressbar
  # end of with open(ofile)



def findFile( filename, pathlist, access ):
  """
     Find <filename> with rights <access> through <pathlist>.
     Author: Wim Lavrijsen (WLavrijsen@lbl.gov)
     Copied from 'atlas/Control/AthenaCommon/python/Utils/unixtools.py'
  """
  # special case for those filenames that already contain a path
  if os.path.dirname( filename ):
    if os.access( filename, access ):
      return filename
  # test the file name in all possible paths until first found
  for path in pathlist:
    f = os.path.join( path, filename )
    if os.access( f, access ):
      return f
  # no such accessible file avalailable
  return None



def mkdir_p(path):
  import errno
  path = os.path.expandvars( path )
  try:
    if not os.path.exists( path ):
      os.makedirs(path)
  except OSError as exc: # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else: raise IOError



def getFiles(folder, ftype = os.path.isfile, fullpath = True):
  """
  As in expand folders, but without recursion
  """
  if fullpath:
    return [ os.path.join(folder,f) for f in sorted(os.listdir(folder)) if ftype( os.path.join(folder,f) ) ]
  else:
    return [ f for f in sorted(os.listdir(folder)) if ftype( os.path.join(folder,f) ) ]

