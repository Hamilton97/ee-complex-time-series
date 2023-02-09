import os 

from enum import Enum

import ee

import harmonics as harm
from cfg import HarmonicCFG
from inputs import InputCollection


def main():
    
    OMEGA = 1.5
    
    roi = ee.Geometry.Point([-122.02331933139578, 54.618262087662735])
    key = 'l8'
    
    preped: ee.ImageCollection = InputCollection(
        cType=key,
        roi=roi,
        omega=OMEGA
    )
    
    cfg = HarmonicCFG()
    
    # add harmonics to the collection and update config
    cfg.collection = preped.map(harm.add_harmonics(
        freq=cfg.harmonic_freq,
        cos_names=cfg.cos_names,
        sin_names=cfg.sin_names
    ))

    harmonics = harm.HarmonicRegression(
        config=cfg
    )
    

if __name__ == '__main__':
    ee.Initialize()
    main()