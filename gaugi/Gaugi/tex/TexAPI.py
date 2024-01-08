__all__ = [ 'escape_decode', 'TexException', 'TexSessionStream', 'PDFTexOutput'
          , 'TexObject', 'TexObjectCollection', 'Center', 'Table'
          , 'GenericTexCode', 'Figure', 'Tabular', 'TableLine', 'HLine', 'formatTex'
          , 'TexPackage', 'TexPackageCollection', 'assertProp'
          , 'TexPassOptionsToPackage', 'TexPassOptionsToPackageCollection'
          , 'tss', 'gco', 'gcc', '_', 'Columns', 'Column', 'IncludeGraphics'
          , 'Centering', 'escape_latex', 'OverPic', 'ResizeBox']
# TODO Create PhantomSection
from future.utils import with_metaclass


def _writeline(self, *l, **kw ):
  l = list(l)
  if not l: l = ['']
  if not l[0].endswith(os.linesep):
    l[0] += os.linesep
  self.write( *l, **kw )



try:
  from StringIO import StringIO ## for Python 2
  StringIO.writeline = _writeline
except ImportError:
  from io import StringIO ## for Python 3
  # Hack to StringIO since I can not include new attributes in python3
  class StringIOExt(StringIO):
    writeline = _writeline
  StringIO = StringIOExt

try:
  basestring
except NameError:
  basestring = str


import os, sys, traceback


from Gaugi.utilities import retrieve_kw,Holder
from Gaugi.storage import ensureExtension, changeExtension, checkExtension
from Gaugi.gtypes import NotSet
from Gaugi.messenger import Logger, LoggingLevel
from Gaugi.messenger.macros import *
from Gaugi.tex.LimitedTypeList import LimitedTypeList, _LimitedTypeList____init__


# If tex package is not available, we will have to add this utilities from it
# to be able to escape latex codes without having to handle ourselves each
# one of the cases below:
_latex_special_chars = { 
    u'$':  u'\\$', 
    u'%':  u'\\%', 
    u'&':  u'\\&', 
    u'#':  u'\\#', 
    u'_':  u'\\_', 
    u'{':  u'\\{', 
    u'}':  u'\\}', 
    u'[':  u'{[}', 
    u']':  u'{]}', 
    u'"':  u"{''}", 
    u'\\': u'\\textbackslash{}', 
    u'~':  u'\\textasciitilde{}', 
    u'<':  u'\\textless{}', 
    u'>':  u'\\textgreater{}', 
    u'^':  u'\\textasciicircum{}', 
    u'`':  u'{}`',   # avoid ?` and !` 
    u'\n': u'\\\\', 
} 
def escape_latex(s): 
    r'''Escape a unicode string for LaTeX. 
 
    :Warning: 
        The source string must not contain empty lines such as: 
            - u'\n...' -- empty first line 
            - u'...\n\n...' -- empty line in between 
            - u'...\n' -- empty last line 
 
    :Parameters: 
        - `s`: unicode object to escape for LaTeX 
 
    >>> s = u'\\"{}_&%a$b#\nc[]"~<>^`\\' 
    >>> escape_latex(s) 
    u"\\textbackslash{}{''}\\{\\}\\_\\&\\%a\\$b\\#\\\\c{[}{]}{''}\\textasciitilde{}\\textless{}\\textgreater{}\\textasciicircum{}{}`\\textbackslash{}" 
    >>> print s 
    \"{}_&%a$b# 
    c[]"~<>^`\ 
    >>> print escape_latex(s) 
    \textbackslash{}{''}\{\}\_\&\%a\$b\#\\c{[}{]}{''}\textasciitilde{}\textless{}\textgreater{}\textasciicircum{}{}`\textbackslash{} 

    Taken from http://pythonhosted.org/tex/tex-pysrc.html#escape_latex
    '''
    return u''.join(_latex_special_chars.get(c, c) for c in s)


