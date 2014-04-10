import mock
import unittest

from requests import ConnectionError

from papaye.tests.tools import FakeGRequestResponse


class ExistsOnPyPIMixinTest(unittest.TestCase):

    from papaye.views.mixins import ExistsOnPyPIMixin

    class FakeView(ExistsOnPyPIMixin, object):
        pass

    @mock.patch('requests.get')
    def test_exists_on_pypi(self, mock):
        mock.return_value = FakeGRequestResponse(200, '')

        view = self.FakeView()

        result = view.exists_on_pypi('http://pypi.python.org/pypi/example')

        self.assertTrue(result)

    @mock.patch('requests.get')
    def test_exists_on_pypi_with_not_found(self, mock):
        mock.return_value = FakeGRequestResponse(404, '')

        view = self.FakeView()

        result = view.exists_on_pypi('http://pypi.python.org/pypi/example')

        self.assertFalse(result)

    @mock.patch('requests.get')
    def test_exists_on_pypi_with_other_status_code(self, mock):
        mock.return_value = FakeGRequestResponse(500, '')

        view = self.FakeView()

        result = view.exists_on_pypi('http://pypi.python.org/pypi/example')

        self.assertFalse(result)

    @mock.patch('requests.get')
    def test_exists_on_pypi_with_exceptions(self, mock):

        mock.side_effect = ConnectionError()

        view = self.FakeView()
        result = view.exists_on_pypi('http://pypi.python.org/pypi/example')
        self.assertFalse(result)
