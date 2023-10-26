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
from reference_models.antenna import antenna
from database import DatabaseServer
from test_harness_objects import DomainProxy
from reference_models.dpa import dpa_mgr
from reference_models.common import data
from common_types import ResponseCodes
from WINNF_FT_S_MCP_testcase import McpXprCommonTestcase

LOW_FREQUENCY_LIMIT_HZ = 3550000000
HIGH_FREQUENCY_LIMIT_HZ = 3650000000
ONE_MHZ = 1000000

def calculate_ref_ant_gain(request):
    tx = request['cbsd']
    rx = request['protection_point']
    gain =  antenna.calculate_antenna_gain_EAP(tx,rx)
    return gain

class EapProtectionTestcase(McpXprCommonTestcase):

  def setUp(self):
    self._sas, self._sas_admin = sas.GetTestingSas()
    self._sas_admin.Reset()

  def tearDown(self):
    self.ShutdownServers()

  def generate_EAP_1_default_config(self, filename):
    print("test")
  def test_WINNF_FT_S_REL2_RI_EAP_1(self):
    """Interference calculation using the Enhanced Antenna Pattern"""
    num_cbsd = 12
    device_cat = 'a'
    registration_request = []
    cat_b_devices = []
    for cbsdIdx in range(0,num_cbsd):
      device_filename_cat_a = '/device_a' + str(cbsdIdx+1) + '.json'
      device_a = json_load(
        os.path.join('testcases', 'testdata', 'EAP_test_data' + device_filename_cat_a))
      device_filename_cat_b = '/device_b' + str(cbsdIdx+1) + '.json'
      device_b = json_load(
        os.path.join('testcases', 'testdata', 'EAP_test_data'+ device_filename_cat_b))
      
      registration_request.append(device_a)
      registration_request.append(device_b)

    
    protection_point = {}
    protection_point['latitude'] = 39.5
    protection_point['longitude']= -112.9
    protection_point['height'] = 9
    request = {'registrationRequest': registration_request}
    response = self._sas.Registration(request)['registrationResponse'] 

    # Check registration response
    cbsd_ids = []
    for resp in response:
      self.assertEqual(resp['response']['responseCode'], 0)
    for cbsdIdx in range(10,num_cbsd*2):
    #for cbsdIdx in range(20,num_cbsd*2):

      req = {'cbsd':request['registrationRequest'][cbsdIdx],'protection_point': protection_point}
      ref_response = calculate_ref_ant_gain(req)
    #cbsd_ids.append(resp['cbsdId'])

    
    del request, response
      
    
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

    num_cbsd = 12
    device_idx_within_40km = [0,2,4,6,8,10]
    lat_within_40km = [38.8203,38.5678,38.785,39.31476,39.0567,39.567]
    lon_within_40km = [-97.2741,-97.145,-97.356,-96.75139,-96.657,-96.8897]

    device_idx_inside_ppa = [1,3,5,7,9,11]
    lat_inside_ppa = [38.8203,38.5678,38.785,39.31476,39.0567,39.567]
    lon_inside_ppa = [-97.2741,-97.145,-97.356,-96.75139,-96.657,-96.8897]

    registration_request = []
    

    device_idx_domain_proxy_0 = [0,1,2,3,4,5]
    device_idx_domain_proxy_1 = [6,7,8,9,10,11]

    grant_request_same_freq = json_load(
      os.path.join('testcases', 'testdata', 'grant_params.json'))
    grant_request_same_freq['operationParam']['operationFrequencyRange']['lowFrequency'] = 3560000000
    grant_request_same_freq['operationParam']['operationFrequencyRange']['highFrequency'] = 3570000000
    grant_req_list_0 = []
    grant_req_list_1 = []
    grant_req_list = []
    reg_request_domain_proxy_0 = []
    reg_request_domain_proxy_1 = []

    for cbsdIdx in range(0,num_cbsd-1):
      device_filename_cat_a = '/device_a' + str(cbsdIdx+1) + '.json'
      device_a = json_load(
        os.path.join('testcases', 'testdata', 'EAP_test_data' + device_filename_cat_a))
      device_filename_cat_b = '/device_b' + str(cbsdIdx+1) + '.json'
      device_b = json_load(
        os.path.join('testcases', 'testdata', 'EAP_test_data'+ device_filename_cat_b))
      
      if cbsdIdx in device_idx_within_40km:
        tempIdx = [i for i,j in enumerate(device_idx_within_40km) if j== cbsdIdx]
        device_a['installationParam']['latitude'] = lat_within_40km[tempIdx[0]]
        device_b['installationParam']['longitude'] = lon_within_40km[tempIdx[0]]
      
      if cbsdIdx in device_idx_inside_ppa:
        tempIdx = [i for i,j in enumerate(device_idx_inside_ppa) if j== cbsdIdx]
        device_a['installationParam']['latitude'] = lat_inside_ppa[tempIdx[0]]
        device_b['installationParam']['longitude'] = lon_inside_ppa[tempIdx[0]]

      if cbsdIdx in device_idx_domain_proxy_0:
        reg_request_domain_proxy_0.append(device_a)
        grant_req_list_0.append(grant_request_same_freq)
        reg_request_domain_proxy_0.append(device_b)
        grant_req_list_0.append(grant_request_same_freq)
      elif cbsdIdx in device_idx_domain_proxy_1:
        reg_request_domain_proxy_1.append(device_a)
        grant_req_list_1.append(grant_request_same_freq)
        reg_request_domain_proxy_1.append(device_b)
        grant_req_list_1.append(grant_request_same_freq)
      else:
        registration_request.append(device_a)
        grant_req_list.append(grant_request_same_freq)
        registration_request.append(device_b)
        grant_req_list.append(grant_request_same_freq)

      #grant_req_list.append(grant_request_same_freq)

    cbsd_records_domain_proxy_0 = {
        'registrationRequests': reg_request_domain_proxy_0,
        'grantRequests': grant_req_list_0,
        'conditionalRegistrationData': []
    }
    cbsd_records_domain_proxy_1 = {
        'registrationRequests': reg_request_domain_proxy_1,
        'grantRequests': grant_req_list_1,
        'conditionalRegistrationData': []
    }
    device_filename_cat_a = '/device_a' + str(12) + '.json'
    device_a = json_load(
        os.path.join('testcases', 'testdata', 'EAP_test_data' + device_filename_cat_a))
    device_filename_cat_b = '/device_b' + str(12) + '.json'
    device_b = json_load(
        os.path.join('testcases', 'testdata', 'EAP_test_data'+ device_filename_cat_b))
    
    device_a['installationParam']['latitude'] = lat_within_40km[-1]
    device_b['installationParam']['longitude'] = lon_within_40km[-1]
    #cbsd_records_domain_proxy_0 = reg_request_domain_proxy_0
    #cbsd_records_domain_proxy_1 = reg_request_domain_proxy_1

    # Protected entity record
    protected_entities = {
        'palRecords': pal_records_1,
        'ppaRecords': [ppa_record_1]
    }
    
    iteration_config = {
        'cbsdRequestsWithDomainProxies': [cbsd_records_domain_proxy_0,
                                          cbsd_records_domain_proxy_1],
        'cbsdRecords': 
        [{
            'registrationRequest': device_a,
            'grantRequest': grant_request_same_freq,
            'conditionalRegistrationData': {},
            'clientCert': getCertFilename('device_d.cert'),
            'clientKey': getCertFilename('device_d.key')
        },
        {
            'registrationRequest': device_b,
            'grantRequest': grant_request_same_freq,
            'conditionalRegistrationData': {},
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
    num_cbsd = 12

    device_idx_N2 = [0,1,2,3,4,5]
    

    registration_request_N2 = []
    registration_request_N3 = []
    grant_req_list_N2 = []
    grant_req_list_N3 = []

    grant_request_same_freq = json_load(
      os.path.join('testcases', 'testdata', 'grant_params.json'))
    grant_request_same_freq['operationParam']['operationFrequencyRange']['lowFrequency'] = 3550000000
    grant_request_same_freq['operationParam']['operationFrequencyRange']['highFrequency'] = 3560000000
    

    for cbsdIdx in range(0,num_cbsd):
      device_filename_cat_a = '/device_a' + str(cbsdIdx+1) + '.json'
      device_a = json_load(
        os.path.join('testcases', 'testdata', 'EAP_test_data' + device_filename_cat_a))
      device_filename_cat_b = '/device_b' + str(cbsdIdx+1) + '.json'
      device_b = json_load(
        os.path.join('testcases', 'testdata', 'EAP_test_data'+ device_filename_cat_b))
      if cbsdIdx in device_idx_N2:
        registration_request_N2.append(device_a)
        grant_req_list_N2.append(grant_request_same_freq)
        registration_request_N2.append(device_b)
        grant_req_list_N2.append(grant_request_same_freq)
      else:
        registration_request_N3.append(device_a)
        grant_req_list_N3.append(grant_request_same_freq)
        registration_request_N3.append(device_b)
        grant_req_list_N3.append(grant_request_same_freq)        

      #grant_req_list.append(grant_request_same_freq)

    device_a = json_load(
    os.path.join('testcases', 'testdata', 'device_a.json'))
    device_a['installationParam']['latitude'] = 30.71570
    device_a['installationParam']['longitude'] = -88.09350
    grant_a = json_load(
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
        'registrationRequestsN2': [registration_request_N2],
        'grantRequestsN2': [grant_req_list_N2],
        'conditionalRegistrationDataN2': [],
        'registrationRequestsN3': [registration_request_N3],
        'grantRequestsN3': [grant_req_list_N3],
        'conditionalRegistrationDataN3': [],
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