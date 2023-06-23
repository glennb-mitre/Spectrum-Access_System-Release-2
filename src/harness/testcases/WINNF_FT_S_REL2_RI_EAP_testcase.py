#    Copyright 2023 SAS Project Authors. All Rights Reserved.
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
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os
import logging
from concurrent.futures import ThreadPoolExecutor

import common_strings
from full_activity_dump_helper import getFullActivityDumpSasTestHarness, getFullActivityDumpSasUut
import sas
import sas_testcase
from sas_test_harness import SasTestHarnessServer, generateCbsdRecords
from util import writeConfig, loadConfig, configurable_testcase, \
  getRandomLatLongInPolygon, makePpaAndPalRecordsConsistent, \
  getCertFilename, getCertificateFingerprint, \
  getFqdnLocalhost, getUnusedPort, json_load
from reference_models.pre_iap_filtering import pre_iap_filtering
from database import DatabaseServer
from test_harness_objects import DomainProxy
from reference_models.dpa import dpa_mgr
from reference_models.common import data
from common_types import ResponseCodes
from testcases.WINNF_FT_S_MCP_testcase import McpXprCommonTestcase

LOW_FREQUENCY_LIMIT_HZ = 3550000000
HIGH_FREQUENCY_LIMIT_HZ = 3650000000
ONE_MHZ = 1000000

