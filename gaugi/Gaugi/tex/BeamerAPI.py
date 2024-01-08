__all__ = [ 'BeamerSlide', 'BeamerTexReport'
          , 'BeamerFigureSlide', 'BeamerMultiFigureSlide', 'BeamerTableSlide'
          , 'BeamerSection', 'BeamerSubSection', 'BeamerSubSubSection'
          , 'BeamerPhantomSection', 'BeamerPhantomSubSection', 'BeamerPhantomSubSubSection'
          , 'TexBeamerTemplate', 'TexBeamerTemplateCollection'
          , 'BeamerOutlineSlide', 'outlineSession', 'BeamerTexReportTemplate1'
          , 'BeamerTexReportTemplate2','gcb']

try:
    basestring
except NameError:
    basestring = str

import os
from Gaugi.utilities import checkForUnusedVars, Holder, retrieve_kw 
from Gaugi.gtypes import NotSet
from Gaugi.messenger import Logger, LoggingLevel
from Gaugi.tex.TexAPI import *

class PDFTexLayout( TexPackage ):
  _preamble = _( r"""
                     %% On Overleaf, these lines give you sharper preview images.
                     %% You might want to comment them out before you export, though.
                  """
               )
  _footer = r"""\pgfpagesuselayout{resize to}[physical paper width=8in, physical paper height=6in]"""
  def __init__(self, *args, **kw):
    TexPackage.__init__(self, 'pgfpages', *args, **kw)

class BeamerObject( TexObject ):
  """
  The most basic object to be created by the beamer submodule slide object
  """

  def __init__( self, **kw ):
    self._parent = kw.get('parent', _btr )


class BeamerSlide( TexObjectCollection ):
  """
  Beamer empty slide
  """
  _preamble = '%%--------------------------------------------------------------'
  _enclosure = 'frame'
  _header = r"\frametitle{%(title)s}"

  def __init__( self,  *args, **kw ):
    TexObjectCollection.__init__( self, *args, **kw )

  def __repr__(self):
    title = '<' + self._keywords.get( 'title', 'untitled' ) + '>'
    return self.__class__.__name__ + title + '[' + ','.join([repr(obj) for obj in self]) + ']'

class BeamerTitleSlide( BeamerSlide ):
  """
  The most basic object to be created by the beamer submodule slide object
  """
  _enclosure = None
  _header = None
  _body = r'\titlepage'
  def __init__( self,  *args, **kw ):
    BeamerSlide.__init__( self, *args, **kw )

  def __repr__(self):
    return self.__class__.__name__ + '[' + ','.join([repr(obj) for obj in self]) + ']'

class BeamerOutlineSlide( BeamerSlide ):
  """
  The most basic object to be created by the beamer submodule slide object
  """
  _enclosure = r'frame'
  _header = _( r"""
              [allowframebreaks]
              \frametitle{Outline}
                """ )
  #_header = None
  #_body = r'\begin{multicols}{2}\tableofcontents\end{multicols}'
  _body = r'\tableofcontents'


  def __init__( self,  *args, **kw ):
    BeamerSlide.__init__( self, *args, **kw )

  def __repr__(self):
    return self.__class__.__name__ + '[' + ','.join([repr(obj) for obj in self]) + ']'

class _BeamerSectionBase( TexObjectCollection ):
  """
  Base class for beamer sections
  """

  def __init__(self, *args, **kw):
    self.shortname = kw.get( 'shortname', '' )
    if self.shortname:
      self.shortname = '[' + selfself.shortname + ']'
    TexObjectCollection.__init__( self, *args, **kw )

  def __repr__(self):
    name = '<' + self._keywords.get( 'name', 'unnamed' ) + '>'
    return self.__class__.__name__ + name + '[' + ','.join([repr(obj) for obj in self]) + ']'

class BeamerSubSubSection( _BeamerSectionBase ):
  """
  Create a subsubsection that can handle slides
  """
  _preamble = """%%--------------------- --------- -------- ---------------------"""
  _header = r"\subsubsection%(star)s%(shortname)s{%(name)s}"
  _acceptedTypes = BeamerSlide,