def escape_decode( txt ):
  #return txt.decode('utf-8')
  return txt

def formatTex( text, width = 80, indent = '' ):
  """
  Strip initial and final '\n' if available and dedent text.
  """
  ntext = text.lstrip('\n ').rstrip('\n ')
  while ntext != text:
    text = ntext
    ntext = text.lstrip('\n ').rstrip('\n ')
  from textwrap import dedent, fill
  ntext = escape_decode( ntext )
  ntext = [l for l in ntext.split('\n') if l]
  if ntext and not ( ntext[0].startswith(' ') or ntext[0].startswith('\t') ):
    fstline = ntext[0]
    ntext = '\n'.join( [fstline, dedent( '\n'.join( ntext[1:] ) )] )
  else:
    ntext = dedent( '\n'.join( ntext ) )
  return escape_decode( ntext )

_ = formatTex

def assertProp( self, prop ):
  """
  Assert that object has property available, otherwise raise TexException.
  """
  if not hasattr( self, prop ): raise TexException( self
                                                  , 'Cannot create a TexObject without %s attribute.' % prop )

class TexException(Exception):
  """
    Exception thrown by specific errors during this module execution
  """

  def __init__( self, obj, message = None ):
    if not isinstance( obj, (TexObject, TexSessionStream) ):
      raise TypeError("Attempted to raise TexException with bad type %s" % type(obj) )
    self.obj = obj
    baseMsg = "Couldn't format %s tex code" % obj.__class__.__name__
    if message:
      self.message =  "%s due to: %s" % (baseMsg, message)
    else:
      self.message = baseMsg
    if not self.message.endswith('.'): self.message += '.'
    Exception.__init__( self, self.message )

# This singleton will be used to assign every TexObject to this 
# tex session file
tss = Holder( None, replaceable = True )

class TexSessionStream( Logger ):
  """
  Object used assign the tex output stream place as a raw tex code.
  """

  _outputExtension = '.tex'

  def __init__( self, outputFile ):
    Logger.__init__( self )
    if not outputFile:
      raise TexException( self, 'Cannot stream to empty file path.' )
    self.outputFile = ensureExtension( outputFile, self._outputExtension )

  def __enter__( self ):
    self.file = open( self.outputFile, 'w')
    # Assign current _texSession to ourself, the last created TexOutputStream object
    tss.set( self )
    return self

  def write(self, *l, **kw ):
    if not hasattr(self, 'file' ):
      raise TexException( self
                        , ( "%s is unavailable. Make sure to start it using with %s('outputFilePath')" 
                        % ( self.__class__.__name__, self.__class__.__name__ ) ) )
    if not l:
      raise TexException( self, 'Attempted to write empty string to file.' )
    self.file.write( *l, **kw )

  def writeline(self, *l, **kw ):
    """
    Write line to file
    """
    l = list(l)
    if not l: l = ['']
    if not l[0].endswith(os.linesep):
      l[0] += os.linesep
    self.write( *l, **kw )

  def __exit__(self, exc_type, exc_value, traceback):
    self.file.close()
    del self.__dict__['file']

class PDFTexOutput( TexSessionStream ):
  """
  As the TexOutputStream, but directly saves the file as pdf.
  """

  _outputExtension = 'pdf'

  def __init__( self, outputFile ):
    TexSessionStream.__init__( self, outputFile )


  def __enter__( self ):
    self.file = StringIO()
    # Assign current _texSession to ourself, the last created TexOutputStream object
    tss.set( self )
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    latexCode = self.file.getvalue()
    try:
      self.file.close()
      f = open(self.outputFile.replace('pdf','tex'),'w')
      with open( changeExtension( self.outputFile, 'tex'
                                  , knownFileExtensions = ['pdf']
                                  , retryExtensions = [] ), 'w' ) as f:
        f.write( str(latexCode) )
      os.system( 'pdflatex %s &> mylog.log'%( changeExtension(self.outputFile, 'tex', knownFileExtensions=['pdf']) ) )
      os.system( 'pdflatex %s &> mylog.log'%( changeExtension(self.outputFile, 'tex', knownFileExtensions=['pdf']) ) )
      for ext in ['aux','log','out','snm','toc','nav']:
        try:
          os.system('rm *.%s'% ext)
        except:
          pass
    except Exception as e:
      self._error( "PDFTexOutput will work as a standard TexSessionStream. Reason:\n%s", e)
      with open( changeExtension( self.outputFile, 'tex'
                                  , knownFileExtensions = ['pdf'] 
                                  , retryExtensions = [] ), 'w' ) as f:
        f.write( latexCode )



