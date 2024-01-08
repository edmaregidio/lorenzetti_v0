

__all__ = ["AutoFixAxes", "NearestNiceNumber", "MinimumForLog", "FixYaxisRanges", "SetYaxisRanges", 
    "GetYaxisRanges", "FixXaxisRanges", "SetXaxisRanges", "GetXaxisRanges", "GetXaxis", "ReweightXAxisScale",
    "eps"]


eps = 7./3 - 4./3 -1

##
## This function will fit all of the histgram bin content, or TGraph points on a plot.
## If a text or legend has been added to the plot it will force the plot content to appear BELOW
## the text.
##
def AutoFixAxes(can, ignoreErrors=False, both=False,
                xminf=1., xminc=0., xmaxf=1., xmaxc=0.,
                yminf=1., yminc=0., ymaxf=1., ymaxc=0.,
                limitXaxisToFilledBins=False, changeAllXAxis=False):
    from ROOT import TFrame
    import math
    if can.GetPrimitive('pad_top') :
        AutoFixAxes(can.GetPrimitive('pad_top'),ignoreErrors=ignoreErrors, both=both,
                xminf=xminf, xminc=xminc, xmaxf=xmaxf, xmaxc=xmaxc,
                yminf=yminf, yminc=yminc, ymaxf=ymaxf, ymaxc=ymaxc,
                limitXaxisToFilledBins=limitXaxisToFilledBins, changeAllXAxis=changeAllXAxis)
        if both and can.GetPrimitive('pad_bot'):
            xmin, xmax = FixXaxisRanges(can.GetPrimitive('pad_top'), xminf, xminc, xmaxf, xmaxc, limitXaxisToFilledBins=limitXaxisToFilledBins, forAll=changeAllXAxis)
            AutoFixAxes(can.GetPrimitive('pad_bot'),ignoreErrors=ignoreErrors, both=both,
                xminf=xminf, xminc=xminc, xmaxf=xmaxf, xmaxc=xmaxc,
                yminf=yminf, yminc=yminc, ymaxf=ymaxf, ymaxc=ymaxc,
                limitXaxisToFilledBins=limitXaxisToFilledBins, changeAllXAxis=changeAllXAxis)
            SetXaxisRanges(can.GetPrimitive('pad_bot'),xmin*xminf+xminc,xmax*xmaxf+xmaxc, forAll=changeAllXAxis)
        return
    FixXaxisRanges(can, xminf, xminc, xmaxf, xmaxc, limitXaxisToFilledBins=limitXaxisToFilledBins, forAll=changeAllXAxis)

    maxy_frac = 1
    tframe_height = 1-can.GetTopMargin()-can.GetBottomMargin()
    for i in can.GetListOfPrimitives() :
        if type(i) == type(TFrame()) :
            continue
        if hasattr(i,'GetY1NDC') :
            maxy_frac = min(maxy_frac,i.GetY1NDC())
        if hasattr(i,'GetY') :
            maxy_frac = min(maxy_frac,i.GetY())

    (miny,maxy) = GetYaxisRanges(can,check_all=True,ignorezeros=True,ignoreErrors=ignoreErrors)

    if miny == 0 and maxy == 0 :
        return
    miny = (0.95*miny)*(miny>0)+(1.05*miny)*(miny<0)
    maxy_frac = maxy_frac-can.GetBottomMargin()
    if can.GetLogy() :
        # special treatment for log plots
        miny = 0.85*MinimumForLog(can)
        # some orders of magnitude *above* miny, making room for text
        orderofmagnitude_span = math.log(maxy/miny)/math.log(10)
        orderofmagnitude_span = 1.1*orderofmagnitude_span*tframe_height/maxy_frac
        maxy = miny*math.pow(10,orderofmagnitude_span)
    else :
        # scale to make space for text
        maxy_frac = maxy_frac-.02
        maxy = tframe_height*(maxy-miny)/float(maxy_frac)+miny
        # round y axis to nice round numbers
        (miny,maxy) = NearestNiceNumber(miny,maxy)
    SetYaxisRanges(can,miny*yminf+yminc-eps,maxy*ymaxf+ymaxc+eps)
    return