class BeamerSubSection( _BeamerSectionBase ):
  """
  Create a subsection that can handle slides and subsubsections
  """
  _preamble = """%%--------------------- --------- -------- ---------------------
                 %%--------------------- --------- -------- ---------------------"""
  _header = r"\subsection%(star)s%(shortname)s{%(name)s}"
  _acceptedTypes = BeamerSlide, BeamerSubSubSection

class BeamerSection( _BeamerSectionBase ):
  """
  Create a subsection that can handle slides and subsections
  """
  _preamble = _( """
                 %%--------------------- --------- -------- ---------------------
                 %%--------------------- --------- -------- ---------------------
                 %%--------------------- --------- -------- ---------------------"""
               )
  _header = r"\section%(star)s%(shortname)s{%(name)s}"
  _acceptedTypes = BeamerSlide, _BeamerSectionBase

outlineSession = BeamerSection( BeamerOutlineSlide()
                              , name = "Outline"
                              , star = True
                              , _contextManaged = False )

class _BeamerPhantomSectionBase( _BeamerSectionBase ):
  """
  Base class for beamer phantom sections
  """
  _global_extra = _(
      r"""
      \makeatletter
      \newcommand{\phantomsectionfortoc}[1]{%%
        \global\advance\beamer@tocsectionnumber by 1%%
        \addtocontents{toc}{\protect\beamer@sectionintoc{0}{#1}{0}{0}%%
          {\the\beamer@tocsectionnumber}}}
      \makeatother
      \makeatletter
      \newcommand{\phantomsubsectionfortoc}[1]{%%
        \global\advance\beamer@tocsubsectionnumber by 1%%
        \addtocontents{toc}{\protect\beamer@subsectionintoc{0}{#1}{0}{0}%%
          {\the\beamer@tocsubsectionnumber}}}
      \makeatother
      \makeatletter
      \newcommand{\phantomsubsubsectionfortoc}[1]{%%
        \global\advance\beamer@tocsubsubsectionnumber by 1%%
        \addtocontents{toc}{\protect\beamer@subsubsectionintoc{0}{#1}{0}{0}%%
          {\the\beamer@tocsubsubsectionnumber}}}
      \makeatother
      """ )
#\newcommand{\phantomsubsectionfortoc}[1]{%
#  %\global\advance\beamer@tocsubsectionnumber by 1%
#  \addtocontents{toc}{\protect\beamer@subsectionintoc{0}{\inserttocsectionnumber}{#1}{0}{0}%
#  %{\the\beamer@tocsectionnumber}
#}}

class BeamerPhantomSubSubSection( _BeamerPhantomSectionBase ):
  """
  Create a subsubsection that can handle slides
  """
  _preamble = """%%--------------------- --------- -------- ---------------------"""
  _header = r"\phantomsubsubsectionfortoc{%(name)s}"
  _acceptedTypes = BeamerSlide,

class BeamerPhantomSubSection( _BeamerPhantomSectionBase ):
  """
  Create a subsection that can handle slides and subsubsections
  """
  _preamble = """%%--------------------- --------- -------- ---------------------
                 %%--------------------- --------- -------- ---------------------"""
  _header = r"\phantomsubsectionfortoc{%(name)s}"
  _acceptedTypes = BeamerSlide, BeamerPhantomSubSubSection

class BeamerPhantomSection( _BeamerPhantomSectionBase ):
  """
  Create a subsection that can handle slides and subsections
  """
  _preamble = _( """
                 %%--------------------- --------- -------- ---------------------
                 %%--------------------- --------- -------- ---------------------
                 %%--------------------- --------- -------- ---------------------"""
               )
  _header = r"\phantomsectionfortoc{%(name)s}"
  _acceptedTypes = BeamerSlide, _BeamerPhantomSectionBase

