'''
Collection of classes to created resolution graphs vs. some other observable.

@author: Christian Grefe, Bonn University (christian.grefe@cern.ch)
'''

import uuid, math
from plotting.DistributionTools import truncatedInterval,truncatedIntervalFromHist, percentiles, histToArray, arrayToHist, meanAndStd,filterDataAndWeights
from plotting.Cut import Cut
from plotting.TreePlot import getValuesFromTree
from plotting.BasicPlot import BasicPlot

class Selection( object ):
    ## Helper class encapsulating a selection logic.
    #  Results are returned in the form of selection intervals.
    #  Base class does not perform any selection
    def __init__( self ):
        ## Default constructor
        self._reset()
        
    def _reset( self ):
        ## Helper method to reset the result fields.
        #  Should be called before recalculating.
        self.low = None
        self.lowLow = None
        self.lowUp = None
        self.up = None
        self.upLow = None
        self.upUp = None
    
    def intervalFromValues( self, values, weights=None ):
        ## Calculates the selected interval from weighted values
        #  No selection, simple determination of min and max value
        #  @param values    list of values
        #  @param weights   list of weights (should match length of values)
        #  @result (lower, upper) boundary
        self._reset()
        self.low = min(values)
        self.up = max(values) 
        return self.low, self.up
    
    def intervalFromHist( self, hist ):
        ## Calculates the selected interval from a histogram
        #  No selection, simple determination of lowest and highest bin with entries
        #  @param hist    1D histogram object
        #  @result (lower, upper) boundary
        self._reset()
        firstBin = hist.FindFirstBinAbove( 0. )
        lastBin = hist.FindLastBinAbove( 0. )
        self.low = hist.GetBinLowEdge( firstBin )
        self.up = hist.GetBinLowEdge( lastBin ) + hist.GetBinWidth( lastBin )
        return self.low, self.up

    
class Truncate( Selection ):
    ## Helper class encapsulating a symmetric truncation logic.
    #  Results are returned in the form of selection intervals.
    def __init__( self, fraction = 1.0 ):
        ## Default constructor
        #  @param fraction    fraction of weights that should be contained in the interval
        Selection.__init__( self )
        self.fraction = fraction
        
    def intervalFromValues( self, values, weights ):
        ## Calculates the selected interval from weighted values
        #  Symmetrically removes entries on both side until the desired fraction
        #  of weights remains. Uncertainties are estimated by interpreting the fraction
        #  of entries below and above the limits as an efficiency measurements.
        #  Limits are then given from the 1-sigma confidence interval.
        #  @param values    list of values
        #  @param weights   list of weights (should match length of values)
        #  @result (lower, upper) boundary
        self._reset()
        from ROOT import TEfficiency
        import numpy
        values = numpy.array( values )
        # simply calculate the interval that contains the desired fraction of weights
        self.low, self.up = truncatedInterval( values, self.fraction, weights )
        nTotal = len( values )
        nLow = len( values[values <= self.low] )
        nUp = len( values[values < self.up] )
        # interpret entries below and above as counting experiment
        # for 1-sigma confidence intervals the corresponding percentiles are calculated
        # as an estimate of the uncertainty on the percentile values above
        self.lowLow, self.lowUp, self.upLow, self.upUp = percentiles( values,
                                                                      [ TEfficiency.ClopperPearson( nTotal, nLow, 0.68, False ),
                                                                        TEfficiency.ClopperPearson( nTotal, nLow, 0.68, True ),
                                                                        TEfficiency.ClopperPearson( nTotal, nUp, 0.68, False ),
                                                                        TEfficiency.ClopperPearson( nTotal, nUp, 0.68, True ) ],
                                                                      weights )
        return self.low, self.up
    
    def intervalFromHist( self, hist ):
        ## Calculates the selected interval from a histogram
        #  Symmetrically removes entries on both side until the desired fraction
        #  of weights remains
        #  @param hist    1D histogram object
        #  @result (lower, upper) boundary
        self._reset()
        return truncatedIntervalFromHist( hist, self.fraction )


