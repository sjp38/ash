#!/usr/bin/env python

import unittest

import data

class TestData(unittest.TestCase):
    def setUp(self):
        print "test data start..."

    def tearDown(self):
        print "tear down..."

    def test_load_from_file(self):
        data.load_from_file("data_2.0.xml")
        self.assertEqual(
                data.get_callback("googleKeyboard", "keyboard", "A_DOWN"),
                ["touch", "DOWN_AND_UP", "300", "680"])
        self.assertEqual(
                data.get_callback("default", "alias", "click"),
                [["touch", "DOWN", ["arg", "1"], ["arg", "2"]],
                    ["sleep", "0.1"],
                    ["touch", "UP", ["arg", "1"], ["arg", "2"]]
                    ])

    def test_save_to_file(self):
        data.clear()
        data.load_from_file("data_2.0.xml")
        data.save_to_file("data_2.0_write_test.xml")
        data.clear()
        data.load_from_file("data_2.0_write_test.xml")
        self.assertEqual(
                data.get_callback("googleKeyboard", "keyboard", "A_DOWN"),
                ["touch", "DOWN_AND_UP", "300", "680"])
        self.assertEqual(
                data.get_callback("default", "alias", "click"),
                [["touch", "DOWN", ["arg", "1"], ["arg", "2"]],
                    ["sleep", "0.1"],
                    ["touch", "UP", ["arg", "1"], ["arg", "2"]]
                    ])

    def test_clear(self):
        data.clear()
        data.add_callback("foo", "bar", "bzrrr", ["a", "b", "c"])
        self.assertEqual(data.get_callback("foo", "bar", "bzrrr"),
                ["a", "b", "c"])
        data.clear()
        self.assertEqual(data.get_callback("foo", "bar", "bzrrr"),
                data.NO_CALLBACK)

    def test_add_callback(self):
        data.clear()
        data.add_callback("abc", "def", "VALUE",
                ["weird", "list", "grrr"])
        self.assertEqual(data.get_callback("abc", "def", "VALUE"),
                ["weird", "list", "grrr"])
        data.add_callback("abc", "def", "VALUE",
                ["normal", "new list", "varrr"])
        self.assertEqual(data.get_callback("abc", "def", "VALUE"),
                ["normal", "new list", "varrr"])

        # Add None is equal to remove.
        data.add_callback("abc", "def", "VALUE", None)
        self.assertEqual(data.get_callback("abc", "def", "VALUE"),
                data.NO_CALLBACK)

        data.add_callback("", "abc", "def", [["code1", "arg1"],["code2"]])
        self.assertEqual(data.get_callback(
                data.DEFAULT_EVENT_MODE, "abc", "def"),
                [["code1", "arg1"], ["code2"]])
        data.add_callback("default", "abc", "def",
                [["code1", "arg1"],["code2"]])
        self.assertEqual(data.get_callback(
                data.DEFAULT_EVENT_MODE, "abc", "def"),
                [["code1", "arg1"], ["code2"]])

    def test_get_callback(self):
        data.clear()
        data.add_callback("googleKeyboard", "keyboard", "A_DOWN",
                ["touch", "DOWN_AND_UP", "200", "400"])
        self.assertEqual(
                data.get_callback("googleKeyboard", "keyboard", "A_DOWN"),
                ["touch", "DOWN_AND_UP", "200", "400"])

        self.assertEqual(
                data.get_callback("googleKeyboard", "keyboard", "no_key"),
                data.NO_CALLBACK)
        self.assertEqual(
                data.get_callback("googleKeyboard", "no_type", "A_DOWN"),
                data.NO_CALLBACK)
        self.assertEqual(
                data.get_callback("no_mode", "keyboard", "A_DOWN"),
                data.NO_CALLBACK)

        data.add_callback(data.DEFAULT_EVENT_MODE, "keyboard",
                          "B_DOWN", ["a", ["c", "d"]])
        self.assertEqual(
                data.get_callback("", "keyboard", "B_DOWN"),
                ["a", ["c", "d"]])
        self.assertEqual(
                data.get_callback("default", "keyboard", "B_DOWN"),
                ["a", ["c", "d"]])

    def test_show(self):
        data.clear()
        data.add_callback("a", "b", "c", ["d", "e", "f", "g"])
        data.add_callback("a", "c", "d", ["d", "e", "f", "g"])
        data.add_callback("b", "c", "d", ["g", "h"])
        data.add_callback("c", "d", "e", ["aaa", "bbb"])
        data.add_callback("ab", "cd", "ef", ["foo"])
        self.assertEqual(data.show(0), [["a", "ab", "b", "c"]])
        self.assertEqual(data.show(1),
                [["a",
                    ["b", "c"],
                 "ab",
                    ["cd"],
                 "b",
                    ["c"],
                 "c",
                    ["d"]
                    ]])
        self.assertEqual(data.show(2),
                [["a",
                    ["b", ["c"],
                     "c", ["d"]],
                 "ab",
                    ["cd", ["ef"]],
                 "b",
                    ["c", ["d"]],
                 "c",
                    ["d", ["e"]]
                    ]])
        self.assertEqual(data.show(3),
                [["a",
                    ["b",
                        ["c",
                            ["d", "e", "f", "g"]],
                     "c",
                        ["d",
                            ["d", "e", "f", "g"]]],
                 "ab",
                    ["cd",
                        ["ef",
                            ["foo"]]],
                 "b",
                    ["c",
                        ["d",
                            ["g", "h"]]],
                 "c",
                    ["d",
                        ["e",
                            ["aaa", "bbb"]]]
                    ]])

    def test_set_mode(self):
        data.clear()
        data.set_mode("abcd")
        self.assertEqual(data._current_event_mode, "abcd")

        data.set_mode(None)
        self.assertEqual(data.get_mode(), "abcd")

    def test_get_mode(self):
        data.clear()
        self.assertEqual(data.get_mode(), data.DEFAULT_EVENT_MODE)
        data._current_event_mode = "grrr"
        self.assertEqual(data.get_mode(), "grrr")
