from enum import Enum


class S2TOA(Enum):
    B1 = 'Aerosols'
    B2 = 'Blue'
    B3 = 'Green'
    B4 = 'Red'
    B5 = 'Red Edge 1'
    B6 = 'Red Edge 2'
    B7 = 'Red Edge 3'
    B8 = 'NIR'
    B8A = 'Red Edge 4'
    B9 = 'Water vapor'
    B10 = 'Cirrus'
    B11 = 'SWIR 1'
    B12 = 'SWIR 2'


class S2SR(Enum):
    B1 = 'Aerosols'
    B2 = 'Blue'
    B3 = 'Green'
    B4 = 'Red'
    B5 = 'Red Edge 1'
    B6 = 'Red Edge 2'
    B7 = 'Red Edge 3'
    B8 = 'NIR'
    B8A = 'Red Edge 4'
    B11 = 'SWIR 1'
    B12 = 'SWIR 2'


class LS8SR(Enum):
    SR_B1 = 'Ultra Blue'
    SR_B2 = 'Blue'
    SR_B3 = 'Green'
    SR_B4 = 'Red'
    SR_B5 = 'NIR'
    SR_B6 = 'SWIR 1'
    SR_B7 = 'SWIR 2'