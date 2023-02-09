from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union, Optional

import ee


@dataclass
class CloudTask:
    object: Union[ee.FeatureCollection, ee.Image]
    bucket: str
    desciption: str = field(default="MyExportCloudTask")
    file_name_prefix: str = field(default=None)

    def __post_init__(self):
        pass


@dataclass
class TableCloudTask(CloudTask):
    object: ee.FeatureCollection
    selectors: list  = field(default_factory=list)
    file_format: str = field(default="CSV")

    def __post_init__(self):
        self.tabletask: ee.batch.Task = ee.batch.Export.table.toCloudStorage(
            collection=self.object,
            description=self.desciption,
            selectors=self.selectors,
            fileFormat=self.file_format,
            fileNamePrefix=self.file_name_prefix
        )


@dataclass
class ImageCloudTask(CloudTask):
    object: ee.Image
    scale: Optional[int] = field(default=None)
    region: Optional[ee.Geometry] = None
    file_dim: Optional[list[int]] = field(default=None)
    shard_size: int = field(default=256)
    crs: str = field(default="EPSG:4326")
    
    def __post_init__(self):
        self.imagetask: ee.batch.Task = ee.batch.Export.image.toCloudStorage(
            image=self.object,
            description=self.desciption,
            bucket=self.bucket,
            fileNamePrefix=self.file_name_prefix,
            fileDimensions=self.file_dim,
            fileFormat='GeoTIFF',
            shardSize=self.shard_size,
            scale=self.scale,
            crs=self.crs
        )


class CloudTaskQue:
    
    def __init__(self) -> None:
        self._que: list[ee.batch.Task] = []
    
    def __len__(self) -> int:
        return len(self._que)

    def __getitem__(self, __idx):
        return self._que[__idx]
    
    def __setitem__(self, idx, value):
        self._que[idx] = value
    
    def append(self, __obj):
        self._que.append(__obj)


def export2cloud(que: CloudTaskQue) -> None:
    for task in CloudTaskQue:
        task.start()
    return None