class BeamerFigureSlide( BeamerSlide ):
  """
  Beamer figure slide
  """
  def __init__(self, path,config = None ,**kw):
    BeamerSlide.__init__(self ,**kw)
    if not 'width' in kw and not 'height' in kw: kw['width'] = 0.7
    self += Center( Figure( path, _contextManaged = False, **kw ),
                    _contextManaged = False )

class BeamerMultiFigureSlide( BeamerSlide ):
  """
  Beamer multiple figures slide
  """

  def __init__(self, paths, nDivWidth, nDivHeight, texts = None
              , fortran = False, usedHeight = .80, usedWidth = 1.
              , fontsize = None, startAt = 0, delocateAll = 0
              , verticalDelocateAll = 0, verticalStartAt = 0
              , config = None, ignoreMissing = False, **kw):
    BeamerSlide.__init__(self, **kw)
    # Deal with text and paths arguments:
    if nDivWidth * nDivHeight < len(paths):
      raise TexException(self, "Not enought divisions (%d,%d) to retrieve all paths (%d)"
                        % (nDivHeight, nDivWidth, len(paths)))
    elif nDivWidth * nDivHeight != len(paths):
      paths += [None] * ( ( nDivWidth * nDivHeight ) - len(paths) )
    try:
      from Gaugi.utilities import traverse
      _, _, _, _, depth = next(traverse( texts ))
    except (GeneratorExit, StopIteration):
      depth = 0
    if depth == 0:
      if isinstance(texts, basestring):
        texts = [ ( (0, 90, texts), ), ]
      else:
        texts = [ ((),), ]
    elif depth == 1:
      texts = [ [ texts, ], ]
    elif depth == 2:
      texts = [ texts ]
    elif depth > 3:
      raise TexException( self, "Too many depth in text object" )
    if config == None:
      config = r'T,totalwidth=%f\textwidth' % usedWidth
    # Now we are sure that texts is a 3D object, add empty objets to the 1st dimension:
    texts += [None] * ( ( nDivWidth * nDivHeight) - len(texts) )
    paths = list(map(lambda path: path if (os.path.exists( os.path.expandvars( os.path.expanduser( path ) ) ) if isinstance(path, basestring) else False) else None, paths))
    # Now start slide figure objects creation:
    fWidth = usedWidth / nDivWidth
    fHeight = usedHeight / nDivHeight
    if fontsize:
      self += GenericTexCode( code = r'\fontsize{%f}{0}\selectfont' % fontsize, _contextManaged = False )
    def calcIdx( hIdx, wIdx ):
      return wIdx * nDivHeight + hIdx if fortran else hIdx * nDivWidth + wIdx
    with Columns( config = config, _contextManaged = False ) as columns:
      Column( 0 ) # We need to create a virtual column to fix OverPic not showing text in the first column
      for wIdx in range(nDivWidth):
        Column( fWidth )
        if not any([paths[i] for i in list(map(lambda hIdx: calcIdx( hIdx, wIdx ), range(nDivHeight)))]):
          GenericTexCode( code = r'\vspace{\textheight}' )
          continue
        for hIdx in range(nDivHeight):
          cIdx =  calcIdx(hIdx, wIdx)
          if not wIdx and startAt:
            # Add user requested start point
            GenericTexCode( code = r'\hspace*{%f\textwidth}' % startAt  )
          if delocateAll:
            # Delocate all images:
            GenericTexCode( code = r'\hspace*{%f\textwidth}' % delocateAll  )
          if not hIdx and verticalStartAt:
            # Delocate all images:
            GenericTexCode( code = r'\vspace*{%f\textheight}' % verticalStartAt  )
          if verticalDelocateAll:
            # Delocate all images:
            GenericTexCode( code = r'\vspace*{%f\textheight}' % verticalDelocateAll  )
          try:
            path = paths[cIdx]
            text = texts[cIdx]
          except IndexError as e:
            path = text = None
            self._warning("Not filling figure at index %d due to: %s", e )
          if path:
            try:
              if text and text != ((),):
                OverPic( path, texts = text, height = fHeight, **kw )
              else:
                IncludeGraphics( path, height = fHeight, **kw )
            except TexException as e:
              if not ignoreMissing:
                raise e
              else:
                GenericTexCode( code = r'\vspace{%f\textheight}' % fHeight )
            GenericTexCode( code = r'\\' )
          else:
            GenericTexCode( code = r'\vspace{%f\textheight}' % fHeight )
      self += columns
    if fontsize:
      self += GenericTexCode( code = r'\fontsize{11}{0}\selectfont', _contextManaged = False )

