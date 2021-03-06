"""
Copyright (c) 2016 Jet Propulsion Laboratory,
California Institute of Technology.  All rights reserved
"""
import unittest
from os import path

import numpy as np
from nexusproto.serialization import from_shaped_array
from nexusproto import NexusContent_pb2 as nexusproto

import processors


class TestReadMurData(unittest.TestCase):
    def setUp(self):
        self.module = processors.GridReadingProcessor('analysed_sst', 'lat', 'lon', time='time')

    def test_read_empty_mur(self):
        test_file = path.join(path.dirname(__file__), 'datafiles', 'empty_mur.nc4')

        input_tile = nexusproto.NexusTile()
        tile_summary = nexusproto.TileSummary()
        tile_summary.granule = "file:%s" % test_file
        tile_summary.section_spec = "time:0:1,lat:0:10,lon:0:10"
        input_tile.summary.CopyFrom(tile_summary)

        results = list(self.module.process(input_tile))

        self.assertEqual(1, len(results))

        for nexus_tile in results:
            self.assertTrue(nexus_tile.HasField('tile'))
            self.assertTrue(nexus_tile.tile.HasField('grid_tile'))

            tile = nexus_tile.tile.grid_tile
            self.assertEqual(10, len(from_shaped_array(tile.latitude)))
            self.assertEqual(10, len(from_shaped_array(tile.longitude)))

            the_data = np.ma.masked_invalid(from_shaped_array(tile.variable_data))
            self.assertEqual((1, 10, 10), the_data.shape)
            self.assertEqual(0, np.ma.count(the_data))
            self.assertTrue(tile.HasField('time'))

    def test_read_not_empty_mur(self):
        test_file = path.join(path.dirname(__file__), 'datafiles', 'not_empty_mur.nc4')

        input_tile = nexusproto.NexusTile()
        tile_summary = nexusproto.TileSummary()
        tile_summary.granule = "file:%s" % test_file
        tile_summary.section_spec = "time:0:1,lat:0:10,lon:0:10"
        input_tile.summary.CopyFrom(tile_summary)

        results = list(self.module.process(input_tile))

        self.assertEqual(1, len(results))

        tile1_data = np.ma.masked_invalid(from_shaped_array(results[0].tile.grid_tile.variable_data))
        self.assertEqual((1, 10, 10), tile1_data.shape)
        self.assertEqual(100, np.ma.count(tile1_data))


class TestReadAscatbData(unittest.TestCase):
    # for data in read_swath_data(None,
    #                       "NUMROWS:0:1,NUMCELLS:0:5;NUMROWS:1:2,NUMCELLS:0:5;file:///Users/greguska/data/ascat/ascat_20130314_004801_metopb_02520_eps_o_coa_2101_ovw.l2.nc"):
    #     import sys
    #     from struct import pack
    #     sys.stdout.write(pack("!L", len(data)) + data)

    # VARIABLE=wind_speed,LATITUDE=lat,LONGITUDE=lon,TIME=time,META=wind_dir,READER=SWATHTILE,TEMP_DIR=/tmp
    def test_read_not_empty_ascatb(self):
        test_file = path.join(path.dirname(__file__), 'datafiles', 'not_empty_ascatb.nc4')

        swath_reader = processors.SwathReadingProcessor('wind_speed', 'lat', 'lon', time='time')

        input_tile = nexusproto.NexusTile()
        tile_summary = nexusproto.TileSummary()
        tile_summary.granule = "file:%s" % test_file
        tile_summary.section_spec = "NUMROWS:0:1,NUMCELLS:0:82"
        input_tile.summary.CopyFrom(tile_summary)

        results = list(swath_reader.process(input_tile))

        self.assertEqual(1, len(results))

        for nexus_tile in results:
            self.assertTrue(nexus_tile.HasField('tile'))
            self.assertTrue(nexus_tile.tile.HasField('swath_tile'))
            self.assertEqual(0, len(nexus_tile.tile.swath_tile.meta_data))

            tile = nexus_tile.tile.swath_tile
            self.assertEqual(82, from_shaped_array(tile.latitude).size)
            self.assertEqual(82, from_shaped_array(tile.longitude).size)

        tile1_data = np.ma.masked_invalid(from_shaped_array(results[0].tile.swath_tile.variable_data))
        self.assertEqual((1, 82), tile1_data.shape)
        self.assertEqual(82, np.ma.count(tile1_data))

    def test_read_not_empty_ascatb_meta(self):
        # with open('./ascat_longitude_more_than_180.bin', 'w') as f:
        #     results = list(self.module.read_swath_data(None,
        #                                                "NUMROWS:0:1,NUMCELLS:0:82;NUMROWS:1:2,NUMCELLS:0:82;file:///Users/greguska/Downloads/ascat_longitude_more_than_180.nc4"))
        #     f.write(results[0])

        test_file = path.join(path.dirname(__file__), 'datafiles', 'not_empty_ascatb.nc4')

        swath_reader = processors.SwathReadingProcessor('wind_speed', 'lat', 'lon', time='time', meta='wind_dir')

        input_tile = nexusproto.NexusTile()
        tile_summary = nexusproto.TileSummary()
        tile_summary.granule = "file:%s" % test_file
        tile_summary.section_spec = "NUMROWS:0:1,NUMCELLS:0:82"
        input_tile.summary.CopyFrom(tile_summary)

        results = list(swath_reader.process(input_tile))

        self.assertEqual(1, len(results))

        for nexus_tile in results:
            self.assertTrue(nexus_tile.HasField('tile'))
            self.assertTrue(nexus_tile.tile.HasField('swath_tile'))
            self.assertLess(0, len(nexus_tile.tile.swath_tile.meta_data))

        self.assertEqual(1, len(results[0].tile.swath_tile.meta_data))
        tile1_meta_data = np.ma.masked_invalid(from_shaped_array(results[0].tile.swath_tile.meta_data[0].meta_data))
        self.assertEqual((1, 82), tile1_meta_data.shape)
        self.assertEqual(82, np.ma.count(tile1_meta_data))