class TexCodeWriteException( TexException ):

  def __init__( self, obj, codename, code, keywords, e):
    TexException.__init__( self, obj,  "Couldn't process %s:\n%s\nKeywords are: %s\nError msg: %s" %
                ( codename, code, keywords, e ) )

class TexObject( Logger ):
  r"""
  TexObject inherited class will convert the object to a string containing the
  tex code by using the skeleton template and its configured attributes.

  Its output will go, by default, to tss stream, which is the last
  TexOutputStream object created. You can change this behavior by setting the
  stream property during the object initialization.

  The following template applies to every TexObject: 

  *_preamble*
  \begin{*_enclosure*} 
    *header* = _header % keywords
    *body* = _body % keywords
    *footer* = _footer % keywords
  \end{*_enclosure*}
  *_appendix*
  """

  class _TexObjectContextManager( with_metaclass(LimitedTypeList ,object) ):
    _acceptedTypes = None,

    def context( self ):
      if self:
        return self[-1]
      return None

    def __call__( self ):
      return self.context()

    def __repr__(self):
      return 'TexObjectContextManager[' + ','.join([repr(obj) for obj in self]) + ']'

  _contextManager = _TexObjectContextManager()

  def __init__( self, d = {}, **kw ):
    if None in self._contextManager._acceptedTypes:
      self._contextManager._acceptedTypes = TexObject,
    if ( not isinstance(self, TexObjectCollection) and
         not hasattr(self,'_preamble'  ) and
         not hasattr(self,'_enclosure' ) and
         not hasattr(self,'_body'      ) and
         not hasattr(self,'_footer'    ) and
         not hasattr(self,'_appendix'  )
       ):
      raise TexException(self, 'Class %s does not write any tex code.' % self.__class__.__name__)
    d.update( kw )
    Logger.__init__( self, d )
    if hasattr(self, '_body' ):
      self._body = formatTex( self._body, retrieve_kw( d, 'textWidth', 80 ) )
    self._stream = kw.pop( 'stream', tss )
    self._keywords = { key :  val for key, val in d.items() if not key.startswith('_') }
    self._keywords.update( { key :  val for key, val in self.__dict__.items() if not key.startswith('_') } )
    if 'star' in self._keywords and self._keywords['star']:
      self._keywords['star'] = '*'
    else:
      self._keywords['star'] = ''
    if hasattr(self, '_assertVars' ):
      for key in self._assertVars:
        if not key in self._keywords:
          raise TexException(self, "Assert var %s failed." % key )
    gcc.set( self )
    self._contextManaged = d.pop('_contextManaged', True)
    self._context = self._contextManager()
    self._isInContext = self._context is not None
    if ( self._isInContext and 
         isinstance( self._context, TexObjectCollection ) and 
         self._contextManaged ):
      self._context += self
    if self._isInContext:
      self._stream = self._context._stream

  def texCode( self ):
    ret = '<%s:ERROR>' % self.__class__.__name__
    s = StringIO()
    self._write( s )
    ret = s.getvalue()
    s.close()
    return ret

  def __call__( self ):
    return self.texCode()

  def __str__( self ):
    """
    Needed to correctly parse options via dictionaries. 
    """
    return self.texCode()

  def _write( self, stream, upperBody = True, lowerBody = True ):
    """
    Write object tex code to stream
    """
    if upperBody:
      if hasattr(self, '_preamble') and self._preamble:
        try:
          line = _( self._preamble % self._keywords )
          #self._verbose( 'Adding preamble:\n%s', line )
          stream.writeline( line )
        except Exception as e:
          traceback.print_tb(sys.exc_info()[2])
          raise TexCodeWriteException( self, 'preamble', self._preamble, self._keywords, e )
      if hasattr(self, '_enclosure') and self._enclosure:
        try:
          line = _( r'\begin{%s}' % self._enclosure )
          #self._verbose( 'Adding opening enclosure:\n%s', line )
          stream.writeline( line )
        except Exception as e:
          traceback.print_tb(sys.exc_info()[2])
          raise TexCodeWriteException( self, 'opening enclosure\n', self._enclosure, self._keywords, e )
      if hasattr(self, '_header' ) and self._header:
        try:
          line = _( self._header % self._keywords )
          #self._verbose( 'Adding header:\n%s ', line )
          stream.writeline( line  )
        except Exception as e:
          traceback.print_tb(sys.exc_info()[2])
          raise TexCodeWriteException( self, 'header', self._header, self._keywords, e )
      try:
        if hasattr(self, '_body') and self._body:
          line = _( self._body % self._keywords )
          #self._verbose( 'Adding body:\n%s ', line )
          stream.writeline( line )
      except Exception as e:
        traceback.print_tb(sys.exc_info()[2])
        raise TexCodeWriteException( self, 'body', self._body, self._keywords, e )
    if lowerBody:
      if hasattr(self, '_footer' ) and self._footer:
        try:
          line = _( self._footer % self._keywords )
          #self._verbose( 'Adding footer:\n%s ', line )
          stream.writeline( line )
        except Exception as e:
          traceback.print_tb(sys.exc_info()[2])
          raise TexCodeWriteException( self, 'footer', self._footer, self._keywords, e )
      if hasattr(self, '_enclosure') and self._enclosure:
        try:
          line = _( r'\end{%s}' % self._enclosure )
          #self._verbose( 'Adding closing enclosure:\n%s', line )
          stream.writeline( line )
        except Exception as e:
          traceback.print_tb(sys.exc_info()[2])
          raise TexCodeWriteException( self, 'enclosure', self._enclosure, self._keywords, e )
      if hasattr(self, '_appendix' ) and self._appendix:
        try:
          line = _( self._appendix % self._keywords )
          #self._verbose( 'Adding appendix:\n%s ', line )
          stream.writeline( line )
        except Exception as e:
          traceback.print_tb(sys.exc_info()[2])
          raise TexCodeWriteException( self, 'appendix', self._appendix, self._keywords, e )

  def __enter__( self ):
    """
    This should be called first when overriding the __enter__ method.
    """
    self._contextManager += self
    if not self._isInContext:
      if not self._stream.isValid():
        raise TexException( self, 'Not valid stream.' )
      self._write(self._stream(), upperBody = True, lowerBody = False )
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    """
    This should be called last when overriding the __exit__ method.
    """
    if not self._isInContext:
      self._write(self._stream(), upperBody = False, lowerBody = True)
      if self._logger.isEnabledFor( LoggingLevel.DEBUG ):
        self._debug('Adding Tex code:\n%s', str(self) )
    self._contextManager.pop()

  def __repr__(self):
    return self.__class__.__name__