##
## Snap to base-ten-centric numbers
##
def NearestNiceNumber(miny,maxy) :
    import math
    round_number = 10 # or 5 perhaps
    if maxy-miny>0:
        smallest_increment = pow(10,math.floor(math.log((maxy-miny))/math.log(10))-2)
        newminy = round_number*smallest_increment*      int(miny/(round_number*smallest_increment))
        newmaxy = round_number*smallest_increment*math.ceil(maxy/(round_number*smallest_increment))
    else:
        newminy = miny; newmaxy = maxy
    return newminy,newmaxy

##
## Find the non-zero y-axis minimum of plot content.
##
def MinimumForLog(can) :
    from ROOT import TGraph,TH1,TMath
    ymin = 999999999
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),TGraph) :
            for y in i.GetY() :
                if y <= 0 :
                    y = ymin
                ymin = min(ymin,y)
        if issubclass(type(i),TH1) :
            for bin in range(i.GetNbinsX()) :
                y = i.GetBinContent(bin+1)
                if y <= 0 :
                    y = ymin
                ymin = min(ymin,y)
    return ymin

##
## Fit all the data into the canvas (for the y-axis)
##
def FixYaxisRanges(can,check_all=True,ignorezeros=True,ignoreErrors=False,
                   yminf=1., yminc=0., ymaxf=1., ymaxc=0.) :
    (ymin,ymax) = GetYaxisRanges(can,check_all,ignorezeros,ignoreErrors)
    SetYaxisRanges(can,ymin*yminf+yminc,ymax*ymaxf+ymaxc)
    return

##
## Set the x-axis ranges of a canvas
##
def SetYaxisRanges(can,ymin,ymax) :
    if can.GetPrimitive('pad_top') :
        SetYaxisRanges(can.GetPrimitive('pad_top'),ymin,ymax)
    if ymin == ymax - eps:
        from math import floor
        ymin = floor(ymin) - eps
        ymax = floor(ymax+1)
    from ROOT import TGraph,TH1
    yaxis = 0
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),TGraph) :
            yaxis = i.GetHistogram().GetYaxis()
            break
        if issubclass(type(i),TH1) :
            yaxis = i.GetYaxis()
            break
    if not yaxis :
        print ('Warning: SetYaxisRange had no effect. Check that your canvas has plots in it.')
        return
    yaxis.SetRangeUser(ymin,ymax)
    can.Modified()
    can.Update()
    return

##
## Returns the y-range of the first plotted histogram.
## If you specify "check_all=True", returns the maximal y-range of all the plots in the canvas
##
def GetYaxisRanges(can,check_all=False,ignorezeros=False,ignoreErrors=False) :
    #
    # check_all is if you want to check the maximum extent of all the histograms you plotted.
    #
    from .PlotFunctions import GetHistogramsMinMax
    ymin, ymax = GetHistogramsMinMax(can.GetListOfPrimitives(), check_all, ignorezeros, ignoreErrors)

    return ymin,ymax

##
## Fit all the data into the canvas (for the x-axis)
##
def FixXaxisRanges(can,
                   xminf=1., xminc=0., xmaxf=1., xmaxc=0., limitXaxisToFilledBins=False, forAll=False) :
    (xmin,xmax) = GetXaxisRanges(can,check_all=True, getFilledLimit=limitXaxisToFilledBins)
    SetXaxisRanges(can,xmin*xminf+xminc,xmax*xmaxf+xmaxc, forAll=forAll)
    return xmin, xmax

##
## Set the x-axis ranges of a canvas
##
def SetXaxisRanges(can,xmin,xmax,forAll=False) :
    from ROOT import TGraph,TH1
    xaxis = 0
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),TGraph) :
            xaxis = i.GetHistogram().GetXaxis()
            break
        if issubclass(type(i),TH1) :
            xaxis = i.GetXaxis()
            break
    if not xaxis :
        print ('Warning: SetXaxisRange had no effect. Check that your canvas has plots in it.')
        return
    if forAll: xaxis.SetRangeUser(xmin,xmax)
    else: xaxis.SetLimits(xmin,xmax)
    can.Modified()
    can.Update()
    return

