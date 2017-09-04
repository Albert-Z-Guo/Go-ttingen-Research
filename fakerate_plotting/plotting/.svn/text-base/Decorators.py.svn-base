"""
@module Decorators 

Helper classes to decorate datasets with new info on the fly

@package plotting
@author Will Davey, Bonn University (will.davey@cern.ch)
"""

## imports
"""
from plotting.BasicPlot import BasicPlot
from plotting.TreePlot import createHistogramFromTree, getValuesFromTree
from plotting.AtlasStyle import Style
from plotting.Cut import Cut
from plotting.HistogramStore import HistogramStore
from plotting.Tools import string2bool, overflowIntoLastBins, histToGraph
from plotting.Variable import createCutFlowVariable
from plotting.Systematics import SystematicVariation, SystematicsSet,\
    TreeSystematicVariation
from plotting import DistributionTools
from copy import copy
import logging, re, os, uuid, math
"""
import logging
import ROOT
from array import array
from Dataset import PhysicsProcess


#_____________________________________________________________________________
class DatasetDecorator( object ):
    """Baseclass to decorate new info to a dataset 
    
    Decoration is done transiently: the new branch is added to a transient tree
    (ie created on the fly and not written out), which is then added as a
    friend to the existing (primary) tree of the dataset.

    Note: if absolutely necessary we could implement persistification 
          of the friend tree, although this is likely to cause more 
          trouble than good if people forget to overwrite when they 
          update the settings of their decorator. A better solution
          is the migrate the decoration to the xTauFW production once 
          it is stable.

    Note: currently the dependent variable must be an existing variable, 
          there is no built in support for using formula, eg.  
            tau_pt       - Good
            tau_pt/1000. - Wont work
          If needed this can be added via TTreeFormula, which is ~trivial. 


    @param branch - name of branch to decorate
    @param input_branches - list of branches needed by the caluclation 
                            (will optimise out unused branches)
    """
    
    #____________________________________________________________
    def __init__(self, branch, input_branches = None):
        """initialisation"""
        self.branch_name = branch
        self.input_branches = input_branches

    #____________________________________________________________
    def calc(self,tree): 
        """Calculate the value of the decoration 
        
        Should be overridden in the derived class
        
        @param tree    Primary TTree object (being decorated)
        @return float
        """
        return 2.0

    #____________________________________________________________
    def decorate(self, dataset, treeName=None):
        """Main decoration function

        @param dataset - Dataset object to decorate
        @treeName      - systematics tree to decorate
        """
        logging.info("Decorating %s, tree:%s with %s..."% \
                (dataset.name,treeName,self.branch_name))
        # recursive call on sub-datasets
        if isinstance(dataset,PhysicsProcess):
            for d in dataset.datasets: 
                self.decorate(d, treeName)
            return

        dataset.keepTreesInMemory = True
        # get primary tree
        tree = dataset._open(treeName)

        # add friend tree to dataset
        if not hasattr(tree,"friend"):
            friend = ROOT.TTree("%s_fr"%(tree.GetName()), \
                               "%s (friend)"%(tree.GetTitle()))
            tree.AddFriend(friend)
            tree.friend = friend
        friend = tree.friend 

        # add new branch
        first_branch = bool(friend.GetNbranches()==0)
        value = array('f',[0.])
        branch = friend.Branch(self.branch_name,value,"%s/F"%(self.branch_name))
        
        # optimise out unused branches in primary tree
        if self.input_branches is not None:
            live_branches = self._get_live_branches_(tree)
            self._set_branches_(tree,self.input_branches,dataset.name)

        # decorate
        for i in xrange(tree.GetEntries()):
            tree.GetEntry(i)
            friend.GetEntry(i)
            value[0] = self.calc(tree)
            if first_branch: friend.Fill()
            else: branch.Fill()
            
        # reset live branches
        if self.input_branches is not None:
            self._set_branches_(tree,live_branches+[self.branch_name],dataset.name)
        
        # flush pointer to local 'value' to avoid 
        # segfault when it goes out of scope
        friend.ResetBranchAddresses()

    #____________________________________________________________
    def _get_branches_(self,tree,live=None):
        """Return list of branches from tree
        
        @param tree - TTree
        @param live - if true only return active branches
        @return     - list of str (branch names)
        """
        l = []
        if tree.GetEntries()>-1:
          itr = tree.GetListOfBranches().MakeIterator()
          while True:
            obj = itr.Next()
            if not obj: break
            # check if switched on
            if live is True and not tree.GetBranchStatus(obj.GetName()): 
                continue
            l.append(obj.GetName())
        return l

    #____________________________________________________________
    def _get_live_branches_(self,tree):
        """Wrapper for _get_branches_(tree,live=True)"""
        return self._get_branches_(tree,live=True)

    #____________________________________________________________
    def _set_branches_(self,tree,branches,datasetname):
        """Switches branches on, everything else off
        Always switch on branches from friends

        @param tree  - TTree
        @param branches - list of str (branch names to be switched on)
        """
        #TODO does not work for TChain - it seems the BranchStatus stays deactivated
        #tree.SetBranchStatus("*",0)
        tree.SetBranchStatus("*",1)

        for b in branches: 
          if tree.GetBranch(b):
            tree.SetBranchStatus(b,1)
          else:
            print "Achtung! branch %s not available in %s"%(b,datasetname)

        # don't optimise out friend branches 
        if tree.GetListOfFriends():
            itr = tree.GetListOfFriends().MakeIterator()
            while True:
                obj = itr.Next()
                if not obj: break
                obj.GetTree().SetBranchStatus("*",1)