class BeamerTableSlide( BeamerSlide ):
  def __init__( self, lines=[], columns='', caption = '', table_width = 1.
              , sideline = '', rounding = None, config = None, **kw ):
    BeamerSlide.__init__( self , **kw )

    with Table( caption = caption, _contextManaged = False ) as table:
      self._table = table
      self += table
      with ResizeBox( size = table_width, _contextManaged = False) as rb:
        table += rb
        with Tabular( columns = columns
                    , _contextManaged = False
                    ) as tabular:
          rb += tabular
          self._tabular = tabular
          for line in lines:
            if isinstance(line, TableLine):
              self._tabular += line
            else:
              TableLine(line, rounding = rounding)
    # Make user directly modify tabular object
    #self._contextManager += self._tabular


class TexBeamerTemplate( TexObject ):
  """
    Defines a tex package to be included
  """
  _body = r"\setbeamertemplate{%(template)s}%(braces)s%(brackets)s"

  def __init__(self, template,  brackets = None, braces = None, **kw):
    self.template = template
    self.help = kw.pop( 'help', '' )
    self.help = ' %% ' + self.help if not self.help.startswith('%%') else self.help
    if not isinstance(brackets, (tuple, list)) and brackets is not None:
      brackets = (brackets,)
    if not isinstance(braces, (tuple, list)) and braces is not None:
      braces = (braces,)
    self.brackets = ''
    if brackets is not None:
      self.brackets += '['
      self.brackets += ','.join( brackets )
      self.brackets += ']'
    self.braces = ''
    if braces is not None:
      self.braces += '{'
      self.braces += ','.join( braces )
      self.braces += '}'
    TexObject.__init__(self)

class TexBeamerTemplateCollection( TexObjectCollection ):
  _acceptedTypes = TexBeamerTemplate,

  def __init__( self,  *args, **kw ):
    TexObjectCollection.__init__( self, *args, **kw )

