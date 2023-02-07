import math
from abc import ABC
from typing import Union, Callable, List

import ee

from . import cfg

def mask_l8_sr(element: ee.Image):
    qa_mask = element.select('QA_PIXEL').bitwiseAnd(int('11111', 2)).eq(0)
    saturation_mask = element.select('QA_RADSAT').eq(0)
    optical_bands = element.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermal_bands = element.select('ST_B.*').multiply(0.00341802).add(149.0)
    
    return element.addBands(optical_bands, None, True)\
        .addBands(thermal_bands, None, True)\
        .updateMask(qa_mask)\
        .updateMask(saturation_mask)

def add_ndvi(red: str = 'SR_B5', nir: str = 'SR_B6') -> Callable:
    def wrapper(element: ee.Image):
        return element.addBands(element.normalizeDifference([red, nir]))\
            .rename('NDVI').float()
    return wrapper

def add_constant(element: ee.Image):
    return element.addBands(ee.Image(1))

def add_time(omega: float = 1.5) -> Callable:
        def add_time_inner(image: ee.Image):
            date = image.date()
            years = date.difference(ee.Date('1970-01-01'), 'year')
            time_radians = ee.Image(years.multiply((2 * omega) * math.pi))
            return image.addBands(time_radians.rename('t').float())
        return add_time_inner

def add_harmonics(freq: List[int], cos_names: List[str], sin_names: List[str]) -> Callable:    
    def add_harmonics_wrapper(element: ee.Image):
        frequencies = ee.Image.constant(freq)
        time = ee.Image(element).select('t')
        cosines = time.multiply(frequencies).cos().rename(cos_names)
        sines = time.multiply(frequencies).sin().rename(sin_names)
        return element.addBands(cosines).addBands(sines)
    return add_harmonics_wrapper

def landsat8(roi: Union[ee.Geometry, ee.FeatureCollection]) -> ee.ImageCollection:
    ASSET_ID: str = "LANDSAT/LC08/C02/T1_L2"
    instance = ee.ImageCollection(ASSET_ID).filterBounds(roi).map(mask_l8_sr)
    return instance


class HarmonicsCollection:
    
    def __new__(cls, img_col: ee.ImageCollection, config: cfg.HarmonicCFG) -> ee.ImageCollection:
        omega = config.omega
        freqs = config.harmonic_freq
        cos_names = config.cos_names
        sin_names = config.sin_names
        
        return img_col.map(add_ndvi).map(add_constant).map(add_time(omega=omega))\
            .map(add_harmonics(freq=freqs, cos_names=cos_names, sin_names=sin_names))
