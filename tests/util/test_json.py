# -*- coding: utf-8 -*-

from datetime import datetime
import unittest

import courseme.util.json as json

class JsonModuleTestCase(unittest.TestCase):

    def test_vanilla_round_trip(self):
        obj = {"number": 123}
        result = json.loads(json.dumps(obj))
        self.assertEqual(result, obj)

    def test_datetime_serialisation(self):
        dt = datetime(2015, 1, 11, 10, 30, 13, 23)
        obj = {"time": dt}
        result = json.loads(json.dumps(obj))
        self.assertEqual(result["time"], dt.isoformat())