class BeamerTexReport( TexObjectCollection ):
  """
  A BeamerTexReport object can be used to generate templated slides
  containing plots, tables etc.
  """
  _acceptedTypes = BeamerSlide, _BeamerSectionBase

  _preamble = _( r"""
                  %(passOptionsToPackages)s
                  \documentclass[table,svgnames,smaller,11pt]{beamer}
                  %(slidenumber)s
                  %% For more themes, color themes and font themes, see:
                  \mode<presentation>
                  {
                    \usetheme{%(theme)s}             %% or try default, Darmstadt, Warsaw, Boadilla ...
                    \usecolortheme{%(colortheme)s}   %% or try albatross, beaver, crane, ...
                    \usefonttheme{%(font)s}          %% or try default, structurebold, ...
                    %(beamertemplates)s
                  }
                  %(packages)s
                  \title{%(title)s}
                  \author{%(author)s}
                  \institute{%(institute)s}
                  \date{\today}
                  %(user_code)s
                  """
              )
  _enclosure = 'document'

  def __init__(self, *args, **kw):
    # FIXME Check if no title slide in args, else add it as first, same for agenda
    if not args:
      args = BeamerTitleSlide( _contextManaged = False), outlineSession
    import getpass, socket
    # Pre-ample default configuration
    self.theme      = retrieve_kw( kw, 'theme',      'Berlin'         ) # Boadilla, Singapore, Madrid
    self.colortheme = retrieve_kw( kw, 'colortheme', 'default'        )
    self.font       = retrieve_kw( kw, 'font',       'serif'          )
    self.title      = escape_latex( retrieve_kw( kw, 'title',      'Report'         ) )
    self.institute  = retrieve_kw( kw, 'institute',  os.environ.get( 'BEAMER_API_INSTITUTE', 'ATLAS Internal' ) )
    self.author     = retrieve_kw( kw, 'author',  os.environ.get( 'BEAMER_API_AUTHOR', getpass.getuser()
                                                                                       + '@'
                                                                                       + socket.gethostname()
                                                                )
                                 )
    self.passOptionsToPackages  = TexPassOptionsToPackageCollection(
                                    retrieve_kw( kw, 'passOptionsToPackage', [
                                                                     #TexPassOptionsToPackage( 'beamerouterthememiniframes', "subsection=false")
                                                                     TexPassOptionsToPackage( 'xcolor', 'table', 'xcdraw', 'x11names' )
                                                                             ]
                                               )
                                                                  )
    self.beamertemplates  = TexBeamerTemplateCollection(
                                    retrieve_kw( kw, 'beamertemplates', [# TexBeamerTemplate( 'navigation symbols', braces = '' )
                                                                          TexBeamerTemplate( 'caption', brackets = 'numbered' )
                                                                        ]
                                               )
                                                                  )
    self.packages  = TexPackageCollection(
                        retrieve_kw( kw, 'packages', [ TexPackage( 'babel', 'english' )
                                                     , TexPackage( 'inputenc', 'utf8x' )
                                                     , TexPackage( 'multicol' )
                                                     , TexPackage( 'multirow' )
                                                     , TexPackage( 'chemfig' )
                                                     , TexPackage( 'etoolbox' )
                                                     , TexPackage( 'moresize' )
                                                     , TexPackage( 'overpic', 'percent', help = r'Display images and text together' )
                                                     , TexPackage( 'mhchem', version = 3 )
                                                     , TexPackage( 'graphicx', help = r'Allows including images' )
                                                     , TexPackage( 'booktabs', help = r'Allows the use of \toprule, \midrule and \bottomrule in tables' )
                                                     #, TexPackage( 'moresize' ) # \usepackage[11pt]{moresize}
                                                     , TexPackage( 'anyfontsize' )
                                                     #, TexPackage( 'helvet', help = r'Needed to simulate root font (use \fontfamily{phv}\selectfont)' )
                                                     #, TexPackage( 'colorbl' )
                                                     #, PDFTexLayout()
                                                     ]
                                   )
                    )
    self.user_code = retrieve_kw( kw, 'user_code', '' )
    slidenumber = ''
    if self.theme in ('Berlin'):
      slidenumber = _( r'''
                        %% Add slide numbers
                        \newcommand*\oldmacro{}%%
                        \let\oldmacro\insertshorttitle%%
                        \renewcommand*\insertshorttitle{%%
                           \oldmacro\hfill%%
                           \insertframenumber\,/\,\inserttotalframenumber}
                        '''
                     )
    kw['slidenumber'] = slidenumber
    self._toPDF       = kw.pop( '_toPDF', None )
    # Behavior:
    self._ignoreErrors = retrieve_kw( kw, 'ignoreErrors', True )
    TexObjectCollection.__init__(self, *args, **kw)
    if self._stream() is None or self._toPDF is not None:
      changeStream = True
      if self._toPDF is not None:
        Output_class = PDFTexOutput if self._toPDF else TexSessionStream
        if not self._stream() is None and not isinstance( self._stream(), Output_class ):
          changeStream = True
          self._warning("Forcing output to be created by %s despite this class is in the context of %s."
                       , Output_class, self._stream().__class__ )
      else:
        self._toPDF = True
        Output_class = PDFTexLayout
      if changeStream:
        self._stream = Holder( Output_class( retrieve_kw( kw, 'outputFile', 'beamer' ) ) )
      # Make our childs to use our stream
      for obj in self:
        if obj._stream() is None:
          obj._stream = self._stream
    kw.pop('slidenumber')
    checkForUnusedVars( kw, self._logger.warning )
    gcb.set( self )

  def addPackage(self, packages):
    """
    Append tex package(s) to the BeamerTexReport
    """
    self.packages += packages

  def __enter__( self ):
    self._info( "Started creating beamer file %s latex code...", self._stream().outputFile )
    self._contextManager += self
    # FIXME The objects are not being added as we would prefer them to be. They
    # are currently being added at each other and BeamerTemplate do not
    # contains sections in it, but rather hold each other..
    #if any([isinstance(obj, _BeamerPhantomSectionBase) for obj in self]):
    self._preamble += _(_BeamerPhantomSectionBase._global_extra)
    if not hasattr(self._stream(), 'file'):
      self._stream().__enter__()
      setattr(self._stream(), '_setVia_BeamerTexReport', True)
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    if exc_type:
      import traceback as tb
      self._error("Traceback:\n%s\nError occurred: %s", ''.join(tb.format_tb(traceback)), exc_value if exc_value else exc_type)
    self._write( self._stream() )
    if self._logger.isEnabledFor( LoggingLevel.DEBUG ):
      self._debug('Beamer Tex code is:\n%s', str(self) )
    if hasattr(self._stream(), '_setVia_BeamerTexReport'):
      self._stream().__exit__( exc_type, exc_value, traceback )
    self._contextManager.pop()

