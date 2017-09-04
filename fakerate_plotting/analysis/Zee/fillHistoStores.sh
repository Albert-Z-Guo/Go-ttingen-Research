cd /home/zuguo/rootcellar/fakerate-plotting/trunk/analysis/Zee
source env.sh
nice python analysis/dataMC.py
nice python analysis/FakeRates.py
nice python analysis/reweighting.py
nice python analysis/Templates.py
nice python analysis/ZeroMatches.py
source cleanPlotDirs.sh
