'''
Collection of helper methods to statistical values on distributions.

@author: Christian Grefe, Bonn University (christian.grefe@cern.ch)
'''
import sys, math, numpy, logging, uuid

logger = logging.getLogger( __name__ )

# typical interesting fractions
OneSigmaFraction   = 0.682689492
TwoSigmaFraction   = 0.954499736
ThreeSigmaFraction = 0.997300204
FourSigmaFraction  = 0.99993666
FiveSigmaFraction  = 0.999999426697

def filterDataAndWeights( data, weights=None, low=None, up=None ):
    ## Helper method to remove all entries below or above the given limits
    #  from the data as well as the weights
    #  @param data     list of values
    #  @param weights  list of weights
    #  @return (data, weights) after filtering
    if weights is None:
        weights = numpy.ones( (len(data),) )
    else:
        weights = numpy.asarray( weights )
    if len(data) != len(weights):
        logger.error( 'filterDataAndWeights(): length of data does not match length of weights' )
    data = numpy.asarray( data )
    mask = numpy.ones( (len(data),), dtype=bool )
    if low is not None:
        mask &= data >= low
    if up is not None:
        mask &= data < up
    return data[mask], weights[mask] 

def sortDataAndWeights( data, weights=None ):
    ## Helper method to sort two arrays in parallel (using the first to determine order)
    #  Implicitely converts to numpy arrays
    #  @param data     list of values
    #  @param weights  list of weights (needs to match length of data)
    #  @return sorted (data, weights)
    if weights is None:
        weights = numpy.ones( (len(data),) )
    else:
        weights = numpy.asarray( weights )
    if len(data) != len(weights):
        logger.error( 'sortDataAndWeights(): length of data does not match length of weights' )
    data = numpy.asarray( data )
    permutation = numpy.argsort( data )
    return data[permutation], weights[permutation]

def histToArray( hist, includeOverflow=False ):
    ## Fills the entries from a histogram into an array
    #  @param hist             histogram object (1D)
    #  @param includeOverflow  decide if under- and overflow should be included as first and last bin
    #  @return (values, weights)
    dataType = 'double'
    from ROOT import TH1C, TH1S, TH1I, TH1F
    if isinstance( hist, TH1F ):
        dataType = 'float32'
    elif isinstance( hist, TH1I ):
        dataType = 'int32'
    elif isinstance( hist, TH1S ):
        dataType = 'int16'
    elif isinstance( hist, TH1C ):
        dataType = 'int8'
    weights = numpy.frombuffer( hist.GetArray(), dataType, hist.fN )
    values = numpy.empty( hist.fN )
    for index in xrange( hist.fN ):
        values[index] = hist.GetBinLowEdge( index )
    if includeOverflow:
        return values, weights
    else:
        return values[1:-1], weights[1:-1]
    
def arrayToHist( data, name=None, title=None, weights=None, nBins=100, low=None, up=None ):
    ## Fills the (weighted) values from an array into a histogram
    #  @param data          list of values
    #  @weights             list of weights (optional, needs to match length of data)
    #  @return 1D-histogram
    from ROOT import TH1D
    name = name if name is not None else 'h_%d' % uuid.uuid1()
    title = title if title is not None else name
    if len(data) < 1:
        return TH1D( name, title, nBins, 0, 1 )
    data, weights = sortDataAndWeights( data, weights )
    low = low if low is not None else data[0]
    up = up if up is not None else data[-1]
    hist = TH1D( name, title, nBins, low, up ) 
    for value, weight in zip( data, weights ):
        hist.Fill( value, weight )
    return hist

def percentiles( data, percentiles, weights=None ):
    ## Calculates the value of all requested percentiles of the given data points
    #  The percentile values are interpolated.
    #  @param data          list of values
    #  @param percentiles   list of percentiles to be calculated (each between 0 and 1)
    #  @weights             list of weights (optional, needs to match length of data)
    #  @return list of percentile values (same order as the passed percentiles)
    if len(data) < 1:
        logger.warning( 'percentiles(): no data, unable to calculate percentile' )
        return numpy.empty( len(percentiles) )
    if len(data) != len(weights):
        logger.error( 'percentiles(): length of data does not match length of weights' )
        return len(percentiles)*[0.]
    data, weights = sortDataAndWeights( data, weights )
    sumOfWeights = weights.sum()
    cumulativeWeights = numpy.cumsum( weights )
    return numpy.interp( numpy.array( percentiles ) * sumOfWeights, cumulativeWeights, data )

def truncatedInterval( data, fraction=OneSigmaFraction, weights=None ):
    ## Calculates the central interval boundaries on the given array containing the given fraction of entries
    #  Entries are trimmed symmetrically
    #  @param array     list of values
    #  @param fraction  fraction of (weighted) entries contained in the interval
    #  @param weights   list of weights, length needs to match array
    #  @return (lower, upper) boundaries
    res = percentiles( data, [ 0.5*(1-fraction), 1-0.5*(1-fraction) ], weights)
    return res[0], res[1]