# This singleton will be used to assign every TexObject to this
# tex session file
gcb = Holder( None, replaceable = True )


class BeamerTexReportTemplate1( BeamerTexReport ):
  _preamble = _( r"""
                  %(passOptionsToPackages)s
                  \documentclass[table,svgnames,smaller,11pt]{beamer}
                  %(slidenumber)s
                  %% For more themes, color themes and font themes, see:
                  \mode<presentation>
                  {
                    \usetheme{%(theme)s}             %% or try default, Darmstadt, Warsaw, Boadilla ...
                    \usecolortheme{%(colortheme)s}   %% or try albatross, beaver, crane, ...
                    \usefonttheme{%(font)s}          %% or try default, structurebold, ...
                    %%\usefonttheme{professionalfonts} %% or try default, structurebold, ...
                    %%\usefonttheme{serif}             %% or try default, structurebold, ...
                    %%\setmainfont{Helvetica}
                    %(beamertemplates)s
                  }
                  %(packages)s
                  \title{%(title)s}
                  \author{%(author)s}
                  \institute{%(institute)s}
                  \date{\today}
                  \setbeamerfont{frametitle}{size=\small}
                  \useinnertheme{rounded}
                  \useoutertheme{smoothtree}
                  \setbeamertemplate{headline}
                  {%%
                    \pgfuseshading{beamer@treeshade}%%
                    \vskip-10.25ex%%
                    \begin{beamercolorbox}[wd=\paperwidth,ht=2.125ex,dp=1.125ex,ignorebg,%%
                      leftskip=.3cm,rightskip=.3cm plus1fil]{section in head/foot}
                      \usebeamerfont{section in head/foot}%%
                      \insertsectionhead
                    \end{beamercolorbox}
                    \begin{beamercolorbox}[wd=\paperwidth,ht=2.125ex,dp=1.125ex,ignorebg,%%
                        leftskip=.3cm,rightskip=.3cm plus1fil]{subsection in head/foot}
                      \usebeamerfont{subsection in head/foot}%%
                      \hskip6pt\insertsubsectionhead
                    \end{beamercolorbox}
                    \begin{beamercolorbox}[wd=\paperwidth,ht=2.125ex,dp=1.125ex,ignorebg,%%
                        leftskip=.3cm,rightskip=.3cm plus1fil]{subsubsection in head/foot}
                      \usebeamerfont{subsection in head/foot}%%
                      \hskip12pt\insertsubsubsectionhead
                    \end{beamercolorbox}
                  }
                  \defbeamertemplate{subsubsection in toc}{subsubsections numbered}
                  {\leavevmode\leftskip=3em%%
                   \rlap{\hskip-3em\inserttocsectionnumber.\inserttocsubsectionnumber.\inserttocsubsubsectionnumber}%%
                   \inserttocsubsubsection\par}
                  \setbeamertemplate{section in toc}[sections numbered]
                  \setbeamertemplate{subsection in toc}[subsections numbered]
                  \setbeamertemplate{subsubsection in toc}[subsubsections numbered]
                  \AtBeginSection[]{
                    \frame<beamer>{\begin{multicols}{4}
                    \frametitle{Outline}
                    \tableofcontents[
                      sectionstyle=show/shaded,
                      subsectionstyle=show/shaded/hide,
                      subsubsectionstyle=show/hide/hide/hide,
                      ]
                    \end{multicols}
                   }
                  }
                  \AtBeginSubsection[]{
                    \frame<beamer>{\begin{multicols}{4}
                    \frametitle{Outline}
                    \tableofcontents[
                      sectionstyle=show/shaded,
                      subsectionstyle=show/shaded/hide,
                      subsubsectionstyle=show/shaded/hide/hide
                      ]
                    \end{multicols}
                   }
                  }
                  \AtBeginSubsubsection[]{
                    \frame<beamer>{\begin{multicols}{4}
                    \frametitle{Outline}
                    \tableofcontents[
                      sectionstyle=show/shaded,
                      subsectionstyle=show/shaded/hide,
                      subsubsectionstyle=show/shaded/hide/hide
                      ]
                    \end{multicols}
                   }
                  }
                  %(user_code)s
                  """
               )