##
## Returns the x-range of the first plotted histogram.
## If you specify "check_all=True", returns the maximal x-range of all the plots in the canvas
##
def GetXaxisRanges(can,check_all=False, getFilledLimit=False) :
    import numpy as np
    from ROOT import TGraph,TH1,TGraphErrors
    from operator import itemgetter
    xmin = 999999999.
    xmax = -999999999.
    for i in can.GetListOfPrimitives() :
        if isinstance(i,TGraph) :
            #xaxis = i.GetHistogram().GetXaxis()
            #if i.GetN():
            #    x = i.GetX()
            #    if i.GetN():
            #        #if isinstance(i,TGraphErrors) :
            #        #    print i.GetN(), i.GetName()
            #        #    xh = i.GetEXhigh()
            #        #    xl = i.GetEXlow()
            #        #    print xh, xl, x
            #        #    xmin = min([x[j] - xl[j] for j in range(i.GetN())])
            #        #    xmax = max([x[j] + xh[j] for j in range(i.GetN())])
            #        #else:
            #        if True:
            #            xmin = min([x[j] for j in range(i.GetN())])
            #            xmax = max([x[j] for j in range(i.GetN())])
            #    if not check_all and not i.GetName().endswith('_specialCases'):
            #        return xmin, xmax
            pass
        if issubclass(type(i),TH1) :
            xaxis = i.GetXaxis()
            if not check_all :
                return xaxis.GetXmin(),xaxis.GetXmax()
            if getFilledLimit:
                x = [i.GetBinCenter(idx) for idx in range(1,i.GetNbinsX()+1) if i.GetBinContent(idx)>0]
                if x:
                    xmin = min(xmin,x[0])
                    xmax = max(xmax,x[-1])
            else:
                xmin = min(xmin,xaxis.GetXmin())
                xmax = max(xmax,xaxis.GetXmax())
    return xmin,xmax

def GetXaxis(can):
    # FIXME Needs work, just a fast function for now
    xaxis = None
    from ROOT import TGraph, TH1
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),TGraph) :
            xaxis = i.GetHistogram().GetXaxis()
        if issubclass(type(i),TH1) :
            xaxis = i.GetXaxis()
        if xaxis: break
    return xaxis

