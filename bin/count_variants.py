#!/usr/bin/python3
#
#
#
#
# Adriana Toutoudaki (August 2019)
# contact: adriana.toutoudaki@addenbrookes.nhs.uk

#!/usr/bin/python3
#
#
#
#
# Adriana Toutoudaki (August 2019)
# contact: adriana.toutoudaki@addenbrookes.nhs.uk

import argparse
import csv
#from datetime import datetime
from base import DBSession,engine,Base
from models import Sample,Analysis,Variant,AnalysisVariant,Panel,Gene,GenePanel,Transcript,SamplePanel
from sqlalchemy import (or_,and_,exists)