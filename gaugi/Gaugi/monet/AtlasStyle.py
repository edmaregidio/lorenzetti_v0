__all__ = ["SetAtlasStyle","ATLASLabel","ATLASLumiLabel","AtlasTemplate1","setLegend1"]


def SetAtlasStyle ():
  print ("\nApplying ATLAS style settings...")
  from ROOT import gROOT, gStyle
  icol=0
  gStyle.SetFrameBorderMode(icol)
  gStyle.SetFrameFillColor(icol)
  gStyle.SetCanvasBorderMode(icol)
  gStyle.SetCanvasColor(icol)
  gStyle.SetPadBorderMode(icol)
  gStyle.SetPadColor(icol)
  gStyle.SetStatColor(icol)
  #atlasStyle.SetFillColor(icol) # don't use: white fill color for *all* objects
  # set the paper & margin sizes
  gStyle.SetPaperSize(20,26)

  # set margin sizes
  gStyle.SetPadTopMargin(0.05)
  gStyle.SetPadRightMargin(0.05)
  gStyle.SetPadBottomMargin(0.16)
  gStyle.SetPadLeftMargin(0.16)

  # set title offsets (for axis label)
  gStyle.SetTitleXOffset(1.4)
  gStyle.SetTitleYOffset(1.4)

  ## use large fonts
  ##Int_t font=72 # Helvetica italics
  font=42 # Helvetica
  tsize=0.05
  gStyle.SetTextFont(font)

  gStyle.SetTextSize(tsize)
  gStyle.SetLabelFont(font,"x")
  gStyle.SetTitleFont(font,"x")
  gStyle.SetLabelFont(font,"y")
  gStyle.SetTitleFont(font,"y")
  gStyle.SetLabelFont(font,"z")
  gStyle.SetTitleFont(font,"z")

  gStyle.SetLabelSize(tsize,"x")
  gStyle.SetTitleSize(tsize,"x")
  gStyle.SetLabelSize(tsize,"y")
  gStyle.SetTitleSize(tsize,"y")
  gStyle.SetLabelSize(tsize,"z")
  gStyle.SetTitleSize(tsize,"z")

  # use bold lines and markers
  gStyle.SetMarkerStyle(20)
  gStyle.SetMarkerSize(1.2)
  gStyle.SetHistLineWidth(2)
  gStyle.SetLineStyleString(2,"[12 12]") # postscript dashes

  # get rid of X error bars
  #gStyle.SetErrorX(0.001)
  # get rid of error bar caps
  gStyle.SetEndErrorSize(0.)

  # do not display any of the standard histogram decorations
  gStyle.SetOptTitle(0)
  gStyle.SetOptStat(1111)
  gStyle.SetOptStat(0)
  gStyle.SetOptFit(1111)
  gStyle.SetOptFit(0)

  # put tick marks on top and RHS of plots
  gStyle.SetPadTickX(1)
  gStyle.SetPadTickY(1)
  gStyle.SetPalette(1)


from ROOT import TLatex, gPad

def ATLASLabel(x,y,text,color=1):
  l = TLatex()
  l.SetNDC()
  l.SetTextFont(72)
  l.SetTextColor(color)
  delx = 0.115*696*gPad.GetWh()/(472*gPad.GetWw())
  l.DrawLatex(x,y,"ATLAS")
  if True:
    p = TLatex()
    p.SetNDC()
    p.SetTextFont(42)
    p.SetTextColor(color)
    p.DrawLatex(x+delx,y,text)
    #p.DrawLatex(x,y,"#sqrt{s}=900GeV");

def ATLASLumiLabel(x,y,lumi=None,color=1):
    l = TLatex()
    l.SetNDC()
    l.SetTextFont(42)
    l.SetTextSize(0.045)
    l.SetTextColor(color)
    dely = 0.115*472*gPad.GetWh()/(506*gPad.GetWw())
    label="#sqrt{s}=13 TeV"
    if lumi is not None: label += ", #intL dt = " + lumi + " fb^{-1}"
    l.DrawLatex(x,y-dely,label)


def setLegend1(leg):
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.032)
    leg.SetLineColor(1)
    leg.SetLineStyle(1)
    leg.SetLineWidth(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.Draw()


def AtlasTemplate1( canvas, **kw ):

  atlaslabel = kw.pop('atlaslabel', 'Internal')
  dolumi = kw.pop('dolumi',False)
  #ATLASLabel(0.2,0.85,'Preliminary')
  #ATLASLabel(0.2,0.85,'Internal')
  if atlaslabel:
    ATLASLabel(0.2,0.85, atlaslabel)
  if dolumi:
    ATLASLumiLabel(0.2,0.845,'33.5')
  #ATLASLumiLabel(0.2,0.845)
  canvas.Modified()
  canvas.Update()


