from dataclasses import dataclass, field

import ee

@dataclass
class HarmonicCFG:
    dependend: str = field(default='NDVI')
    independents: list = field(default_factory= lambda: ['constant', 't'])
    harmonics: int = 2
    omega: float = 1.5
    red: str = field(default="")
    nir: str = field(default="")
    
    def __post_init__(self):
        self.harmonic_freq = list(range(1, self.harmonics + 1))
        self.cos_names = [f'cos_{ _ }' for _ in self.harmonic_freq]
        self.sin_names = [f'sin_{ _ }' for _ in self.harmonic_freq]
        self.independents = [*self.independents, *self.cos_names, *self.sin_names]
    