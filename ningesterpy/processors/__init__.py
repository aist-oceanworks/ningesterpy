"""
Copyright (c) 2017 Jet Propulsion Laboratory,
California Institute of Technology.  All rights reserved
"""
from collections import defaultdict

import nexusproto.NexusContent_pb2 as nexusproto


class Processor(object):
    def __init__(self, *args, **kwargs):
        self.environ = defaultdict(lambda: None)
        for k, v in kwargs.items():
            self.environ[k.upper()] = v
        pass

    def process(self, input_data):
        raise NotImplementedError


class NexusTileProcessor(Processor):
    @staticmethod
    def parse_input(input_data):
        if isinstance(input_data, nexusproto.NexusTile):
            return input_data
        else:
            return nexusproto.NexusTile.FromString(input_data)

    def process(self, input_data):
        nexus_tile = self.parse_input(input_data)

        for data in self.process_nexus_tile(nexus_tile):
            yield data

    def process_nexus_tile(self, nexus_tile):
        raise NotImplementedError


# All installed processors need to be imported and added to the dict below

from processors.callncpdq import CallNcpdq
from processors.callncra import CallNcra
from processors.computespeeddirfromuv import ComputeSpeedDirFromUV
from processors.emptytilefilter import EmptyTileFilter
from processors.kelvintocelsius import KelvinToCelsius
from processors.normalizetimebeginningofmonth import NormalizeTimeBeginningOfMonth
from processors.regrid1x1 import Regrid1x1
from processors.subtract180longitude import Subtract180Longitude
from processors.tilereadingprocessor import GridReadingProcessor, SwathReadingProcessor, TimeSeriesReadingProcessor
from processors.tilesummarizingprocessor import TileSummarizingProcessor
from processors.winddirspeedtouv import WindDirSpeedToUV

INSTALLED_PROCESSORS = {
    "CallNcpdq": CallNcpdq,
    "CallNcra": CallNcra,
    "ComputeSpeedDirFromUV": ComputeSpeedDirFromUV,
    "EmptyTileFilter": EmptyTileFilter,
    "KelvinToCelsius": KelvinToCelsius,
    "NormalizeTimeBeginningOfMonth": NormalizeTimeBeginningOfMonth,
    "Regrid1x1": Regrid1x1,
    "Subtract180Longitude": Subtract180Longitude,
    "GridReadingProcessor": GridReadingProcessor,
    "SwathReadingProcessor": SwathReadingProcessor,
    "TimeSeriesReadingProcessor": TimeSeriesReadingProcessor,
    "TileSummarizingProcessor": TileSummarizingProcessor,
    "WindDirSpeedToUV": WindDirSpeedToUV
}
