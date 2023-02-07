import math
from typing import List

import ee

from . import cfg
from . import inputs


class HarmonicRegression:

   
    def __init__(self, harmonics_image: inputs.HarmonicsCollection, config: cfg.HarmonicCFG) -> None:
        self.config = config
        self.harmonics_image = harmonics_image
        self.harmonic_trend = self.harmonics_image.select([*self.config.independents, 
                                                           self.config.dependend]).\
            reduce(ee.Reducer.linearRegression(**{
                'numX': len(self.config.independents),
                'numY': 1
            }))
        
        self.harmonic_coeff = self.harmonic_trend.select('coefficients').\
            arrayProject([0]).\
            arrayFlatten([self.config.independents])

    @property
    def phase(self) -> ee.Image:
        def mk_phase_inner(numerator: str, denominator: str) -> ee.Image:
            return self._harmonic_coeff.select(numerator).atan(self._harmonic_coeff.\
                select(denominator)).unitScale(-math.pi, math.pi)
        return ee.Image.cat(*[mk_phase_inner(x,y) for x,y in zip(self.config.sin_names, 
                                                                 self.config.cos_names)])
    
    @property
    def ampltiude(self) -> ee.Image:
        
        def mk_amp_inner(numerator, denominator) -> ee.Image:
            return self._harmonic_coeff.select(numerator)\
                .hypot(self._harmonic_coeff.select(denominator))
        
        return ee.Image.cat(*[mk_amp_inner(x,y) for x,y in zip(self.config.sin_names, 
                                                                self.config.cos_names)])
    
    @property
    def mean_dependent(self) -> ee.Image:
        return self.harmonics_image.select(self.config.dependend).mean()
    
    def fit_harmonics(self) -> None:
        def fit_inner(element: ee.Image):
            return element.addBands(element.select(self.config.dependent).\
                multiply(self.harmonic_coeff).\
                reduce('sum').\
                rename('fitted')
            )
    
        return self._harmonics_image.map(fit_inner)
        
    