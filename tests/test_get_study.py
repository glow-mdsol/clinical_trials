import os
import unittest
from mock import mock

from clinical_trials.connector import get_study


class TestGetStudy(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(os.path.dirname(__file__), "fixtures/NCT02348489.xml"), 'rb') as fh:
            self.content = fh.read()

    def test_successful_retrieval(self):
        """
        Get the expected path and response
        """
        with mock.patch('clinical_trials.connector.requests.get') as mock_get:
            mock_get.return_value = mock.MagicMock(status_code=200, content=self.content)
            response_content = get_study('NCT02348489')
        self.assertEqual(self.content, response_content)
        mock_get.assert_called_with("https://clinicaltrials.gov/ct2/show/NCT02348489?displayxml=True")

    def test_failed_pull(self):
        """
        Get the expected path and response
        """
        with mock.patch('clinical_trials.connector.requests.get') as mock_get:
            mock_get.return_value = mock.MagicMock(status_code=404, content="")
            with self.assertRaises(ValueError) as exc:
                response_content = get_study('NCT10000000')
        self.assertEqual("Unable to load study NCT10000000", str(exc.exception))
        mock_get.assert_called_with("https://clinicaltrials.gov/ct2/show/NCT10000000?displayxml=True")