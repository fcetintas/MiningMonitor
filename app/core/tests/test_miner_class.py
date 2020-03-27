from django.test import TestCase

from core.miner import Miner
from core.sampleMiner import SampleMiner

import logging

SERVER_IP = '127.0.0.1'
SERVER_PORT = 3333

MINER_DATA = {'version': '9.3 - ETH',  # miner version.
              'running_time': 21,  # running time, in minutes.
              'hashrate': {
                           'hashrate': 182724,
                           'shr': 51,
                           'rejshr': 0
                           },
              'gpus': [
                       {'hashrate': 30502, 'tmp': 53, 'fan': 71},
                       {'hashrate': 30457, 'tmp': 57, 'fan': 67},
                       {'hashrate': 30297, 'tmp': 61, 'fan': 72},
                       {'hashrate': 30481, 'tmp': 55, 'fan': 70},
                       {'hashrate': 30479, 'tmp': 59, 'fan': 71},
                       {'hashrate': 30505, 'tmp': 61, 'fan': 70}
                       ],
              'pool': 'eth-eu1.nanopool.org:9999'
              }


class TestMiner(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = logging.getLogger(__name__)
        cls.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        _ = '%(asctime)s | %(levelname)s | %(module)s | %(message)s'
        formatter = logging.Formatter(_)
        handler.setFormatter(formatter)
        cls.logger.addHandler(handler)

        cls._connection = SampleMiner(host='0.0.0.0',
                                      port=3333,
                                      logger=cls.logger)
        cls._connection.start()

    @classmethod
    def tearDownClass(cls):
        cls._connection.stop()
        cls._connection.join()

    def test_is_active_property_working_server(self):
        """Test if is_active function working properly
        while server running"""
        miner = Miner(ip=SERVER_IP, port=SERVER_PORT, logger=self.logger)
        result = miner.check_connection()
        self.assertTrue(result)

    def test_is_active_property_not_working_server(self):
        """Test is is_active function working properly
        while server not running"""
        miner = Miner(ip=SERVER_IP, port=3334, logger=self.logger)
        result = miner.check_connection()
        self.assertFalse(result)

    def test_get_data(self):
        """Test if miner retrieve data appropriately"""
        miner = Miner(ip=SERVER_IP, port=SERVER_PORT, logger=self.logger)
        result = miner.get_data()
        self.assertEqual(result, MINER_DATA)
