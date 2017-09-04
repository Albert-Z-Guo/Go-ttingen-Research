"""
@module Decorators 

Copy of Decorators.py with modifications to decorate multiple branches simultaneously (speeding up things)

@package plotting
@author Will Davey, Bonn University (will.davey@cern.ch)
@author Eric Drechsler, Goettingen University (eric.drechsler@cern.ch)
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
from plotting.Decorators import DatasetDecorator
from ROOT import TH1D,TH2D

#_____________________________________________________________________________
# Helper to optimise DatasetMultiDecorator bookkeeping
class MultiDecoratorContainer(object):
    def __init__(self,branch,var,hist):
        self.branch= branch
        self.var = var
#_____________________________________________________________________________
# Helper to optimise DatasetMultiDecorator bookkeeping
class MultiDecoratorContainer(object):
    def __init__(self,branch,var,hist):
        self.branch= branch
        self.var = var
        self.hist = hist
        self.name=branch
#_____________________________________________________________________________
# Helper to optimise DatasetMultiDecorator bookkeeping
class MultiDecoratorContainer2D(object):
    def __init__(self,branch,xvar,yvar,hist):
        self.branch= branch
        self.xvar = xvar
        self.yvar = yvar
        self.hist = hist
        self.name=branch
#_____________________________________________________________________________
class DatasetMultiDecorator( DatasetDecorator ):
    def __init__(self,dataset,multiDecorContList):
        #DatasetDecorator.__init__(self,branch,input_branches = [var.command])
        self.decorationList=multiDecorContList
        self.decorFileName=None
        self.dataset = dataset
        self.updateDecorFile = None
       # self.var = var
       # self.hist = hist
        self.defaultVal = 0.
    #____________________________________________________________
    def calc(self, tree, decoratorIndex):
        """Derived calc function (returns fake-factor)"""
        # could be swapped to use TTree formula
        
        if isinstance(self.decorationList[decoratorIndex],MultiDecoratorContainer):
          val = getattr(tree,self.decorationList[decoratorIndex].var.command)
          ibin = self.decorationList[decoratorIndex].hist.FindBin(val)
        elif isinstance(self.decorationList[decoratorIndex],MultiDecoratorContainer2D):
          xVal = getattr(tree,self.decorationList[decoratorIndex].xvar.command)
          yVal = getattr(tree,self.decorationList[decoratorIndex].yvar.command)
          ibin = self.decorationList[decoratorIndex].hist.FindBin(float(xVal),float(yVal))
          #print xVal,yVal,ibin, self.decorationList[decoratorIndex].hist.GetBinContent(ibin)
        else:
          raise Exception("Could not determine type of decoration histogram")
        if ibin <= 0: 
            logging.debug("Dependent variable in underflow!")
        if ibin > self.decorationList[decoratorIndex].hist.GetNbinsX(): 
            logging.debug("Dependent variable in overflow!")
        
        # force bin in range
       # tmpibin=ibin
       # ibin = max(ibin,0)
       # ibin = min(ibin,self.decorationList[decoratorIndex].hist.GetNbinsX())
       # if not tmpibin==ibin:
       #   raise Exception("Forced bin in range")

        # retrieve value and return
        return self.decorationList[decoratorIndex].hist.GetBinContent(ibin)
    #____________________________________________________________
    # explicit overwrite of DatasetDecorator decorate method
    def decoratePhysicsProcess(self, treeName=None):
        """Main decoration function

        @treeName      - systematics tree to decorate
        """
        if self.updateDecorFile:
          self.createDecorationTree(self.dataset, treeName)
        self.friendDecorationTree(self.dataset, treeName)
    
    def friendDecorationTree(self, dataset, treeName=None):
      from ROOT import TTree
      from ROOT import TMVA, TFile, TTree
      from plotting.Dataset import FriendTree
      # recursive call on sub-datasets
      if isinstance(dataset,PhysicsProcess):
          for d in dataset.datasets: 
              self.friendDecorationTree(d, treeName)
          return
      decorFile = TFile.Open( self.decorFileName, 'READ' )
      import logging
      if not decorFile or not decorFile.IsOpen():
        raise Exception( 'friendDecorationTree(): unable to open output file "%s"' % self.decorFileName )
      else:
        logging.debug("friendDecorationTree(): Successfully opened weightfile %s for ds %s"%(self.decorFileName,dataset.name))
      dsName=dataset.name
      friendTreedsName=dsName
# only 2016 MC samples have been decorated to avoid duplication
      if dsName.endswith("2015"):
        dsName=dataset.name.rsplit("2015")
        friendTreedsName=dsName[0]+"2016"
      dirName="decor_"+treeName
      friendTreeName="DecorationFriend_"+friendTreedsName
      decorTree = decorFile.Get(dirName+"/"+friendTreeName)
      if not decorTree:
        raise Exception( 'friendDecorarionTree(): could not open %s in file "%s"' %(dirName, friendTreeName ))
      del decorTree
      #get dataset tree
      dsTree=dataset._open(treeName)
      friendtree=FriendTree(treeName=dirName+"/"+friendTreeName, fileNames=[self.decorFileName] ,alias=dataset.name+"_"+friendTreeName+"_Friend")
      dataset.addFriendTree(friendtree)
      logging.debug( 'friendDecorationTree(): Friended %s from %s to %s.' % (friendTreeName,decorFile,dsTree.GetName()))
      decorFile.Close()
      del dsTree
        
    def writeDecorationFile(self,friendTree, dataset, treeName):
      from ROOT import TFile, TTree
      if not self.decorFileName:
        raise ValueError("In writeDecorationFile: decorFileName not set")
      outputFile = TFile.Open( self.decorFileName, 'UPDATE' )
      outputFile.cd()
      sysDir=outputFile.GetDirectory("decor_"+treeName)
      if not sysDir:
        sysDir=outputFile.mkdir("decor_"+treeName)
      sysDir.cd()
      friendTree.Write()
      outputFile.Close()
   
    #____________________________________________________________
    def createDecorationTree(self, dataset, treeName=None):
      from ROOT import TTree
      #  logging.info("Decorating %s, tree:%s with %s..."% \
      #        (self.dataset.name,treeName,self.decorationList[i].branch))
      # get primary tree
      # recursive call on sub-datasets
      if isinstance(dataset,PhysicsProcess):
          for d in dataset.datasets: 
              self.createDecorationTree(d, treeName)
          return
      if dataset.name.endswith("2015"):
        print "Skipping DS %s to avoid duplicated MC tree in decor file for 2015/16 splitting"%dataset.name
        return
      dsTree = dataset._open(treeName)
      friendTree = TTree("DecorationFriend_"+dataset.name, "DecorationFriend_"+dataset.name)
      
      values={}
      branches={}
      for i in range(0,len(self.decorationList)):
        values[i] = array('f',[0.])
       # print "register values",values[i],hex(id(values[i]))
        branches[i] = friendTree.Branch(self.decorationList[i].branch,values[i],"%s/F"%(self.decorationList[i].branch))
       # print "register branches",branches[i],hex(id(branches[i]))

      # decorate
      for i in dsTree:
          for j in range(0,len(self.decorationList)):
            values[j][0] = self.calc(dsTree,j)
          friendTree.Fill()
          for j in range(0,len(self.decorationList)):
            val=branches[j].GetLeaf(self.decorationList[j].branch).GetValue()
        #    print "getting branch val:", j, val
      
      self.writeDecorationFile(friendTree,dataset,treeName)
