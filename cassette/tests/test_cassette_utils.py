from cassette.tests.base import TestCase
from cassette.utils import Encoder, JsonEncoder, YamlEncoder

TEST_DATA = {
    'binary_data': '\x89\x70\x00',
    'normal_str': 'ABCDEFG',
    'some_list': [1, 2, 3, 4],
    'deep_list': [
            {'a': 3},
            {'b': 4},
            {'c': 6},
            {'d': 7},
    ]
}


class TestEncoder(TestCase):

    def test_implementation_errors(self):
        """Verify that we cannot call dump/load since they are yet not implemented."""
        with self.assertRaises(NotImplementedError):
            Encoder().dump({})

        with self.assertRaises(NotImplementedError):
            Encoder().load('')


class CommonEncoderTest(object):
    """Common test cases shared by TestJsonEncoder and TestYamlEncoder."""

    def test_dump_and_load(self):
        """Verify dump and load are working. Used for implemented encoders."""
        data = self.encoder.load(self.encoder.dump(TEST_DATA))

        for key in TEST_DATA.keys():
            self.assertEqual(data[key], TEST_DATA[key])


class TestJsonEncoder(TestCase, CommonEncoderTest):
    """Verify that the JSON dump/load is working."""

    def setUp(self):
        self.encoder = JsonEncoder()


class TestYamlEncoder(TestCase, CommonEncoderTest):
    """Verify that the JSON dump/load is working."""

    def setUp(self):
        self.encoder = YamlEncoder()