class TestReadSmapData(unittest.TestCase):
    def test_read_not_empty_smap(self):
        test_file = path.join(path.dirname(__file__), 'datafiles', 'not_empty_smap.h5')

        swath_reader = processors.SwathReadingProcessor('smap_sss', 'lat', 'lon',
                                                        time='row_time',
                                                        glblattr_day='REV_START_TIME',
                                                        glblattr_day_format='%Y-%jT%H:%M:%S.%f')

        input_tile = nexusproto.NexusTile()
        tile_summary = nexusproto.TileSummary()
        tile_summary.granule = "file:%s" % test_file
        tile_summary.section_spec = "phony_dim_0:0:76,phony_dim_1:0:1"
        input_tile.summary.CopyFrom(tile_summary)

        results = list(swath_reader.process(input_tile))

        self.assertEqual(1, len(results))

        # with open('./smap_nonempty_nexustile.bin', 'w') as f:
        #     f.write(results[0])

        for nexus_tile in results:
            self.assertTrue(nexus_tile.HasField('tile'))
            self.assertTrue(nexus_tile.tile.HasField('swath_tile'))
            self.assertEqual(0, len(nexus_tile.tile.swath_tile.meta_data))

            tile = nexus_tile.tile.swath_tile
            self.assertEqual(76, from_shaped_array(tile.latitude).size)
            self.assertEqual(76, from_shaped_array(tile.longitude).size)

        tile1_data = np.ma.masked_invalid(from_shaped_array(results[0].tile.swath_tile.variable_data))
        self.assertEqual((76, 1), tile1_data.shape)
        self.assertEqual(43, np.ma.count(tile1_data))
        self.assertAlmostEqual(-50.056,
                               np.ma.min(np.ma.masked_invalid(from_shaped_array(results[0].tile.swath_tile.latitude))),
                               places=3)
        self.assertAlmostEqual(-47.949,
                               np.ma.max(np.ma.masked_invalid(from_shaped_array(results[0].tile.swath_tile.latitude))),
                               places=3)

        self.assertEqual(1427820162, np.ma.masked_invalid(from_shaped_array(results[0].tile.swath_tile.time))[0])


class TestReadCcmpData(unittest.TestCase):

    def test_read_not_empty_ccmp(self):
        test_file = path.join(path.dirname(__file__), 'datafiles', 'not_empty_ccmp.nc')

        ccmp_reader = processors.GridReadingProcessor('uwnd', 'latitude', 'longitude', time='time', meta='vwnd')

        input_tile = nexusproto.NexusTile()
        tile_summary = nexusproto.TileSummary()
        tile_summary.granule = "file:%s" % test_file
        tile_summary.section_spec = "time:0:1,longitude:0:87,latitude:0:38"
        input_tile.summary.CopyFrom(tile_summary)

        results = list(ccmp_reader.process(input_tile))

        self.assertEqual(1, len(results))

        # with open('./ccmp_nonempty_nexustile.bin', 'w') as f:
        #     f.write(results[0])

        for nexus_tile in results:
            self.assertTrue(nexus_tile.HasField('tile'))
            self.assertTrue(nexus_tile.tile.HasField('grid_tile'))
            self.assertEqual(1, len(nexus_tile.tile.grid_tile.meta_data))

            tile = nexus_tile.tile.grid_tile
            self.assertEqual(38, from_shaped_array(tile.latitude).size)
            self.assertEqual(87, from_shaped_array(tile.longitude).size)
            self.assertEqual((1, 38, 87), from_shaped_array(tile.variable_data).shape)

        tile1_data = np.ma.masked_invalid(from_shaped_array(results[0].tile.grid_tile.variable_data))
        self.assertEqual(3306, np.ma.count(tile1_data))
        self.assertAlmostEqual(-78.375,
                               np.ma.min(np.ma.masked_invalid(from_shaped_array(results[0].tile.grid_tile.latitude))),
                               places=3)
        self.assertAlmostEqual(-69.125,
                               np.ma.max(np.ma.masked_invalid(from_shaped_array(results[0].tile.grid_tile.latitude))),
                               places=3)

        self.assertEqual(1451606400, results[0].tile.grid_tile.time)


