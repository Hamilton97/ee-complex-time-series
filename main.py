import os
import sys

import ee


from code import cfg
from code import inputs

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

def main(args = None):
    years = '2017', '2021'
    
    input_collection = inputs.landsat8(roi=None)\
        .filterDate(*years)
    
    harmonics_col = inputs.HarmonicsCollection(
        img_col = input_collection,
        config = 
    )
       
    model_cfg = cfg.HarmonicCFG(
        
    )


if __name__ == '__main__':
    ee.Initialize()
    os.chdir(CURRENT_DIR)
    main()