class EapProtectionTestcase(McpXprCommonTestcase):

  def setUp(self):
    self._sas, self._sas_admin = sas.GetTestingSas()
    self._sas_admin.Reset()

  def tearDown(self):
    self.ShutdownServers()

  def generate_EAP_default_config(self, filename):
    """ Generates the WinnForum configuration for EAP testcase """
  @configurable_testcase(generate_EAP_default_config)

  def test_WINNF_FT_S_REL2_RI_EAP(self, config_filename):
    """Interference calculation using the Enhanced Antenna Pattern"""
  
    
  def generate_EAP_2_default_config(self, filename):
    """ Generates the WinnForum configuration for testcase EAP.2. """

    # Load PPA record
    ppa_record = json_load(
      os.path.join('testcases', 'testdata', 'ppa_record_0.json'))
    pal_record = json_load(
      os.path.join('testcases', 'testdata', 'pal_record_0.json'))

    pal_low_frequency = 3550000000
    pal_high_frequency = 3560000000

    ppa_record_1, pal_records_1 = makePpaAndPalRecordsConsistent(
                                  ppa_record,
                                  [pal_record],
                                  pal_low_frequency,
                                  pal_high_frequency,
                                  'test_user_1'
    )

    # Load devices info
    device_1 = json_load(
      os.path.join('testcases', 'testdata', 'device_a.json'))
    # Moving device_1 to a location within 40 KMs of PPA zone
    device_1['installationParam']['latitude'] = 38.8203
    device_1['installationParam']['longitude'] = -97.2741

    device_2 = json_load(
      os.path.join('testcases', 'testdata', 'device_b.json'))
    # Moving device_2 to a location outside 40 KMs of PPA zone
    device_2['installationParam']['latitude'] = 39.31476
    device_2['installationParam']['longitude'] = -96.75139

    device_3 = json_load(
      os.path.join('testcases', 'testdata', 'device_c.json'))
    # Moving device_3 to a location within PPA zone
    device_3['installationParam']['latitude'], \
    device_3['installationParam']['longitude'] = getRandomLatLongInPolygon(ppa_record_1)

    device_4 = json_load(
      os.path.join('testcases', 'testdata', 'device_d.json'))
    # Moving device_4 to a location within PPA zone
    device_4['installationParam']['latitude'], \
    device_4['installationParam']['longitude'] = getRandomLatLongInPolygon(ppa_record_1)

    # Load Grant requests
    grant_request_1 = json_load(
      os.path.join('testcases', 'testdata', 'grant_0.json'))
    grant_request_1['operationParam']['operationFrequencyRange']['lowFrequency'] = 3550000000
    grant_request_1['operationParam']['operationFrequencyRange']['highFrequency'] = 3560000000

    grant_request_2 = json_load(
      os.path.join('testcases', 'testdata', 'grant_1.json'))
    grant_request_2['operationParam']['operationFrequencyRange']['lowFrequency'] = 3550000000
    grant_request_2['operationParam']['operationFrequencyRange']['highFrequency'] = 3560000000

    grant_request_3 = json_load(
      os.path.join('testcases', 'testdata', 'grant_2.json'))
    grant_request_3['operationParam']['operationFrequencyRange']['lowFrequency'] = 3550000000
    grant_request_3['operationParam']['operationFrequencyRange']['highFrequency'] = 3560000000

    grant_request_4 = json_load(
      os.path.join('testcases', 'testdata', 'grant_0.json'))
    grant_request_4['operationParam']['operationFrequencyRange']['lowFrequency'] = 3550000000
    grant_request_4['operationParam']['operationFrequencyRange']['highFrequency'] = 3560000000

    # device_b and device_d are Category B
    # Load Conditional Data
    self.assertEqual(device_2['cbsdCategory'], 'B')
    conditionals_device_2 = {
        'cbsdCategory': device_2['cbsdCategory'],
        'fccId': device_2['fccId'],
        'cbsdSerialNumber': device_2['cbsdSerialNumber'],
        'airInterface': device_2['airInterface'],
        'installationParam': device_2['installationParam'],
        'measCapability': device_2['measCapability']
    }

    self.assertEqual(device_4['cbsdCategory'], 'B')
    conditionals_device_4 = {
        'cbsdCategory': device_4['cbsdCategory'],
        'fccId': device_4['fccId'],
        'cbsdSerialNumber': device_4['cbsdSerialNumber'],
        'airInterface': device_4['airInterface'],
        'installationParam': device_4['installationParam'],
        'measCapability': device_4['measCapability']
    }

    # Remove conditionals from registration
    del device_2['cbsdCategory']
    del device_2['airInterface']
    del device_2['installationParam']
    del device_2['measCapability']
    del device_4['cbsdCategory']
    del device_4['airInterface']
    del device_4['installationParam']
    del device_4['measCapability']

    # Registration and grant records
    cbsd_records_domain_proxy_0 = {
        'registrationRequests': [device_1, device_2],
        'grantRequests': [grant_request_1, grant_request_2],
        'conditionalRegistrationData': [conditionals_device_2]
    }
    cbsd_records_domain_proxy_1 = {
        'registrationRequests': [device_3],
        'grantRequests': [grant_request_3],
        'conditionalRegistrationData': []
    }

    # Protected entity record
    protected_entities = {
        'palRecords': pal_records_1,
        'ppaRecords': [ppa_record_1]
    }

    iteration_config = {
        'cbsdRequestsWithDomainProxies': [cbsd_records_domain_proxy_0,
                                          cbsd_records_domain_proxy_1],
        'cbsdRecords': [{
            'registrationRequest': device_4,
            'grantRequest': grant_request_4,
            'conditionalRegistrationData': conditionals_device_4,
            'clientCert': getCertFilename('device_d.cert'),
            'clientKey': getCertFilename('device_d.key')
        }],
        'protectedEntities': protected_entities,
        'dpaActivationList': [],
        'dpaDeactivationList': [],
        'sasTestHarnessData': []
    }

    # Create the actual config.
    config = {
        'initialCbsdRequestsWithDomainProxies': self.getEmptyCbsdRequestsWithDomainProxies(2),
        'initialCbsdRecords': [],
        'iterationData': [iteration_config],
        'sasTestHarnessConfigs': [],
        'domainProxyConfigs': [{
            'cert': getCertFilename('domain_proxy.cert'),
            'key': getCertFilename('domain_proxy.key')
        }, {
            'cert': getCertFilename('domain_proxy_1.cert'),
            'key': getCertFilename('domain_proxy_1.key')
        }]
    }
    writeConfig(filename, config)

  @configurable_testcase(generate_EAP_2_default_config)

  def test_WINNF_FT_S_REL2_RI_EAP_2(self, config_filename):
    """Single SAS PPA Protection using the Enhanced Antenna Pattern"""
    
    config = loadConfig(config_filename)
    # Invoke MCP test steps 1 through 22.
    self.executeMcpTestSteps(config, 'EAP2')

  def generate_EAP_3_default_config(self, filename):
    """ Generates the WinnForum configuration for EAP.3 testcase """
        # Load Devices.
    device_a = json_load(
        os.path.join('testcases', 'testdata', 'device_a.json'))
    device_a['installationParam']['latitude'] = 30.71570
    device_a['installationParam']['longitude'] = -88.09350

    device_b = json_load(
        os.path.join('testcases', 'testdata', 'device_b.json'))
    device_b['installationParam']['latitude'] = 30.71570
    device_b['installationParam']['longitude'] = -88.09350
    device_c = json_load(
        os.path.join('testcases', 'testdata', 'device_c.json'))
    device_c['installationParam']['latitude'] = 30.71570
    device_c['installationParam']['longitude'] = -88.09350

    # Pre-load conditionals and remove reg conditional fields from registration
    # request.
    conditional_keys = [
        'cbsdCategory', 'fccId', 'cbsdSerialNumber', 'airInterface',
        'installationParam', 'measCapability'
    ]
    reg_conditional_keys = [
        'cbsdCategory', 'airInterface', 'installationParam', 'measCapability'
    ]
    conditionals_b = {key: device_b[key] for key in conditional_keys}
    conditionals_c = {key: device_c[key] for key in conditional_keys}
    device_b = {
        key: device_b[key]
        for key in device_b
        if key not in reg_conditional_keys
    }
    device_c = {
        key: device_c[key]
        for key in device_c
        if key not in reg_conditional_keys
    }

    # Load grant requests.
    grant_a = json_load(
        os.path.join('testcases', 'testdata', 'grant_0.json'))
    grant_b = json_load(
        os.path.join('testcases', 'testdata', 'grant_0.json'))
    grant_c = json_load(
        os.path.join('testcases', 'testdata', 'grant_0.json'))

    sas_test_harness_config = {
        'sasTestHarnessName': 'SAS-Test-Harness-1',
        'hostName': getFqdnLocalhost(),
        'port': getUnusedPort(),
        'serverCert': getCertFilename('sas.cert'),
        'serverKey': getCertFilename('sas.key'),
        'caCert': getCertFilename('ca.cert'),
        'fullActivityDumpRecords': [
            generateCbsdRecords([device_a], [[grant_a]])
        ]
    }

    dpa_1 = {
        'dpaId': 'Pascagoula',
        'frequencyRange': {
            'lowFrequency': 3620000000,
            'highFrequency': 3630000000
        },
        'points_builder': 'default (25, 10, 10, 10)',
        'movelistMargin': 10
    }

    config = {
        'sasTestHarnessConfigs': [sas_test_harness_config],
        'registrationRequestsN2': [device_b],
        'grantRequestsN2': [grant_b],
        'conditionalRegistrationDataN2': [conditionals_b],
        'registrationRequestsN3': [device_c],
        'grantRequestsN3': [grant_c],
        'conditionalRegistrationDataN3': [conditionals_c],
        'dpas': [dpa_1]
    }
    writeConfig(filename, config)

  @configurable_testcase(generate_EAP_3_default_config)

  def test_WINNF_FT_S_REL2_RI_EAP_3(self, config_filename):
    """Single SAS DPA Protection using the Enhanced Antenna Pattern"""
    config = loadConfig(config_filename)
    self.assertValidConfig(
        config, {
            'sasTestHarnessConfigs': list,
            'registrationRequestsN2': list,
            'grantRequestsN2': list,
            'registrationRequestsN3': list,
            'grantRequestsN3': list,
            'conditionalRegistrationDataN2': list,
            'conditionalRegistrationDataN3': list,
            'dpas': list
        })
    # The N3 grant requests must all overlap at least partially with 3550-3650.
    for grant_request in config['grantRequestsN3']:
      self.assertLessEqual(
          grant_request['operationParam']['operationFrequencyRange'][
              'lowFrequency'],
          3650e6,
          msg=
          'Invalid config: N3 Grants must at least partially overlap with 3550-3650 MHz.'
      )
    num_peer_sases = len(config['sasTestHarnessConfigs'])
    # SAS UUT loads DPAs.
    logging.info('Step 1: trigger DPA load.')
    self._sas_admin.TriggerLoadDpas()

    # Steps 2 & 3 can be interleaved.
    logging.info('Steps 2 + 3: activate and configure SAS Test Harnesses.')
    test_harnesses = []
    for test_harness_config in config['sasTestHarnessConfigs']:
      # Create test harness, notify the SAS UUT, and load FAD records.
      test_harness = SasTestHarnessServer(
          test_harness_config['sasTestHarnessName'],
          test_harness_config['hostName'], test_harness_config['port'],
          test_harness_config['serverCert'], test_harness_config['serverKey'],
          test_harness_config['caCert'])
      test_harness.start()
      self._sas_admin.InjectPeerSas({
          'certificateHash':
              getCertificateFingerprint(test_harness_config['serverCert']),
          'url':
              test_harness.getBaseUrl()
      })
      for fullActivityDumpRecord in test_harness_config['fullActivityDumpRecords']:
          self.InjectTestHarnessFccIds(fullActivityDumpRecord)
      test_harness.writeFadRecords(
          test_harness_config['fullActivityDumpRecords'])
      test_harnesses.append(test_harness)

    # Register N2 CBSDs with the SAS UUT and request Grants.
    logging.info('Step 4: Registering and Granting N2 CBSDs with SAS UUT.')
    n2_domain_proxy = DomainProxy(self)
    n2_domain_proxy.registerCbsdsAndRequestGrants(
        config['registrationRequestsN2'],
        config['grantRequestsN2'],
        conditional_registration_data=config['conditionalRegistrationDataN2'])

    # Trigger CPAS.
    logging.info('Step 5: Triggering CPAS.')
    self.TriggerDailyActivitiesImmediatelyAndWaitUntilComplete()

    # Register N3 CBSDs with the SAS UUT and request Grants.
    logging.info('Step 6: Registering and Granting N3 CBSDs with SAS UUT.')
    # Note: the frequency range of the N3 grant requests was checked above.
    n3_domain_proxy = DomainProxy(self)
    n3_domain_proxy.registerCbsdsAndRequestGrants(
        config['registrationRequestsN3'],
        config['grantRequestsN3'],
        conditional_registration_data=config['conditionalRegistrationDataN3'])

    # Heartbeat all SAS UUT CBSDS
    logging.info('Step 7: Heartbeating all active Grants.')
    n2_domain_proxy.heartbeatForAllActiveGrants()
    n3_domain_proxy.heartbeatForAllActiveGrants()

    # None of the N3 CBSDS should be authorized.
    logging.info('CHECK: None of the N3 Grants are authorized.')
    cbsds = n3_domain_proxy.getCbsdsWithAtLeastOneAuthorizedGrant()
    if cbsds:
      for cbsd in cbsds:
        logging.info(
            'CBSD (cbsd_id=%s, fcc_id=%s, sn=%s) '
            'is authorized after IPR.1 step 7. SAS UUT FAILS this test. '
            '(If this config is new please verify the CBSD is in a DPA neighborhood.)',
            cbsd.getCbsdId(),
            cbsd.getRegistrationRequest()['fccId'],
            cbsd.getRegistrationRequest()['cbsdSerialNumber'])
    self.assertEqual(
        len(cbsds),
        0,
        msg='At least one N3 CBSD was authorized; see above for details.')

    # Get SAS UUT FAD and Test Harness FADs.
    logging.info('Steps 8 + 9: generate and pull FAD.')
    sas_uut_fad = None
    test_harness_fads = []
    if num_peer_sases:
      ssl_cert = config['sasTestHarnessConfigs'][0]['serverCert']
      ssl_key = config['sasTestHarnessConfigs'][0]['serverKey']
      sas_uut_fad = getFullActivityDumpSasUut(self._sas, self._sas_admin, ssl_cert=ssl_cert, ssl_key=ssl_key)
      for test_harness in test_harnesses:
        test_harness_fads.append(
            getFullActivityDumpSasTestHarness(
                test_harness.getSasTestHarnessInterface()))

    # Trigger CPAS.
    logging.info('Step 10: Triggering CPAS.')
    self.TriggerDailyActivitiesImmediatelyAndWaitUntilComplete()

    # Heartbeat SAS UUT grants.
    logging.info('Step 12: Heartbeating all active Grants.')
    n2_domain_proxy.heartbeatForAllActiveGrants()
    n3_domain_proxy.heartbeatForAllActiveGrants()
    # Get CbsdGrantInfo list of SAS UUT grants that are in an authorized state.
    grant_info = data.getAuthorizedGrantsFromDomainProxies([n2_domain_proxy, n3_domain_proxy])

    # Initialize DPA objects and calculate movelist for each DPA.
    logging.info('Steps 11 + 13, CHECK: DPA aggregate interference check.')
    dpas = []
    all_dpa_checks_succeeded = True
    for dpa_config in config['dpas']:
      logging.info('Checking DPA %s', dpa_config)
      dpa = dpa_mgr.BuildDpa(dpa_config['dpaId'], dpa_config['points_builder'])
      low_freq_mhz = dpa_config['frequencyRange']['lowFrequency'] // ONE_MHZ
      high_freq_mhz = dpa_config['frequencyRange']['highFrequency'] // ONE_MHZ
      dpa.ResetFreqRange([(low_freq_mhz, high_freq_mhz)])
      dpa.SetGrantsFromFad(sas_uut_fad, test_harness_fads)
      dpa.ComputeMoveLists()
      # Check grants do not exceed each DPAs interference threshold.
      this_dpa_check_succeeded = dpa.CheckInterference(
          sas_uut_active_grants=grant_info,
          margin_db=dpa_config['movelistMargin'],
          channel=(low_freq_mhz, high_freq_mhz),
          do_abs_check_single_uut=(num_peer_sases == 0))
      if not this_dpa_check_succeeded:
        logging.error('Check for DPA %s FAILED.', dpa_config['dpaId'])
        all_dpa_checks_succeeded = False

    self.assertTrue(
        all_dpa_checks_succeeded,
        'At least one DPA check failed; please see logs for details.')

    # Stop test harness servers.
    for test_harness in test_harnesses:
      test_harness.shutdown()
      del test_harness