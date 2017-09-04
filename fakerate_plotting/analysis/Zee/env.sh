# Any python 2.7 + ROOT setup should work. The extra packages included like numpy are actually not used but might prove useful in user code

# setup a proper python environment on lxplus
export PYTHONDIR=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/python/2.7.3-x86_64-slc6-gcc47/sw/lcg/external/Python/2.7.3/x86_64-slc6-gcc47-opt/

if [ -d $PYTHONDIR ]; then
    export PYTHONDIR=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/python/2.7.3-x86_64-slc6-gcc47/sw/lcg/external/Python/2.7.3/x86_64-slc6-gcc47-opt/
    export PATH=$PYTHONDIR/bin:$PATH
    export LD_LIBRARY_PATH=$PYTHONDIR/lib:$LD_LIBRARY_PATH
    export PYTHONPATH=$PYTHONDIR
    
    # Numpy, etc.
    export PYTHONPATH=/cvmfs/atlas.cern.ch/repo/sw/software/AthAnalysisBase/x86_64-slc6-gcc49-opt/2.4.24/sw/lcg/releases/LCG_81e/pyanalysis/1.5_python2.7/x86_64-slc6-gcc49-opt/lib/python2.7/site-packages:$PYTHONPATH

    # IPython, etc.
    export PYTHONPATH=/cvmfs/atlas.cern.ch/repo/sw/software/AthAnalysisBase/x86_64-slc6-gcc49-opt/2.4.24/sw/lcg/releases/LCG_81e/pytools/1.9_python2.7/x86_64-slc6-gcc49-opt/lib/python2.7/site-packages:$PYTHONPATH
    export PATH=/cvmfs/atlas.cern.ch/repo/sw/software/AthAnalysisBase/x86_64-slc6-gcc49-opt/2.4.24/sw/lcg/releases/LCG_81e/pytools/1.9_python2.7/x86_64-slc6-gcc49-opt/bin:$PATH
fi

# setup the standard ROOT environment
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh # = setupATLAS
lsetup root

# where is the package installed (independent of from where this script was actually executed)

if [ -n "$ZSH_VERSION" ]; then
   # assume Zsh
   FULLSCRIPTNAME=$0:A
   SCRIPTNAME=/$0
   THISPATH=${FULLSCRIPTNAME%$SCRIPTNAME}
#elif [ -n "$BASH_VERSION" ]; then
#   # assume Bash
else
   # asume something else (including Bash)
  THISPATH=$(readlink -f $(dirname ${BASH_ARGV[0]}))
  # echo ${BASH_ARGV[0]}
fi

TRUNKPATH=${THISPATH%"/analysis/Zee"}

echo "path to this script:" $THISPATH
export PYTHONPATH=$TRUNKPATH:$PYTHONPATH
export PYTHONPATH=$THISPATH:$PYTHONPATH

# define where to look for the atlas style macro
export ATLAS_STYLE_MACRO=$TRUNKPATH/plotting/atlasstyle/AtlasStyle.C
