import math
from dataclasses import dataclass, InitVar, field
from typing import List

import ee


@dataclass
class ModelCfg:
    time_seies_collection: ee.ImageCollection # TODO create custom obj for TS img
    independent: List = field(default_factory = lambda: ['constant', 't'])
    dependent: str = field(default='NDVI')
    harmonics: int = 3
    omega: int = 1.5
    
    def __post_init__(self):
        self.harmonic_freq = range(1, self.harmonics + 1)
        self.cos_hs = [f'cos_{h}' for h in self.harmonic_freq]
        self.sin_hs = [f'sin_{h}' for h in self.harmonic_freq]
        self.independent = [*self.independent, *self.cos_hs, *self.sin_hs]


class HarmonicsImage:

    @staticmethod
    def add_harmonics(freqs: List[str], cos_names: List[str], sin_names: List[str]):
        def add_inner(image: ee.Image):
            frequencies = ee.Image.constant(freqs)
            time = ee.Image(image).select('t')
            cosines = time.multiply(frequencies).cos().rename(cos_names)
            sines = time.multiply(frequencies).sin().rename(sin_names)
            return image.addBands(cosines).addBands(sines)
        return add_inner
    
    def __init__(self, cfg: ModelCfg) -> None:
        self._CFG = cfg

        self._harmonics_image = cfg.time_seies_collection\
            .map(self.add_harmonics(
                freqs=cfg.harmonic_freq,
                cos_names=cfg.cos_hs,
                sin_names=cfg.sin_hs
            ))
        
        harmonic_trend = self._harmonics_image.select([*cfg.independent, *cfg.dependent]).\
            reduce(**{
                'numX': len(cfg.independent),
                'numY': cfg.omega
            })
        
        self._harmonic_coeff = harmonic_trend.select('coefficients').\
            arrayProject([0]).\
            arrayFlatten([cfg.independent])
    
    @property
    def phase(self) -> ee.Image:
        def mk_phase_inner(numerator: str, denominator: str) -> ee.Image:
            return self._harmonic_coeff.select(numerator).atan(self._harmonic_coeff.\
                select(denominator)).unitScale(-math.pi, math.pi)
        return ee.Image.cat(*[mk_phase_inner(x,y) for x,y in zip(self._CFG.sin_hs, 
                                                                 self._CFG.cos_hs)])
    
    @property
    def ampltiude(self) -> ee.Image:
        
        def mk_amp_inner(numerator, denominator) -> ee.Image:
            return self._harmonic_coeff.select(numerator)\
                .hypot(self._harmonic_coeff.select(denominator))
        
        return ee.Image.cat(*[mk_amp_inner(x,y) for x,y in zip(self._CFG.sin_hs, 
                                                                self._CFG.cos_hs)])
    
    @property
    def mean_dependent(self) -> ee.Image:
        return self._CFG.time_seies_collection.select(self._CFG.dependent).mean()
    
    
    def fit_harmonics(self) -> None:
        def fit_inner(element: ee.Image):
            return element.addBands(element.select(self._CFG.independent).\
                multiply(self._harmonic_coeff).\
                reduce('sum').\
                rename('fitted')
            )
    
        return self._harmonics_image.map(fit_inner)
        
    