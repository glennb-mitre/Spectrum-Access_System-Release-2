import pytest

import grant_processes as gp
import utils


class Test_Grant():
    """ """

    def __init__():
        """ Setup as the m-i-t-m or connect to a fake sas so testcases can be evaluated. """
        self.gp = gp.Grant(test_ip, test_port)
        self.sas = utils.sas_connect()

            # Load test value lists into their respective varialbles.
            self.userIds = config.userIds
            self.fccIds = config.fcc_ids
            self.cbsdSerialNumbers = config.cbsdSerialNumbers
    
    
    def test_step_1():
        """ Ensure no cbsdId exists in the SAS for the CBSDs being tested. """
        #
        if self.sas.get_cbsdId == 0:
            assert self.gp.check_for_cbsds() == False

        #
        self.sas.add_cbsdId(cbsdId1)
        assert self.gp.check_for_cbsds() == True

        # Ensure the test cbsds are not in the SAS
        if self.sas.get_cbsdId != 0:
            for cbsd in self.cbsds:
                assert self.gp.check_for_cbsd(cbsd) == False

    
    def test_step_2():
        """ Ensure that the DP Test Harness sends a Registration Request in the form of one 3-element Array to the SAS. """
        self.gp.send_registration_request()
        reg_req_list = self.sas.get_last_registration_request()
        for reg_req in reg_req_list:
            assert reg_req[0] in self.userIds
            assert reg_req[1] in self.fccIds
            assert reg_req[2] in self.cbsdSerialNumbers


    def test_check_1():
        """ """
        self.sas.send_registration_response()
        
        
    def test_step_3():
        """ CBSD Test Harness (C1) sends a Grant Request Message in which cbsdId is set to C2. """
        self.gp.send_grant_request()
        grant_req = self.sas.get_last_grant_request()
        assert grant_req["cbsdId"] == "C2"
    
    
    def test_step_5():
        """ DP Test Harness sends a Heartbeat Request Message with the heartbeatRequest parameter containing 3 elements. """
        # Check if the test harness correctly accounts for incumbents.
        # by blocking the grant so it can be handed over.
        # self.gp.send_heartbeat_request

        # 
        self.gp.send_heartbeat_request()
        heart_req = self.sas.get_last_heartbeat_request()
        assert len(heart_req) >= 4
        assert heart_req[0] in self.cbsdIds
        assert heart_req[1] != None
        assert heart_req[1] != ""
        assert heart_req[2] == True
        assert heart_req[3] != None
        assert heart_req[3] != ""


    def test_step_7():
        """ CBSD Test Harness (C1) sends a Grant Request Message in which cbsdId is set to C2. """
        self.gp.send_c2_grant_request()
        grant_req = self.sas.get_last_grant_request()

        grant_req = self.sas.get_last_grant_request()
        assert grant_req["cbsdId"] == "C2"
    

    def test_check_2():
        """ """
        self.sas.send_grant_response()