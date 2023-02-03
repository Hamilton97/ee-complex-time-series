from abc import ABC
import ee


def add_variables(image: ee.Image):
    date = image.date()
    years = date.difference(ee.Date('1970-01-01'), 'year')
    return image.addBands(ee.Image(years).rename('t')).float()\
        .addBands(ee.Image.constant(1))
        

class LandSat8SR:

    def __new__(cls, ) -> ee.ImageCollection:
        pass