# This singleton can be used to Get Current Texobject
gco = Holder( None, replaceable = True )

class TexObjectCollection( with_metaclass(LimitedTypeList, TexObject) ):
  r"""
  Base class for tex collections.

  The following template applies to every TexObjectCollection

  *_preamble*
  \begin{*_enclosure*} 
    *header* = _header % keywords
    *body* = _body % keywords
    *self[0] tex code*
    *self[1] tex code*
    ...
    *self[-1] tex code*
    *footer* = _footer % keywords
  \end{*_enclosure*}
  *_appendix*
  """
  _acceptedTypes = type(None), # This will be filled after TexItemCollection is defined

  def __init__( self, *args, **kw ):
    _LimitedTypeList____init__(self, *args)
    TexObject.__init__( self, kw )
    self._TexObject_addAppendix = False
    gco.set( self )

  def _write( self, stream, upperBody = True, lowerBody = True ):
    if upperBody:
      TexObject._write( self, stream, True, False )
    if lowerBody:
      for obj in self:
        try:
          stream.write( str( obj ) )
        except TexException as e:
          self._warning( "Ignoring badly formed object of type %s. Reason:\n%s"
                       , self.__class__.__name__, e )
      TexObject._write( self, stream, False, True )

  def __repr__(self):
    return self.__class__.__name__ + '[' + ','.join([repr(obj) for obj in self]) + ']'

