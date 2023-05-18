import pytest

import grant_processes as gp
import utils

class Test_Grant_Objects():
    """ """

    def __init__():
        """ Setup as the m-i-t-m or connect to a fake sas so testcases can be evaluated. """
        self.gp = gp.Grant(test_ip, test_port)
        self.sas = utils.sas_connect()

            # Load test value lists into their respective varialbles.
            self.userIds = config.userIds
            self.fccIds = config.fcc_ids
            self.cbsdSerialNumbers = config.cbsdSerialNumbers


    def test_registration_request():
        """ """
        self.gp.send_registration_request()
        reg_req = self.sas.get_last_registration_request()
        registration_request_destructure(reg_req)
    

    def registration_request_destructure():
        """ """
        # Required
        self.userId = ""
        self.fccId = ""
        self.cbsdSerialNumber = ""
        self.cbsdFeatureCapabilityList = [""]

        # Regulatory Conditional.
        self.cbsdCategory = [""]
        self.airInterface = {radioTechnology:""}
        self.installationParam = {lattitude:00, longitude:00, height:00, heightType:"",indoorDeployment:False, antennaAzimuth:00, antennaDowntilt:00, antennaGain:00, \
            antennaBeamwidth:00}
        self.measCapability = [""]

    
    def test_grant_request():
        """ """
        self.gp.send_grant_request()
        reg_req = self.sas.get_last_grant_request()
        grant_request_destructure(reg_req)
    

    def grant_request_deconstruction():
        """ """
        self.cbsdId = ""
        self.operationParam = 
        self.maxEirp = ""
        self.operationFrequencyRange = 
    
    
    def test_heartbeat_request():
        """ """
        self.gp.send_heartbeat_request()
        reg_req = self.sas.get_last_heartbeat_request()
        heartbeat_request_destructure(reg_req)

    
    def heartbeat_request_deconstruction():
        """ """
        self.cbsdId = ""
        self.grantId = ""
        self.operationState = ""