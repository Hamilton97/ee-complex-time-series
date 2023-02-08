from __future__ import annotations

import math
from abc import ABC, abstractstaticmethod
from dataclasses import dataclass, field, InitVar
from typing import Union, Callable, List

import ee


def add_ndvi(red: str, nir: str ) -> Callable:
    def wrapper(element: ee.Image):
        equation = '(NIR - RED) / (NIR + RED)'
        calc = element.expression(
            expression=equation,
            opt_map={'NIR': nir, 'RED': red}
        ).rename('NDVI').float()
        return element.addBands(calc)
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


class InputCollection:
    
    def __new__(cls, cType: str, roi: Union[ee.Geometry, ee.FeatureCollection], omega: int = 1.5):
        _cKeyword = {
            'l8': LandSAT8,
            'S2_SR': Sentinel2SR,
            'S2_TOA': Sentinel2TOA
        }
        
        cfg: _BaseData = _cKeyword.get(cType, None)
        
        
        if cfg is None:
            raise KeyError(f"{cType} not at valid Key must be: {_cKeyword.keys()}")
        
        instance = ee.ImageCollection(cfg.ASSET_ID).filterBounds(roi).filterDate('2017', '2021')\
            .map(cfg.cloud_mask).map(add_ndvi(red=cfg.RED, nir=cfg.NIR)).map(add_time(omega=omega))\
                .map(add_constant)

        return instance
        

@dataclass
class _BaseData(ABC):
    ASSET_ID: str = field(default=None)
    NIR: str = field(default=None)
    RED: str = field(default=None)
    
    @abstractstaticmethod
    def cloud_mask(element):
        pass


@dataclass(frozen=True)
class LandSAT8(_BaseData):
    ASSET_ID: str = field(default="LANDSAT/LC08/C02/T1_L2")
    NIR: str = field(default='SR_B6')
    RED: str = field(default='SR_B5') 
    
    @staticmethod
    def cloud_mask(element: ee.Image):
        qa_mask = element.select('QA_PIXEL').bitwiseAnd(int('11111', 2)).eq(0)
        saturation_mask = element.select('QA_RADSAT').eq(0)
        optical_bands = element.select('SR_B.').multiply(0.0000275).add(-0.2)
        thermal_bands = element.select('ST_B.*').multiply(0.00341802).add(149.0)

        return element.addBands(optical_bands, None, True)\
            .addBands(thermal_bands, None, True)\
            .updateMask(qa_mask)\
            .updateMask(saturation_mask)


@dataclass(frozen=True)
class Sentinel2TOA(_BaseData):
    ASSET_ID: str =field(default="COPERNICUS/S2_HARMONIZED") 
    NIR: str = field(default="B8")
    RED: str = field(default="B4")
    
    @staticmethod
    def cloud_mask(element: ee.Image):
        qa = element.select('QA60')
        cloudBitMask = 1 << 10
        cirrusBitMask = 1 << 11
        mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))
        return element.updateMask(mask)


@dataclass(frozen=True)
class Sentinel2SR(_BaseData):
    ASSET_ID: str =field(default="COPERNICUS/S2_SR_HARMONIZED") 
    NIR: str = field(default="B8")
    RED: str = field(default="B4")
    
    @staticmethod
    def cloud_mask(element: ee.Image):
        qa = element.select('QA60')
        cloudBitMask = 1 << 10
        cirrusBitMask = 1 << 11
        mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))
        return element.updateMask(mask)