class BeamerTexReportTemplate2( BeamerTexReport ):
  _preamble = _( r"""
                  %(passOptionsToPackages)s
                  \documentclass[table,svgnames,smaller,11pt]{beamer}
                  %(slidenumber)s
                  %% For more themes, color themes and font themes, see:
                  \mode<presentation>
                  {
                    \usetheme{%(theme)s}             %% or try default, Darmstadt, Warsaw, Boadilla ...
                    \usecolortheme{%(colortheme)s}   %% or try albatross, beaver, crane, ...
                    \usefonttheme{%(font)s}          %% or try default, structurebold, ...
                    %%\usefonttheme{professionalfonts} %% or try default, structurebold, ...
                    %%\usefonttheme{serif}             %% or try default, structurebold, ...
                    %%\setmainfont{Helvetica}
                    %(beamertemplates)s
                  }
                  %(packages)s
                  \title{%(title)s}
                  \author{%(author)s}
                  \institute{%(institute)s}
                  \date{\today}
                  \setbeamerfont{frametitle}{size=\small}
                  \useinnertheme{rounded}
                  \useoutertheme{smoothtree}
                  \setbeamertemplate{headline}
                  {%%
                    \pgfuseshading{beamer@treeshade}%%
                    \vskip-10.25ex%%
                    \begin{beamercolorbox}[wd=\paperwidth,ht=2.125ex,dp=1.125ex,ignorebg,%%
                      leftskip=.3cm,rightskip=.3cm plus1fil]{section in head/foot}
                      \usebeamerfont{section in head/foot}%%
                      \insertsectionhead
                    \end{beamercolorbox}
                    \begin{beamercolorbox}[wd=\paperwidth,ht=2.125ex,dp=1.125ex,ignorebg,%%
                        leftskip=.3cm,rightskip=.3cm plus1fil]{subsection in head/foot}
                      \usebeamerfont{subsection in head/foot}%%
                      \hskip6pt\insertsubsectionhead
                    \end{beamercolorbox}
                    \begin{beamercolorbox}[wd=\paperwidth,ht=2.125ex,dp=1.125ex,ignorebg,%%
                        leftskip=.3cm,rightskip=.3cm plus1fil]{subsubsection in head/foot}
                      \usebeamerfont{subsection in head/foot}%%
                      \hskip12pt\insertsubsubsectionhead
                    \end{beamercolorbox}
                  }
                  """
               )

