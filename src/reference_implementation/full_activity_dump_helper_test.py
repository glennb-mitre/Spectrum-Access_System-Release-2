#    Copyright 2018 SAS Project Authors. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
"""Tests for the Full Activity Dump Helper."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime
import unittest
import logging
import copy

try:
  from unittest import mock
except ImportError:
  import mock

import full_activity_dump_helper


class FullActivityDumpHelperTest(unittest.TestCase):
  """Full Activity Dump Helper unit tests."""

  @staticmethod
  def getFullActivityDumpHelper(ssl_cert=None, ssl_key=None):
    """Provides a generic dump to use for tests. Setting the generation date to
       now is needed for SAS UUT unit test.
    """
    return {
        'files': [{
            'url': 'cbsd/cbsd_test_url.json',
            'checksum': 'checksum does not matter for test',
            'size': 1,
            'version': 'version does not matter for test',
            'recordType': 'cbsd'
        }, {
            'url': 'zone/zone_test_url.json',
            'checksum': 'checksum does not matter for test',
            'size': 1,
            'version': 'some version',
            'recordType': 'zone'
        }, {
            'url': 'esc_sensor/esc_test_url.json',
            'checksum': 'checksum does not matter for test',
            'size': 1,
            'version': 'some version',
            'recordType': 'esc_sensor'
        }, {
            'url': 'cbsd/cbsd_test_url2.json',
            'checksum': 'checksum does not matter for test',
            'size': 1,
            'version': 'some version',
            'recordType': 'cbsd'
        }],
        'generationDateTime': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'description':
            'mock for testing full activity dump'
    }

  @staticmethod
  def downloadFileHelper(url, ssl_cert=None, ssl_key=None):
    """Helper to return test dump content."""
    logging.debug('CALLED: %s %s %s', url, ssl_cert, ssl_key)
    if url == 'cbsd/cbsd_test_url.json':
      return {'recordData': [{'a': 1, 'b': 2}, {'c': 3}]}
    if url == 'esc_sensor/esc_test_url.json':
      return {'recordData': [{'d': 1}]}
    if url == 'zone/zone_test_url.json':
      return {'recordData': [{'g': 1}]}
    if url == 'cbsd/cbsd_test_url2.json':
      return {'recordData': [{'j': 1}]}
    else:
      raise ValueError('unsupported URL: %s' % url)

  @staticmethod
  def getMockSasInterface():
    sas_interface = mock.MagicMock()
    sas_interface.GetFullActivityDump.side_effect = FullActivityDumpHelperTest.getFullActivityDumpHelper
    sas_interface.DownloadFile.side_effect = FullActivityDumpHelperTest.downloadFileHelper
    return sas_interface

  def test_create_fad_for_sas_uut(self):
    """Tests that a FullActivityDump can be created for the SAS UUT."""
    mock_sas = FullActivityDumpHelperTest.getMockSasInterface()
    mock_sas_admin = mock.MagicMock()
    fad = full_activity_dump_helper.getFullActivityDumpSasUut(
        mock_sas, mock_sas_admin)
    mock_sas.GetFullActivityDump.assert_called()
    mock_sas.DownloadFile.assert_called()
    self.assertDictEqual(
        fad.getData(), {
            'cbsd': [{'a': 1, 'b': 2}, {'c': 3}, {'j': 1}],
            'esc_sensor': [{'d': 1}],
            'zone': [{'g': 1}]
        })

  def test_create_fad_for_test_harness(self):
    """Tests that a FullActivityDump can be created for a test harness."""
    mock_sas = FullActivityDumpHelperTest.getMockSasInterface()
    fad = full_activity_dump_helper.getFullActivityDumpSasTestHarness(
        mock_sas)
    mock_sas.GetFullActivityDump.assert_called_once()
    mock_sas.DownloadFile.assert_called()
    self.assertDictEqual(
        fad.getData(), {
            'cbsd': [{'a': 1, 'b': 2}, {'c': 3}, {'j': 1}],
            'esc_sensor': [{'d': 1}],
            'zone': [{'g': 1}]
        })


if __name__ == '__main__':
  unittest.main()