def truncatedIntervalFromHist( hist, fraction=OneSigmaFraction, includeOverflow=False ):
    ## Calculates the central interval boundaries on the given histogram containing the given fraction of entries
    #  Entries are trimmed symmetrically.
    #  @param hist             histogram
    #  @param fraction         fraction of (weighted) entries contained in the interval
    #  @param includeOverflow  include under- and overflow bins
    #  @return (lower, upper) boundaries
    data, weights = histToArray( hist, includeOverflow )
    res = percentiles( data, [ 0.5*(1-fraction), 1-0.5*(1-fraction) ], weights )
    return res[0], res[1]

def truncatedMean( data, fraction=OneSigmaFraction, weights=None ):
    ## Calculates the weighted mean from the central fraction of the given (weighted) data points.
    #  @param data       list of values
    #  @param fraction   fraction of (weighted) entries contained in the interval
    #  @param weights    list of weights, length needs to match array
    #  @return weighted mean of the values within the fraction boundaries 
    low, up = truncatedInterval( data, fraction, weights )
    data = numpy.asarray( data )
    if weights is None:
        weights = numpy.empty( len(data) )
        weights.fill( 1. )
    else:
        weights = numpy.asarray( weights )
    # remove all values outside of boundaries
    mask = (data >= low) & (data < up) 
    return numpy.average( data[mask], weights=weights[mask] )

def smallestInterval( data, fraction=OneSigmaFraction, weights=None ):
    ## Finds the smallest interval within the given values conatining the given fraction of entries
    # sorting the array minimizes the number of possible intervals to consider
    data, weights = sortDataAndWeights( data, weights )
    totalSumOfWeights = weights.sum()
    # target number of entries in the interval
    targetSumOfWeights = fraction * totalSumOfWeights
    # find the smallest interval conatining the target number of entries    
    minWidth = sys.float_info.max
    minWidthStartIndex = 0
    minWidthEndIndex = 0
    minEndIndex = 1
    sumOfWeightsAfterIndex = totalSumOfWeights - numpy.cumsum( weights )
    for startIndex in xrange( len( data ) ):
        # check if the remaining fraction of weights is still sufficient
        if sumOfWeightsAfterIndex[startIndex] < targetSumOfWeights:
            break
        # check if the end index starts below the start index
        if startIndex > minEndIndex:
            minEndIndex = startIndex+1
        for endIndex in xrange( minEndIndex, len(data) ):
            width = data[endIndex] - data[startIndex]
            if width > minWidth:
                break
            weightInInterval = weights[startIndex:endIndex].sum()
            # surpassed the required fraction of weights
            if weightInInterval > targetSumOfWeights:
                if width < minWidth:
                    minWidth = width
                    minWidthStartIndex = startIndex
                    minWidthEndIndex = endIndex
                # store this index, after increasing the start index this is the minimum to end
                minEndIndex = endIndex
                break
    return data[minWidthStartIndex], data[minWidthEndIndex]

def meanAndStd( data, weights=None ):
    ## Calculates the weighted mean and standard deviation
    #  @param data     list of values
    #  @param weights  (optional) list of weights. Length needs to match data
    #  @return (mean, std)
    if weights is None:
        weights = numpy.empty( len(data) )
        weights.fill( 1. )
    else:
        weights = numpy.asarray( weights )
    if len(data) != len(weights):
        logger.error( 'meanAndStd(): length of data does not match length of weights' )
    mean = numpy.average( data, weights=weights )
    variance = numpy.average( (data - mean)**2, weights=weights )
    return mean, math.sqrt( variance )

def sumOfWeights( weights ):
    ## Calculates the sum of a list and the uncertainty on the sum
    weights = numpy.asarray( weights )
    variance = (weights**2).sum()
    return weights.sum(), math.sqrt( variance ) 

if __name__ == '__main__':
    # fill some dummy values
    import ROOT
    r = ROOT.TRandom3()
    h = ROOT.TH1D( 'h', '', 40, 0, 10 )
    v = []
    w = []
    mean = 5.0
    sigma = 1.3
    weightMean = 1.0
    weightSigma = 0.2
    for i in xrange( 1000 ):
        value = r.Gaus( mean, sigma )
        weight = r.Gaus( weightMean, weightSigma )
        h.Fill( value, weight )
        v.append( value )
        w.append( weight )

    #print filterDataAndWeights( v, w, 4, 6 )
    print 'input: mean=%.2g, sigma=%.2g, weights=%.2g+-%.2g' % (mean, sigma, weightMean,weightSigma)
    #print 'histToArray():', histToArray( h, False )
    #print 'arayToHist():', arrayToHist( v, weights=w )
    print 'percentiles([2.5%,16%,50%]):', percentiles( v, [0.025, 0.16, 0.50], w )
    print 'truncatedInterval():', truncatedInterval( v, weights=w )
    print 'truncatedIntervalFromHist():', truncatedIntervalFromHist( h, includeOverflow=True )
    print 'truncatedMean():', truncatedMean( v, weights=w )
    print 'smallestInterval():', smallestInterval( v, weights=w )
    print 'meanAndStd():', meanAndStd( v, w )
    print 'sumOfWeights():', sumOfWeights( w )
    print 'Unweighted poisson mean and variance:', len(w), math.sqrt( len(w) )
    
    x = raw_input( 'Continue?' )
    