class GenericTexCode( TexObject ):
  """
  Write direct tex code to file
  """
  _body = r"%(code)s"

  def __init__( self, code, **kw ):
    self.code = code
    TexObject.__init__( self, **kw )

TexObjectCollection._acceptedTypes = basestring, TexObject, TexObjectCollection

# This singleton can be used to Get Current texobjectCollection
gcc = Holder( None , replaceable = True )

class Center( TexObjectCollection ):
  _enclosure = 'center'
  def __init__( self, *args, **kw ):
    TexObjectCollection.__init__( self, *args, **kw )

class Columns( TexObjectCollection ):
  _enclosure = 'columns'
  _header = '%(config)s'

  def __init__( self, config = None, *args, **kw ):
    self.config = ''
    if config:
      self.config += '['
      self.config += config
      self.config += ']'
    TexObjectCollection.__init__( self, *args, **kw )

class Column( GenericTexCode ):
  def __init__( self, width, *args, **kw ):
    self.code = '\column{' + ( str(width) + r"\textwidth" if isinstance(width, (int, float) ) else width ) + '}'
    GenericTexCode.__init__( self, self.code, *args, **kw )

class Centering( TexObject ):
  _body = r'\centering'

class RaiseBox( TexObjectCollection ):
  """
  Create a raisebox by adding each held object code to be delocated by the raisebox configuration
  """

  _body = r'\raisebox{%(lift)s}[%(height)s][%(depth)s]{%(code)s}'

  def __init__( self, code, lift = r'0pt', height = r'0pt', depth = r'0pt', **kw):
    self.lift = lift
    self.height = height
    self.depth = depth
    TexObjectCollection.__init__( self, **kw )

  def _write( self, stream, upperBody = True, lowerBody = True ):
    if upperBody:
      self.code = ''
      for obj in self:
        try:
          self.code += str( obj )
        except TexException as e:
          self._warning( "Ignoring badly formed object of type %s. Reason:\n%s"
                       , self.__class__.__name__, e )
      TexObject._write( self, stream, True, False )
    if lowerBody:
      TexObject._write( self, stream, False, True )


class ResizeBox( TexObjectCollection ):
  _header = r"\resizebox{%(size)s}{%(option)s}{%%"
  _footer = r"}"

  def __init__( self, size=1., option='!',  *args, **kw ):
    if isinstance(size,(int,float)):
      self.size = r'%f\textwidth' % size
    elif isinstance(size,(basestring)):
      self.size = size
    else:
      TexObjectCollection.__init__( self, *args, **kw )
      self._fatal("Cannot handle size: %r", size, TypeError) 
    self.option = option
    TexObjectCollection.__init__( self, *args, **kw )
  