class Measure( object ):
    ## Helper class to encapsulate a statistical measure.
    #  In addition to the calculation of the measure, a selection object 
    #  can be used to preselect entries before determining the measurement.
    #  Derived classes need to implement __calculateFromValues__, __calculateFromHist__
    #  or both.
    def __init__( self, selection=None ):
        ## Default constructor
        #  @param selection     selection object applied before measuring
        self.selection = selection if selection is not None else Selection()
        self.label = 'Measure'
        
    def getDecoratedLabel( self, var ):
        ## Return a variable label decorated by the label of this measure
        #  @param var     Variable object
        #  @return decorated label
        label = '%s(%s)' % (self.label, var.title)
        if var.unit:
            label += ' [%s]' % var.unit
        return label
    
    def __calculateFromValues__( self, values, weights, low, up ):
        ## Helper method to calculate the measure from a list of weighted values
        #  Can be limited by lower and upper boundaries.
        #  This default method maps onto the __calculateFromHist__ method.
        #  @param values     list of values
        #  @param weights    list of weights (needs to match length of values)
        #  @param low        lower limit
        #  @param up         upper limit
        #  @returns (result, errLow, errUp)
        hist = arrayToHist( values, weights )
        return self.__calculateFromHist__( hist, low, up )
    
    def __calculateFromHist__( self, hist, low, up ):
        ## Helper method to calculate the measure from a histogram
        #  Can be limited by lower and upper boundaries.
        #  This default method maps onto the __calculateFromValues__ method.
        #  @param hist       1D histogram object
        #  @param low        lower limit
        #  @param up         upper limit
        #  @returns (result, errLow, errUp)
        values, weights = histToArray( hist )
        return self.__calculateFromValues__( values, weights, low, up )
            
    
    def calculateFromValues( self, values, weights=None ):
        ## Calculate the measure from a list of weighted values
        #  @param values     list of values
        #  @param weights    list of weights (needs to match length of values)
        #  @returns (result, errLow, errUp)
        low, up = self.selection.intervalFromValues( values, weights )
        return self.__calculateFromValues__( values, weights, low, up )
    
    def calculateFromHist( self, hist ):
        ## Calculate the measure from a histogram
        #  @param hist       1D histogram object
        #  @returns (result, errLow, errUp)
        low, up = self.selection.intervalFromHist( hist )
        return self.__calculateFromValues__( hist, low, up )
    
class Mean( Measure ):
    ## Measures the weighted mean of the input
    def __init__( self, selection=None ):
        ## Default constructor
        #  @param selection     selection object applied before measuring
        Measure.__init__( self, selection )
        self.label = 'Mean'
    
    def __calculateFromValues__( self, values, weights, low, up ):
        ## Helper method to calculate the measure from a list of weighted values
        #  Can be limited by lower and upper boundaries.
        #  @param values     list of values
        #  @param weights    list of weights (needs to match length of values)
        #  @param low        lower limit
        #  @param up         upper limit
        #  @returns (result, errLow, errUp)
        values, weights = filterDataAndWeights( values, weights, low, up )
        mean, std = meanAndStd( values, weights )
        meanErr = std / math.sqrt( values.size )
        return mean, meanErr, meanErr
    
    def __calculateFromHist__( self, hist, low, up ):
        ## Helper method to calculate the measure from a histogram
        #  Can be limited by lower and upper boundaries.
        #  @param hist       1D histogram object
        #  @param low        lower limit
        #  @param up         upper limit
        #  @returns (result, errLow, errUp)
        hist.GetXaxis().SetRangeUser( low, up )
        mean = hist.GetMean()
        meanErr = hist.GetMeanError()
        return mean, meanErr, meanErr
    
class StandardDeviation( Measure ):
    # Measures the standard deviation of the input
    def __init__( self, selection=None ):
        ## Default constructor
        #  @param selection     selection object applied before measuring
        Measure.__init__( self, selection )
        self.label = 'RMS'
    
    def __calculateFromValues__( self, values, weights, low, up ):
        ## Helper method to calculate the measure from a list of weighted values
        #  Can be limited by lower and upper boundaries.
        #  @param values     list of values
        #  @param weights    list of weights (needs to match length of values)
        #  @param low        lower limit
        #  @param up         upper limit
        #  @returns (result, errLow, errUp)
        values, weights = filterDataAndWeights( values, weights, low, up )
        std = meanAndStd( values, weights )[1]
        stdErr = 0
        if values.size > 0:
            # approximation only valid for large N. ROOT uses same.
            stdErr = std / math.sqrt( 2*(values.size-1) )
        return std, stdErr, stdErr
    
    def __calculateFromHist__( self, hist, low, up ):
        ## Helper method to calculate the measure from a histogram
        #  Can be limited by lower and upper boundaries.
        #  @param hist       1D histogram object
        #  @param low        lower limit
        #  @param up         upper limit
        #  @returns (result, errLow, errUp)
        hist.GetXaxis().SetRangeUser( low, up )
        value = hist.GetStdDev()
        error = hist.GetStdDevError()
        return value, error, error
    
class GaussianSigma( Measure ):
    ## Measures the Gaussian sigma from a fit
    def __init__( self, selection=None ):
        ## Default constructor
        #  @param selection     selection object applied before measuring
        Measure.__init__( self, selection )
        from ROOT import TF1
        self.function = TF1( 'gaus', 'gaus' )
        self.fitOptions = 'LMNQ'
        self.label = '#sigma'
    
    def __calculateFromHist__( self, hist, low, up ):
        ## Helper method to calculate the measure from a histogram
        #  Can be limited by lower and upper boundaries.
        #  @param hist       1D histogram object
        #  @param low        lower limit
        #  @param up         upper limit
        #  @returns (result, errLow, errUp)
        hist.Fit( self.function, self.fitOptions, '', low, up )
        sigma = self.function.GetParameter( 2 )
        sigmaErr = self.function.GetParError( 2 )
        return sigma, sigmaErr, sigmaErr
        