#_____________________________________________________________________________
class GaussDecorator(DatasetDecorator):
    """Dummy Gauss decoration
    Optimises out all branches in primary tree (input_branches = [])
    """
    #____________________________________________________________
    def __init__(self):
        DatasetDecorator.__init__(self,"Gauss",input_branches = [])

    #____________________________________________________________
    def calc(self, tree):
        """Derived calc function (returns random from normal distribution)"""
        return ROOT.gRandom.Gaus()

#_____________________________________________________________________________
class HistogramDecorator1D(DatasetDecorator):
    """Basic Fake-factor decoration

    @param branch - str (branch name)
    @param var    - Variable (dependent variable)
    @param hist   - TH1 (stores fake-factors vs dependent variable)
    """
    #____________________________________________________________
    def __init__(self,branch,var,hist):
        DatasetDecorator.__init__(self,branch,input_branches = [var.command])
        self.var = var
        self.hist = hist
        self.defaultVal = 0.

    #____________________________________________________________
    def calc(self, tree):
        """Derived calc function (returns fake-factor)"""
        # could be swapped to use TTree formula
        val = getattr(tree,self.var.command)
        ibin = self.hist.FindBin(val)
        # check if bin out of range (maybe should change to warning)
        if ibin <= 0: 
            logging.debug("Dependent variable in underflow!")
        if ibin > self.hist.GetNbinsX(): 
            logging.debug("Dependent variable in overflow!")
        
        # force bin in range
        ibin = max(ibin,0)
        ibin = min(ibin,self.hist.GetNbinsX())

        # retrieve value and return
        return self.hist.GetBinContent(ibin)
    
#_____________________________________________________________________________
class HistogramDecorator2D(DatasetDecorator):
    """Basic Fake-factor decoration

    @param branch - str (branch name)
    @param var    - Variable (dependent variable)
    @param hist   - TH1 (stores fake-factors vs dependent variable)
    """
    #____________________________________________________________
    def __init__(self,branch,xVar,yVar,hist):
        DatasetDecorator.__init__(self,branch,input_branches = [xVar.command, yVar.command])
        self.xVar = xVar
        self.yVar = yVar
        self.hist = hist

    #____________________________________________________________
    def calc(self, tree):
        """Derived calc function (returns fake-factor)"""
        # could be swapped to use TTree formula
        xVal = getattr(tree,self.xVar.command)
        yVal = getattr(tree,self.yVar.command)
        ibin = self.hist.FindBin(float(xVal),float(yVal))
        
        # check if bin out of range (maybe should change to warning)
        if ibin <= 0: 
            logging.debug("Dependent variable in underflow!")
        if ibin > self.hist.GetNbinsX(): 
            logging.debug("Dependent variable in overflow!")
        
        # retrieve value and return
        return self.hist.GetBinContent(ibin)

#_____________________________________________________________________________
class BasicFakeFactorDecorator(HistogramDecorator1D):
    """Basic Fake-factor decoration

    @param branch - str (branch name)
    @param var    - Variable (dependent variable)
    @param hist   - TH1 (stores fake-factors vs dependent variable)
    """
    #____________________________________________________________
    def __init__(self,branch,var,hist):
        HistogramDecorator1D.__init__(self,branch,var,hist)    
    
    #____________________________________________________________
    def calc(self, tree):
        """Derived calc function (returns fake-factor)"""
        # could be swapped to use TTree formula
        ff = HistogramDecorator1D.calc( self, tree )
        if ff > 1.0 or ff < 0.0: 
            print "ff: %f"%(ff)
        return ff
    

## EOF
