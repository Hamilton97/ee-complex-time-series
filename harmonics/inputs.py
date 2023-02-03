from abc import ABC
from typing import Union
import ee



class LandSAT8SR(ee.ImageCollection):

    ASSET_ID = "LANDSAT/LC08/C02/T1_L2"
    
    def __new__(cls, viewport: Union[ee.FeatureCollection, ee.Geometry]) -> ee.ImageCollection:
        instance = ee.ImageCollection(cls.ASSET_ID)
        return instance.filterBounds(viewport)\
            .map(cls.mask_l8_sr)\
            .map(cls.add_variables)
    
    @classmethod
    def mask_l8_sr(cls):
        
        def mask_inner(element: ee.Image):
            qa_mask = element.select('QA_PIXEL').bitwiseAnd(int('11111', 2)).eq(0)
            saturation_mask = element.select('QA_RADSAT').eq(0)
            optical_bands = element.select('SR_B.').multiply(0.0000275).add(-0.2)
            thermal_bands = element.select('ST_B.*').multiply(0.00341802).add(149.0)
            
            return element.addBands(optical_bands, None, True)\
                .addBands(thermal_bands, None, True)\
                .updateMask(qa_mask)\
                .updateMask(saturation_mask)

        return cls.map(mask_inner)
    
    @classmethod
    def add_variables(cls):

        def add_variables_inner(image: ee.Image):
            date = image.date()
            years = date.difference(ee.Date('1970-01-01'), 'year')
            return image.addBands(ee.Image(years).rename('t')).float()\
                .addBands(image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI'))\
                .addBands(ee.Image.constant(1))
        
        return cls.map(add_variables_inner)
