__all__=[]

def SetBoxes(pad, hists):
  #pad.Update();
  x_begin = 1.
  x_size = .18
  x_dist = .03;
  histStatsList=[]
  from ROOT import TPaveStats
  for hist in hists:
    histStats = hist.GetListOfFunctions().FindObject("stats")
    histStats.__class__=TPaveStats
    histStats.SetX1NDC(x_begin-x_dist); histStats.SetX2NDC(x_begin-x_size-x_dist);
    histStats.SetTextColor(hist.GetLineColor())
    histStatsList.append(histStats)
    x_begin-=x_dist+x_size;
  return histStatsList


def GetLine(x1,y1,x2,y2,color,style,width, text=''):
  from ROOT import TLine
  l = TLine(x1,y1,x2,y2)
  l.SetNDC(False)
  l.SetLineColor(color)
  l.SetLineWidth(width)
  l.SetLineStyle(style)
  return l


def getColors(outColors, transparency=None):
  from ROOT import TColor
  return [getColor(color, transparency) for color in zip(*outColors)]


def getColor(color, transparency = None):
	from ROOT import TColor
	try:
	  color = TColor.GetColor( *color )
	except:
	  if type(color) is not int: color = TColor.GetColor( color )
	if transparency is not None:
	  color = TColor.GetColorTransparent( color, transparency )
	return color

def colorGradient(color1, color2, nSteps, smoothThres=None, transparency=None):
  import numpy as np
  color1 = np.array(color1)
  color2 = np.array(color2)
  deltas = color2 - color1
  deltaSum = sum(abs(deltas))
  if smoothThres is not None and deltaSum/nSteps>smoothThres:
    color2 = color1 + deltas*smoothThres*nSteps/deltaSum
  outColors = [np.linspace(pcolor1,pcolor2,nSteps) for pcolor1, pcolor2 in zip(color1,color2)]
  outColors = getColors(outColors, transparency)
  return outColors


def sumHists(histList):
  totalHist = None
  for hist in histList:
    if not hist:
      continue
    if not totalHist:
      totalHist=hist.Clone()
    else:
      totalHist.Add( hist )
  return totalHist


def NormHist(hist, norm=None, removeZeros=0):

  from ROOT import TH1F
  if not norm:  norm = 1./sum(hist)
  h = TH1F(hist.GetName()+"_normalized", hist.GetTitle(), hist.GetNbinsX(), hist.GetBinLowEdge(0),
           hist.GetBinLowEdge( hist.GetNbinsX() + 2 ) )

  for bin in range(0,h.GetNbinsX()+1):
    content = hist.GetBinContent(bin)
    if not content and removeZeros:  content=removeZeros
    value = content*norm if norm else content
    h.SetBinContent(bin , value )

  return h



def ShiftHistogram( hist, shift ):
  h = hist.Clone()
  h.Reset('M')
  for bin in range(1, hist.GetNbinsX()):
    content = hist.GetBinContent(bin)
    h.SetBinContent(bin+shift, content)
  return h