class OverPic( TexObject ):
  _enclosure = r'overpic'
  _header = r'[%(graphics_option)s]'
  _body = r'{%(path)s}'
  _footer = r'%(texts)s'

  def __init__( self, path, texts
              , width = None, height = None, keepaspectratio = None
              , moreGraphicsOptions = {}, *args, **kw ):
    path = os.path.abspath( os.path.expandvars( os.path.expanduser( path ) ) )
    if not os.path.isfile( path ):
      raise TexException( self, 'Figure not available at path %s' % path )
    if not checkExtension( path, 'eps|pdf|png' ):
      raise TexException( self, 'Not valid figure extension for file: %s' % path )
    self.path = path
    graphics_option = {}
    if width == height == None:
      width = 1.
    if width:
      graphics_option['width'] = str(width) + r"\textwidth" if isinstance(width, (int, float) ) else width
    if height:
      graphics_option['height'] = str(height) + r"\textheight" if isinstance(height, (int, float) ) else height
    graphics_option = ','.join( [str(key) + '=' + str(val) for key, val in graphics_option.iteitems() ] )
    if keepaspectratio:
      if graphics_option: self.graphics_option += ','
      graphics_option += 'keepaspectratio'
    graphics_option += ',' if moreGraphicsOptions else ''
    graphics_option += ','.join( [str(key) + ('=' + str(val) if val else '') for key, val in moreGraphicsOptions.items() ] )
    self.graphics_option = graphics_option
    from Gaugi.utilities import traverse
    try:
      _, _, _, _, depth = traverse(texts ).next()
    except (GeneratorExit, StopIteration):
      depth = 0
    if depth == 0:
      if isinstance(texts, basestring):
        texts = [ [0, 90, texts] ]
      else:
        texts = [ [ None ] ]
    elif depth == 1:
      texts = [ texts ]
    elif depth > 2:
      raise TexException( self, "Too many depth in text object" )
    self.texts = '\n'.join([r"\put (%f,%f) {%s}" % text for text in texts if text and not None in text])
    TexObject.__init__( self, *args, **kw )

class IncludeGraphics( TexObject ):
  _body = r'\includegraphics[%(graphics_option)s]{%(path)s}'
  def __init__( self, path, width = None, height = None, keepaspectratio = None, *args, **kw ):
    path = os.path.abspath( os.path.expandvars( os.path.expanduser( path ) ) )
    if not os.path.isfile( path ):
      raise TexException( self, 'Figure not available at path %s' % path )
    if not checkExtension( path, 'eps|pdf|png' ):
      raise TexException( self, 'Not valid figure extension for file: %s' % path )
    self.path = path
    graphics_option = {}
    if width == height == None:
      width = 1.
    if width:
      graphics_option['width'] = str(width) + r"\textwidth" if isinstance(width, (int, float) ) else width
    if height:
      graphics_option['height'] = str(height) + r"\textheight" if isinstance(height, (int, float) ) else height
    graphics_option = ','.join( [str(key) + '=' + str(val) for key, val in graphics_option.items() ] )
    if keepaspectratio:
      if graphics_option: self.graphics_option += ','
      graphics_option += 'keepaspectratio'
    self.graphics_option = graphics_option
    TexObject.__init__( self, *args, **kw )


class Figure( TexObject ):
  """
  Create figure tex code
  """
  _header = r'%(config)s'
  _enclosure = 'figure'
  _body = r''
  _footer = r'\caption{%(caption)s}'

  def __init__( self, path
              , config = [], caption = ''
              , width = None, height = None, keepaspectratio = None,
              **kw ):
    self.caption = caption
    self.config = ''
    if config:
      self.config += '['
      self.config += config
      self.config += ']'
    if width == height == None:
      width = .8
    self._body += str( IncludeGraphics( path, width, height, keepaspectratio, _contextManaged = False ) )
    TexObject.__init__( self
                      , width = width
                      , path = path
                      , **kw )