class ReweightXAxisScale(object):
    """
    Adapts histograms and canvas to have points of higher importance occupying
    larger space in the x axis and further improve the visualization of their
    information.
    """

    _count = 0
    possible_sizes = list(reversed([1,2,3,4,5,6,8,10,12,14]))

    def __init__( self, xedges, weights
                , addLabels = True, addTopXNumbers = True, labelSize = None
                , method = "pureWeight", N1 = 5, N2 = 6, N3=5
                ):
        import numpy as np, ROOT
        if isinstance(xedges,ROOT.TH1): xedges = [xedges.GetBinLowEdge(xc) for xc in range(1,xedges.GetNbinsX()+2)]
        self.xedges = np.array(xedges) if not isinstance(xedges,np.ndarray) else xedges
        self.xcenters = np.array(map(lambda xl,xu: (xu+xl)/2, self.xedges[:-1], self.xedges[1:]))
        self.weights = np.array(weights) if not isinstance(weights,np.ndarray) else weights
        if len(xedges) != len(weights)+1:
            raise ValueError("Edges length do not match value expected. Is %d, should be %d!" % (len(xedges), len(weights)+1))
        self.addLabels = addLabels
        self.labelSize = labelSize
        self.addTopXNumbers = addTopXNumbers
        #self.drawXPosUpper
        self.func = self.__retrieveF1(method)
        self.N1 = N1; self.N2 = N2; self.N3 = N3
        ReweightXAxisScale._count += 1

    def __call__(self, arg):
        import ROOT
        #if isinstance(arg,)
        self.__reweightCanvas(arg, self.addLabels, self.addTopXNumbers )

    def getNewSize(self,i):
        return possible_sizes[i+1] if i < len(possible_sizes) else possible_sizes[i]

    def __retrieveF1(self, method):
        from ROOT import TF1
        s = '(x<%(x_0)f)*x + ( 0' % { 'x_0' : self.xedges[0] }
        if method == "pureWeight":
            # Normalize so that we have each each contribution not increased by deltaX
            self.weights /= [self.__deltaX(i+1) if self.__deltaX(i+1) else 1. for i in range(len(self.weights))]
        # else the weights will also be weightened by the x bin size
        dY = self.__deltaY()
        dX = self.__deltaX()
        self.weights = self.weights * ( dX/dY if dY else 1. )
        #else do nothing
        for i in range(len(self.weights)):
            cDy = self.__deltaY(i+1)
            if self.xedges[i+1] > self.xedges[i]:
                s += ' + (x>=%(x_i)f)*(%(w)f*(x-%(x_i)f)+%(prevDy)f)*(x<%(x_in)f)' % { 'x_i' : self.xedges[i]
                                                                                     , 'x_in' : self.xedges[i+1]
                                                                                     , 'prevDy' : cDy + self.xedges[0]
                                                                                     , 'w' : self.weights[i]
                                                                                     }
        s += ') + (x>=%(x_n)f)*(x-%(x_n)f+%(prevDy)f)' %  { 'x_n' : self.xedges[-1]
                                                          , 'prevDy' : self.__deltaY() + self.xedges[0]
                                                          }
        return TF1("reweight_%d" % ReweightXAxisScale._count, s, self.xedges[0], self.xedges[-1] )

    def transform(self, x):
        from numpy import array
        from ROOT import TH1
        if isinstance(x,TH1):
            x = x.Clone()
            x.SetBins(x.GetNbinsX(), array([self.func.Eval(x.GetBinLowEdge(xi)) for xi in range(1,x.GetNbinsX()+2)]))
            return x
        else:
            return self.func.Eval(x)

    def __deltaX(self,i=None):
        if i is None:
            return self.xedges[-1] - self.xedges[0]
        else:
            return self.xedges[i] - self.xedges[i-1] if i > 0. else self.xedges[0]

    def __deltaY(self,i=None):
        if i is not None:
          return sum(map(lambda x1,x2: x2-x1, zip(self.xedges[:i-1],self.xedges[1:i]))*(self.weights[:i-1])) if i>0. else 0
        else:
          return sum(map(lambda x1,x2: x2-x1, zip(self.xedges[:-1],self.xedges[1:]))*(self.weights) )

    def __reweightCanvas(self, can, addLabels, addTopXNumbers):
        import numpy as np, ROOT
        from ROOT import TGaxis, TLatex, kBlack
        if can.GetPrimitive('pad_top'):
            self.__reweightCanvas(can.GetPrimitive('pad_top'), False, addTopXNumbers)
        if can.GetPrimitive('pad_bot'):
            self.__reweightCanvas(can.GetPrimitive('pad_bot'), self.addLabels, False)
        if can.GetPrimitive('pad_bot') or can.GetPrimitive('pad_bot'): return
        can.cd()
        # First we "remove" previous axis
        xaxis = GetXaxis(can)
        # Now create new axis
        #xaxis.SetName("__xaxis_ignored")
        # Now draw new canvas
        #xmin, xmax = GetXaxisRanges(can)
        #import os
        #c = ROOT.TCanvas(self.func.GetName(),self.func.GetName())
        #self.func.Draw()
        #c.SaveAs( os.path.join( 'e26_RunByRun_noAdjustment', c.GetName() +'.pdf' ) )
        #can.cd()
        #chopt = "+C" + ("U" if not addLabels else "")
        chopt = "+CU"
        axis = TGaxis( can.GetUxmin(), can.GetUymin()
                     , can.GetUxmax(), can.GetUymin()
                     , self.func.GetName()
                     , 10000*self.N3+100*self.N2+1*self.N1, chopt )
        axis.SetNoExponent(False)
        #axis.SetExponentOffset()
        if xaxis:
            axis.ImportAxisAttributes(xaxis)
            xaxis.SetTickLength(0)
            xaxis.SetLabelOffset(999.)
        if self.labelSize: axis.SetLabelSize( self.labelSize )
        #1 + 100*N2 + *N3N
        axis.Draw()
        from .PlotFunctions import tobject_collector
        if addTopXNumbers:
            _, ymax = GetYaxisRanges(can,check_all=True,ignorezeros=True,ignoreErrors=False)
            for xc in self.xcenters:
                text = TLatex(self.func.Eval(xc), ymax, str(xc)  )
                text.SetTextFont(43)
                text.SetTextSize(2)
                text.SetTextAlign(12)
                text.SetTextAngle(90)
                text.SetTextColor( ROOT.kBlack )
                text.Draw()
                tobject_collector.append(text)
        if addLabels:
            binLow, binHigh, nBins = self.__getXEdges( chopt )
            #labelPos = map( lambda x: (x,self.func.GetX(x),(self.func.GetX(x)-self.xedges[0])/(self.xedges[-1]-self.xedges[0]))
            #              , np.linspace(binLow,binHigh, nBins) )
            labelPos = map( lambda x: (x,self.func.Eval(x),(self.func.Eval(x)-self.xedges[0])/(self.xedges[-1]-self.xedges[0])), np.linspace(binLow,binHigh, nBins) )
            ypos = can.GetUymin()-0.04*(can.GetUymax()-can.GetUymin())
            #labels = []
            for x, mx, pmx in labelPos:
                text = TLatex(mx,ypos,str(x));
                text.SetTextFont(43)
                #text.SetTextSizePixels(textPerc)
                text.SetTextAlign(23)
                text.SetTextColor( ROOT.kBlack )
                text.SetTextSize(14)
                text.Draw()
                tobject_collector.append(text)
                #labels.append(text)
            #gxc = (self.xedges[-1]-self.xedges[0] )/2
            #lLabels = len(labels)
            #for i, text in enumerate(labels):
            #    xc = text.GetBBoxCenter()
            #    if xc < gxc:
            #        if i+1 < lLabels:
            #            text2 = labels[i+1]
            #            while conflict(text.GetBBox(),text2.GetBBox()):
            #                sizes[i] = possible_sizes[sizes[i]+1]
            #                 text.SetTextSize( getNewSize


        ##AdjustBinSize (Double_t A1, Double_t A2, Int_t nold, Double_t &BinLow, Double_t &BinHigh, Int_t &nbins, Double_t &BinWidth)
        #lLabels = [labels.At(i) for i in range(labels.GetEntries())]
        tobject_collector.append( axis )
        #can.Modified()
        #can.Update()
        return axis

    def __getXEdges(self, chopt):
        """
        Adaptation of https://root.cern.ch/doc/master/TGaxis_8cxx_source.html#l02148
        to ROOT
        """
        # FIXME HARD-CODED FOR NOW
        return self.xedges[0], self.xedges[-1], 2
        #import ROOT, ctypes
        #from ROOT import THLimitsFinder
        #wmin = self.xedges[0]
        #wmax = self.xedges[-1]
        #binLow = ROOT.Double(wmin)
        #binHigh = ROOT.Double(wmax)
        #nbins = ROOT.Long(0)
        #binWidth = ROOT.Double(0.)
        #THLimitsFinder.OptimizeLimits(self.N1, nbins, binLow, binHigh, False)
        #if ((wmin-binLow)  > eps):
        #    binLow  += binWidth;
        #if ((binHigh-wmax) > eps):
        #    binHigh -= binWidth
        #    nbins -= 1
        #return binLow, binHigh, nbins

