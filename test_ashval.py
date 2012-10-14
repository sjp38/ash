#!/usr/bin/env python

import unittest

import ashval
import data

class TestAshval(unittest.TestCase):
    def setUp(self):
        print "test ashval start..."

    def tearDown(self):
        print "tear down..."

    def test_raw_ashval(self):
        question = "click [100 200]"
        right_answer = ["click", ["100", "200"]]
        self.assertEqual(ashval.ashval(question), right_answer)

        question = "test [100 [100 200] [ [100 200] 300] [400]] [ [200] ]"
        right_answer = ["test", ["100", ["100", "200"],
            [["100", "200"], "300"], ["400"]], [["200"]]]
        self.assertEqual(ashval.ashval(question), right_answer)

    def test_get_code(self):
        f = ashval._get_code(["arg"])
        self.assertTrue(f and hasattr(f, '__call__'))

    def test_ashval_function(self):
        data.add_callback("", "alias", "c",
                [
                    ["_mock_function",
                        ["arg", "1"], ["arg", "2"], ["arg", "3"]]
                ])
        self.assertEqual(ashval.ashval("c 100 200 300"),
                "_mock_function : 100, 200, 300")
        self.assertEqual(ashval.ashval("c 110 0 350"),
                "_mock_function : 110, 0, 350")

        data.add_callback("", "alias", "d",
                [
                    ["_mock_function",
                        ["arg", "1"], ["arg", "2"], ["arg", "3"]],
                    ["_mock_function",
                        ["arg", "2"], ["arg", "3"], ["arg", "1"]]
                ])
        self.assertEqual(ashval.ashval("d 100 200 300"),
                "_mock_function : 200, 300, 100")
        self.assertEqual(ashval.ashval("d 110 0 350"),
                "_mock_function : 0, 350, 110")

        data.add_callback("", "alias", "d",
                [
                    ["_mock_function",
                        ["arg", "1"], ["arg", "2"], ["arg", "3"]],
                    ["c",
                        ["arg", "2"], ["arg", "3"], ["arg", "1"]]
                ])
        print data._callbacks[data.DEFAULT_EVENT_MODE]["alias"]
        self.assertEqual(ashval.ashval("d 100 200 300"),
                "_mock_function : 200, 300, 100")
        self.assertEqual(ashval.ashval("d 110 0 350"),
                "_mock_function : 0, 350, 110")

        self.assertTrue(ashval.ashval("a b c [[d] [e]]"))
        self.assertTrue(ashval.ashval("_mock_function [[d] [e]] f g"))

    def test_record(self):
        data.add_callback("", "alias", "c",
                [
                    ["_mock_function",
                        ["arg", "1"], ["arg", "2"], ["arg", "3"]]
                ])

        ashval.ashval("record abc")
        ashval.ashval("c 100 200 300")
        ashval.ashval("c 200 200 300")
        ashval.ashval("c 100 200 300")
        ashval.ashval("record_stop")
        self.assertEqual(ashval.ashval("abc"),
                "_mock_function : 100, 200, 300")


    def test_event(self):
        data.clear()
        data.add_callback("", "typeB", "valueC",
                [
                    ["_mock_function",
                        ["arg", "1"], ["arg", "2"], ["arg", "3"]]
                ])
        self.assertEqual(ashval.ashval("event default typeB valueC 10 20 33"),
                "_mock_function : 10, 20, 33")