class TestReadAvhrrData(unittest.TestCase):
    def test_read_not_empty_avhrr(self):
        test_file = path.join(path.dirname(__file__), 'datafiles', 'not_empty_avhrr.nc4')

        avhrr_reader = processors.GridReadingProcessor('analysed_sst', 'lat', 'lon', time='time')

        input_tile = nexusproto.NexusTile()
        tile_summary = nexusproto.TileSummary()
        tile_summary.granule = "file:%s" % test_file
        tile_summary.section_spec = "time:0:1,lat:0:10,lon:0:10"
        input_tile.summary.CopyFrom(tile_summary)

        results = list(avhrr_reader.process(input_tile))

        self.assertEqual(1, len(results))

        for nexus_tile in results:
            self.assertTrue(nexus_tile.HasField('tile'))
            self.assertTrue(nexus_tile.tile.HasField('grid_tile'))

            tile = nexus_tile.tile.grid_tile
            self.assertEqual(10, from_shaped_array(tile.latitude).size)
            self.assertEqual(10, from_shaped_array(tile.longitude).size)
            self.assertEqual((1, 10, 10), from_shaped_array(tile.variable_data).shape)

        tile1_data = np.ma.masked_invalid(from_shaped_array(results[0].tile.grid_tile.variable_data))
        self.assertEqual(100, np.ma.count(tile1_data))
        self.assertAlmostEqual(-39.875,
                               np.ma.min(np.ma.masked_invalid(from_shaped_array(results[0].tile.grid_tile.latitude))),
                               places=3)
        self.assertAlmostEqual(-37.625,
                               np.ma.max(np.ma.masked_invalid(from_shaped_array(results[0].tile.grid_tile.latitude))),
                               places=3)

        self.assertEqual(1462060800, results[0].tile.grid_tile.time)
        self.assertAlmostEqual(289.71,
                               np.ma.masked_invalid(from_shaped_array(results[0].tile.grid_tile.variable_data))[
                                   0, 0, 0],
                               places=3)


class TestReadWSWMData(unittest.TestCase):

    def test_read_not_empty_wswm(self):
        test_file = path.join(path.dirname(__file__), 'datafiles', 'not_empty_wswm.nc')

        wswm_reader = processors.TimeSeriesReadingProcessor('Qout', 'lat', 'lon', 'time')

        input_tile = nexusproto.NexusTile()
        tile_summary = nexusproto.TileSummary()
        tile_summary.granule = "file:%s" % test_file
        tile_summary.section_spec = "time:0:1,rivid:0:500"
        input_tile.summary.CopyFrom(tile_summary)

        results = list(wswm_reader.process(input_tile))

        self.assertEqual(1, len(results))

        for nexus_tile in results:
            self.assertTrue(nexus_tile.HasField('tile'))
            self.assertTrue(nexus_tile.tile.HasField('time_series_tile'))

            tile = nexus_tile.tile.time_series_tile
            self.assertEqual(500, from_shaped_array(tile.latitude).size)
            self.assertEqual(500, from_shaped_array(tile.longitude).size)
            self.assertEqual((1, 500), from_shaped_array(tile.variable_data).shape)

        tile1_data = np.ma.masked_invalid(from_shaped_array(results[0].tile.time_series_tile.variable_data))
        self.assertEqual(500, np.ma.count(tile1_data))
        self.assertAlmostEqual(41.390,
                               np.ma.min(
                                   np.ma.masked_invalid(from_shaped_array(results[0].tile.time_series_tile.latitude))),
                               places=3)
        self.assertAlmostEqual(42.071,
                               np.ma.max(
                                   np.ma.masked_invalid(from_shaped_array(results[0].tile.time_series_tile.latitude))),
                               places=3)

        self.assertEqual(852098400, results[0].tile.time_series_tile.time)
        self.assertAlmostEqual(0.009,
                               np.ma.masked_invalid(from_shaped_array(results[0].tile.time_series_tile.variable_data))[
                                   0, 0],
                               places=3)


if __name__ == '__main__':
    unittest.main()
