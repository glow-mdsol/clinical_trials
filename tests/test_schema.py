import unittest

from mock import mock

from clinical_trials.schema import get_local_schema


class TestGetLocalSchema(unittest.TestCase):
    def test_something(self):
        with mock.patch('clinical_trials.schema.os.path.exists') as mock_exist:
            mock_exist.return_value = False
            with self.assertRaises(ValueError) as exc:
                schema = get_local_schema()
            self.assertEqual("Unable to locate schema document", str(exc.exception))