class GaussianMean( Measure ):
    ## Measures the Gaussian mean from a fit
    def __init__( self, selection=None ):
        ## Default constructor
        #  @param selection     selection object applied before measuring
        Measure.__init__( self, selection )
        from ROOT import TF1
        self.function = TF1( 'gaus', 'gaus' )
        self.label = 'Mean'
    
    def __calculateFromHist__( self, hist, low, up ):
        ## Helper method to calculate the measure from a histogram
        #  Can be limited by lower and upper boundaries.
        #  @param hist       1D histogram object
        #  @param low        lower limit
        #  @param up         upper limit
        #  @returns (result, errLow, errUp)
        hist.Fit( self.function, 'LMNQ', '', low, up )
        mean = self.function.GetParameter( 1 )
        meanErr = self.function.GetParError( 1 )
        return mean, meanErr, meanErr
    
class HalfWidth( Measure ):
    ## Measures the half width of the distribution
    def __init__( self, selection=None ):
        ## Default constructor
        #  @param selection     selection object applied before measuring
        Measure.__init__( self, selection )
        self.label = 'Half-width'
    
    def __calculateFromValues__( self, values, weights, low, up ):
        ## Helper method to calculate the measure from a list of weighted values
        #  Can be limited by lower and upper boundaries.
        #  @param values     list of values
        #  @param weights    list of weights (needs to match length of values)
        #  @param low        lower limit
        #  @param up         upper limit
        #  @returns (result, errLow, errUp)
        value = 0.5 * (up - low)
        errLow = 0.
        errUp = 0.
        if self.selection.lowUp and self.selection.upLow:
            errLow = abs(value - 0.5 * (self.selection.upLow - self.selection.lowUp))
        if self.selection.lowLow and self.selection.upUp:
            errUp = abs(0.5 * (self.selection.upUp - self.selection.lowLow) - value)
        return value, errLow, errUp


def resolutionGraph( tree, xVar, yVar, title, measure, cut='', weightExpression='' ):
    ## Create and fill a resolution graph for this dataset, i.e. resolution of y vs. x
    #  @ param tree              TTree object used to create the histogram
    #  @ param xVar              Variable object defining the xAxis and the draw command
    #  @ param yVar              Variable object defining the xAxis and the draw command
    #  @ param title             histogram title
    #  @param measure            Measure object to evaluate the resolution
    #  @ param cut               Cut object (optional)
    #  @ param weightExpression  weight expression (optional)
    #  @ return the generated histogram
    bins = xVar.binning.bins
    title = '%s vs %s' % (yVar.title, xVar.title) if not title else title
    name = 'h%s_%s' % ( title.replace(' ', '_').replace('(', '').replace(')',''), uuid.uuid1() )
    from ROOT import TGraphAsymmErrors
    graph = TGraphAsymmErrors( xVar.binning.nBins )
    graph.SetNameTitle( name, '%s;%s;%s' % (title, xVar.axisLabel, measure.getDecoratedLabel( yVar ) ) )
    # create a histogram of y for each bin in x and evaluate measure
    for iBin in xrange( xVar.binning.nBins ):
        low = bins[iBin]
        up = bins[iBin+1]
        xMean = low + 0.5 * (up - low)
        xErr = xMean - low
        myCut = (Cut( '%s >= %s && %s < %s' % (xVar.command, low, xVar.command, up) ) + cut) * weightExpression
        values, weights = getValuesFromTree( tree, yVar.command, myCut.cut )
        yMean, yErrLow, yErrUp = measure.calculateFromValues( values, weights )
        graph.SetPoint( iBin, xMean, yMean )
        graph.SetPointError( iBin, xErr, xErr, yErrLow, yErrUp )        
    return graph


if __name__ == '__main__':
    from ROOT import TTree, TRandom3
    from array import array
    from plotting.Variable import Variable, Binning
    from AtlasStyle import redLine, blueLine, greenLine
    
    # create some dummy tree
    rndm = TRandom3()
    size = array( 'f', [0] )
    energy = array( 'f', [0] )
    t = TTree( 'tree', 'My Tree' )
    t.Branch( 'size', size, 'size/F' )
    t.Branch( 'energy', energy, 'energy/F' )
    for entry in xrange( 10000 ):
        size[0] = rndm.Poisson( 3 )
        energy[0] = rndm.Landau( size[0]*2.5, size[0] )
        t.Fill()
    
    # define a variable object for each branch
    sizeVar = Variable( 'size', title='Cluster Size', binning=Binning(10, 1, 11, range(1,11)) )
    energyVar = Variable( 'energy', title='Hit Energy', unit='MeV', binning=Binning(50, 0, 100) )

    p = BasicPlot( 'test', sizeVar, Variable( 'RMS(E)', unit = 'MeV' ) )
    measure = HalfWidth()
    measure.selection = Truncate( 0.68 )
    g = p.addGraph( resolutionGraph( t, sizeVar, energyVar, '', measure ) )
    p.draw()

    g.Draw()
    
    raw_input( 'Continue?' )