#def PaintCandlePlotV610(can, h2,l):
#    import ROOT
#
#    #kNoOption = 0, kBox = 1, kMedianLine = 10, kMedianNotched = 20,
#    #kMedianCircle = 30, kMeanLine = 100, kMeanCircle = 300, kWhiskerAll = 1000,
#    #kWhisker15 = 2000, kAnchor = 10000, kPointsOutliers = 100000, kPointsAll = 200000,
#    #kPointsAllScat = 300000, kHistoLeft = 1000000, kHistoRight = 2000000, kHistoViolin = 3000000,
#    #kHistoZeroIndicator = 10000000, kHorizontal = 1000000000
#
#    myCandle = ROOT.TCandle()
#    r = myCandle.ParseOption(l)
#    myCandle.SetOption(3000000)
#    #myCandle.SetMarkerColor(h2.GetLineColor())
#    #myCandle.SetLineColor(h2.GetLineColor())
#    myCandle.SetFillColor(h2.GetFillColor())
#    myCandle.SetFillStyle(h2.GetFillStyle())
#    myCandle.SetMarkerSize(h2.GetMarkerSize())
#    myCandle.SetMarkerStyle(h2.GetMarkerStyle())
#    myCandle.SetLog(False,False)
#
#    swapXY = myCandle.IsHorizontal()
#    print "horizontal:", swapXY
#    standardCandleWidth = 0.66
#
#    fXaxis = h2.GetXaxis()
#
#    from TagAndProbeFrame.PlotFunctions import tobject_collector
#    if not swapXY:
#       for i in range(1,h2.GetNbinsX()+1):
#           print "painting histogram", i
#           binPosX = fXaxis.GetBinLowEdge(i)
#           binWidth = fXaxis.GetBinWidth(i)
#           hproj = h2.ProjectionY("_px", i, i)
#           if (hproj.GetEntries() !=0):
#               width = h2.GetBarWidth()
#               offset = h2.GetBarOffset()*binWidth
#               if (width > 0.999 and width < 1.001): width = standardCandleWidth
#               print hproj.GetEntries(), "w", width, "bW", binWidth, "bPos", binPosX
#               myCandle.SetAxisPosition(binPosX+binWidth/2. + offset)
#               myCandle.SetWidth(width*binWidth)
#               myCandle.SetHistogram(hproj)
#               myCandle.Paint()
#               tobject_collector.append( hproj )
#    else:
#        raise NotImplementedError("Adaptation of the candle for x axis is not available on python")
#       #for (Int_t i=Hparam.yfirst; i<=Hparam.ylast; i++) {
#       #   Double_t binPosY = fYaxis->GetBinLowEdge(i);
#       #   Double_t binWidth = fYaxis->GetBinWidth(i);
#       #   hproj = h2.ProjectionX("_py", i, i);
#       #   if (hproj.GetEntries() !=0) {
#       #      Double_t width = h2.GetBarWidth();
#       #      Double_t offset = h2.GetBarOffset()*binWidth;
#       #      if (width > 0.999 && width < 1.001) width = standardCandleWidth;
#       #      myCandle.SetAxisPosition(binPosY+biWidth/2. + offset);
#       #      myCandle.SetWidth(width*binWidth);
#       #      myCandle.SetHistogram(hproj);
#       #      myCandle.Paint();
#    tobject_collector.append( myCandle )
#
#
#def PaintCandlePlotV611(can, h2,l):
#    import ROOT
#
#    myCandle = ROOT.TCandle()
#    opt = myCandle.ParseOption(l)
#    myCandle.SetOption(opt)
#    myCandle.SetMarkerColor(h2.GetLineColor())
#    myCandle.SetLineColor(h2.GetLineColor())
#    myCandle.SetLineWidth(h2.GetLineWidth())
#    myCandle.SetFillColor(h2.GetFillColor())
#    myCandle.SetFillStyle(h2.GetFillStyle())
#    myCandle.SetMarkerSize(h2.GetMarkerSize())
#    myCandle.SetMarkerStyle(h2.GetMarkerStyle())
#
#    swapXY = myCandle.IsHorizontal()
#    standardCandleWidth = 0.66;
#    standardHistoWidth = 0.8;
#
#    allMaxContent = h2.GetBinContent(h2.GetMaximumBin())
#    allMaxIntegral = 0;
#
#    fXaxis = GetXaxis(can)
#    if not fXaxis:
#        raise RuntimeError("Couldn't get axis...")
#
#    if not swapXY:
#       # Determining the slice with the maximum content
#       for i in range(1,h2.GetNbinsX()+1):
#          hproj = h2.ProjectionY("_px", i, i);
#          if (hproj.Integral() > allMaxIntegral): allMaxIntegral = hproj.Integral();
#       for i in range(1,h2.GetNbinsX()+1):
#          binPosX = fXaxis.GetBinLowEdge(i);
#          binWidth = fXaxis.GetBinWidth(i);
#          hproj = h2.ProjectionY("_px", i, i);
#          if (hproj.GetEntries() !=0):
#             candleWidth = h2.GetBarWidth();
#             offset = h2.GetBarOffset()*binWidth;
#             myMaxContent = hproj.GetBinContent(hproj.GetMaximumBin());
#             myIntegral = hproj.Integral();
#             histoWidth = candleWidth;
#             if (candleWidth > 0.999 and candleWidth < 1.001):
#                 candleWidth = standardCandleWidth
#                 histoWidth = standardHistoWidth
#             if (myCandle.IsViolinScaled()): histoWidth *= myMaxContent/allMaxContent
#             if (myCandle.IsCandleScaled()): candleWidth *= myIntegral/allMaxIntegral
#
#             myCandle.SetAxisPosition(binPosX+binWidth/2. + offset);
#             myCandle.SetCandleWidth(candleWidth*binWidth);
#             myCandle.SetHistoWidth(histoWidth*binWidth);
#             myCandle.SetHistogram(hproj);
#             myCandle.Paint();
#    else:
#        raise NotImplementedError("Adaptation of the candle for x axis is not available on python")
#    #} else { // Horizontal candle
#    #   //Determining the slice with the maximum content
#    #   for (Int_t i=Hparam.yfirst; i<=Hparam.ylast; i++) {
#    #      hproj = h2.ProjectionX("_py", i, i);
#    #      if (hproj.Integral() > allMaxIntegral) allMaxIntegral = hproj->Integral();
#    #   }
#    #   for (Int_t i=Hparam.yfirst; i<=Hparam.ylast; i++) {
#    #      Double_t binPosY = fYaxis->GetBinLowEdge(i);
#    #      Double_t binWidth = fYaxis->GetBinWidth(i);
#    #      hproj = h2.ProjectionX("_py", i, i);
#    #      if (hproj.GetEntries() !=0) {
#    #         Double_t candleWidth = h2.GetBarWidth();
#    #         Double_t offset = h2.GetBarOffset()*binWidth;
#    #         double myMaxContent = hproj.GetBinContent(hproj->GetMaximumBin());
#    #         double myIntegral = hproj.Integral();
#    #         Double_t histoWidth = candleWidth;
#    #         if (candleWidth > 0.999 && candleWidth < 1.001) {
#    #             candleWidth = standardCandleWidth;
#    #             histoWidth = standardHistoWidth;
#    #         }
#    #         if (Hoption.Logz && myMaxContent > 0) {
#    #             histoWidth *= myMaxContent/TMath::Log10(myMaxContent);
#    #             if (myCandle.IsViolinScaled() && myMaxContent > 0 && allMaxContent > 0) histoWidth *= TMath::Log10(myMaxContent)/TMath::Log10(allMaxContent);
#    #         } else if (myCandle.IsViolinScaled()) histoWidth *= myMaxContent/allMaxContent;
#    #         if (myCandle.IsCandleScaled()) candleWidth *= myIntegral/allMaxIntegral;
#
#    #         myCandle.SetAxisPosition(binPosY+binWidth/2. + offset);
#    #         myCandle.SetCandleWidth(candleWidth*binWidth);
#    #         myCandle.SetHistoWidth(histoWidth*binWidth);
#    #         myCandle.SetHistogram(hproj);
#    #         myCandle.Paint();