class Table( TexObjectCollection ):
  _enclosure = 'table'
  _header = r'\scriptsize' # FIXME scriptsize?
  _footer = r'%(caption)s'
  def __init__(self, **kw):
    if 'caption' in kw:
      caption = kw['caption']
      if not caption.startswith(r'\caption{'): caption = r'\caption{' + caption
      if not caption.endswith(r'}'): caption += '}'
      kw['caption'] = caption
    TexObjectCollection.__init__( self,  **kw )

class TableLine( TexObject ):
  _body = r'%(line)s \\'
  def __init__( self, columns, rounding = None, d = {}, **kw ):
    d.update(kw)
    if isinstance(rounding, basestring):
      def roundingMethod(v):
        if isinstance(v, basestring):
          return v
        else:
          return rounding % v
    elif hasattr(rounding, '__call__'):
      roundingMethod = rounding
    elif rounding is None:
      roundingMethod = lambda v: str(v)
    else:
      TexObject.__init__(self, d)
      self._error("Could not parse rounding method", ValueError)
    self.line = ' & '.join([(roundingMethod(v) if v is not None else ' ') for v in columns])
    TexObject.__init__(self, d)

class HLine( TableLine ):
  _body = r'\hline'
  def __init__( self, d = {}, **kw ):
    d.update(kw)
    TexObject.__init__(self, d)

class Tabular( TexObjectCollection ):
  """
  Create tabular tex code
  """
  _enclosure = "tabular"
  _header = _( r"%(columns)s" )
 # _assertVars = ('columns', 'title', 'body','tabular_header' )

  def __init__(self, columns='', **kw):
    if not columns.startswith('{'): columns = '{' + columns
    if not columns.endswith('}'): columns += '}'
    self.columns = columns
    TexObjectCollection.__init__( self,  **kw )

class TexPackage( TexObject ):
  """
    Defines a tex package to be included
  """
  _body = r"\usepackage%(config)s{%(package)s}"

  def __init__(self, package,  *args, **kw):
    self.package = package
    self.help = kw.pop( 'help', '' )
    self.help = ' %% ' + self.help if not self.help.startswith('%%') else self.help
    self.config = ''
    if args or kw:
      self.config += '['
      self.config += ','.join( args ) 
      self.config += ',' if kw and args else ''
      self.config += ','.join( [str(key) + '=' + str(val) for key, val in kw.items() ] )
      self.config += ']'
    TexObject.__init__(self)

class TexPackageCollection( TexObjectCollection ):
  _acceptedTypes = TexPackage,
  _preamble = """%%----------------------PACKAGES-|-SEGAKCAP---------------------"""
  _appendix = """%%---------------END-OF-PACKAGES-|-SEGAKCAP-FO-DNE--------------"""

  def __init__( self,  *args, **kw ):
    TexObjectCollection.__init__( self, *args, **kw )

class TexPassOptionsToPackage( TexObject ):
  """
    Defines a tex package to be included
  """
  _body = r"\PassOptionsToPackage{%(options)s}{%(package)s}"

  def __init__(self, package,  *args, **kw):
    self.package = package
    self.help = kw.pop( 'help', '' )
    self.help = ' %% ' + self.help if not self.help.startswith('%%') else self.help
    self.options = ''
    if args or kw:
      self.options += ','.join( args ) 
      self.options += ',' if kw and args else ''
      self.options += ','.join( [str(key) + '=' + str(val) for key, val in kw.items() ] )
    else:
      raise TexException( self, 'Attempted to create TexPassOptionsToPackage without options.' )
    TexObject.__init__(self)

class TexPassOptionsToPackageCollection( TexObjectCollection ):
  _acceptedTypes = TexPassOptionsToPackage,
  _preamble = """%% Package options:"""

  def __init__( self,  *args, **kw ):
    TexObjectCollection.__init__( self, *args, **kw )

#class TexEnum( TexObjectCollection ):
#  """
#  Tex enumeration object 
#  """
#
#  def __init__( self ):
#    self.skeleton = kw.pop( 'skeleton',  )
#
#  def addItem( self, item ):
#    self.items.append( item )
