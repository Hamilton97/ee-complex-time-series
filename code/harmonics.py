import math
from typing import Callable, List, Iterable

import ee

import cfg


def add_harmonics(freq: List[int], cos_names: List[str], sin_names: List[str]) -> Callable:    
    def add_harmonics_wrapper(element: ee.Image):
        frequencies = ee.Image.constant(freq)
        time = ee.Image(element).select('t')
        cosines = time.multiply(frequencies).cos().rename(cos_names)
        sines = time.multiply(frequencies).sin().rename(sin_names)
        return element.addBands(cosines).addBands(sines)
    return add_harmonics_wrapper


class HarmonicsStack:
    
    def __new__(cls, *images: Iterable[ee.Image]) -> ee.Image:
        """Creates a new Image that contains the Harmoic Coeffiecient Image, as well as
        phase and apmlitude 

        Returns:
            ee.Image: a image that has been concatinated together
        """
        return ee.Image.cat(*images).float()



class HarmonicRegression:

   
    def __init__(self, config: cfg.HarmonicCFG) -> None:
        self.config = config
        self.harmonics_image = config.collection
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
        def mk_phase_inner(b1, b2):
            return self.harmonic_coeff.select(b1).atan2(self.harmonic_coeff.select(b2))\
                .unitScale(-math.pi, math.pi)
        
        stack = ee.Image.cat(*[mk_phase_inner(x,y) for x,y in zip(self.config.sin_names, 
                                                                 self.config.cos_names)])
    
        old_names: ee.List = stack.bandNames()
        new_names = [f'phase_{idx}' for idx, _ in enumerate(self.config.sin_names, start=1)]
        return stack.select(old_names, new_names)

    @property
    def ampltiude(self) -> ee.Image:
        
        def mk_amp_inner(numerator, denominator) -> ee.Image:
            return self.harmonic_coeff.select(numerator)\
                .hypot(self.harmonic_coeff.select(denominator))
        
        stack = ee.Image.cat(*[mk_amp_inner(x,y) for x,y in zip(self.config.sin_names, 
                                                                self.config.cos_names)])
        
        band_names: ee.List = stack.bandNames()
        new_names = [f'amp_{idx}' for idx, _ in enumerate(self.config.sin_names, start=1)]
        return stack.select(band_names, new_names)

    @property
    def mean_dependent(self) -> ee.Image:
        return self.harmonics_image.select(self.config.dependend).mean()\
            .rename(f'{self.config.dependend}_mean')
    
    def fit_harmonics(self) -> ee.ImageCollection:
        def fit_inner(element: ee.Image):
            return element.addBands(element.select(self.config.dependent).\
                multiply(self.harmonic_coeff).\
                reduce('sum').\
                rename('fitted')
            )
    
        return self.harmonics_image.map(fit_inner)
    
    def stack(self) -> HarmonicsStack:
        return HarmonicsStack(self.harmonic_coeff, self.ampltiude, self.phase, self.mean_dependent)
        
    