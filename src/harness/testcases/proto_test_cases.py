import pytest

def test_registration():
    """ 6.1.4.1	 [WINNF.FT.S.REG.1] Array Multi-Step Registration for CBSDs (Cat A and B) """
    pass

def test_grant_request():
    """ 6.3.4.17	[WINNF.FT.S.GRA.17] [Configurable] Array Grant Request """
    
    sas = "config.fake_sas"
    fcc_ids = [config.fcc_ids]
    user_ids = [config.user_ids]
    cbsds = [config.cbsds]

    # Every test must start with the sas being reset to ensure a baseline state
    sas.reset()

    for num in range(fcc_ids):
        sas.check_fcc_id(fcc_ids[num])
        sas.check_user_id(user_ids[num])

    # Register method returns the response code
    for cbsd in cbsds:
        assert sas.register(cbsd) == 0

    sas.grant_request()


def test_heartbeat():
    """ 6.4.4.1	[WINNF.FT.S.HBT.1] Array request: Successful Heartbeat Request """

    # Every test must start with the sas being reset to ensure a baseline state
    sas.reset()

    # Checks the SAS to ensure base conditions are met
    for cbsd in cbsds:
        assert sas.get_cbsd(cbsd).id == cbsd.id
        assert sas.get_grant(cbsd) == True
        assert sas.check_authorized(cbsd) == True
    
    
    # Heartbeat request is assumed to be a list.
    heart_req = cbsd.heartbeat_req
    assert len(heart_req) == 4
    assert heart_req[0].cbsd_id != None
    assert heart_req[0].cbsd_grant_id != None 
    assert heart_req[1].cbsd_id != None
    assert heart_req[1].cbsd_grant_id != None 
    assert heart_req[2].cbsd_id != None
    assert heart_req[2].cbsd_grant_id != None

    # The 4th eleement in the list should not be an object with a cbs_id. 
    with pytest.raises(AttributeError):
        assert heart_req[3].cbs__id == None
    
    # Checks whether the cbsd_id's grant lists a frequency needed for an incumbent.
    assert sas.check_incumbent(heart_req.cbsd_id) == False


def test_grant_renewal_heartbeat():
    """ 6.4.4.2	[WINNF.FT.S.HBT.2] Array request: Successful Heartbeat Request from CBSD for Grant renewal  """

    sas.reset()

    # Checks the SAS to ensure base conditions are met.
    for cbsd in cbsds:
        assert sas.get_cbsd(cbsd).id == cbsd.id
        assert sas.get_grant(cbsd) == True
        assert sas.check_authorized(cbsd) == True
    

    heart_req = cbsd.heartbeat_req
    assert len(heart_req) == 4
    assert heart_req[0].cbsd_id != None
    assert heart_req[0].cbsd_grant_id != None 
    assert heart_req[0].cbsd_grant_renew == True
    assert heart_req[1].cbsd_id != None
    assert heart_req[1].cbsd_grant_id != None 
    assert heart_req[1].cbsd_grant_renew == True
    assert heart_req[2].cbsd_id != None
    assert heart_req[2].cbsd_grant_id != None
    assert heart_req[2].cbsd_grant_renew == True

    with pytest.raises(AttributeError):
        assert heart_req[3].cbs__id == None

    # Checks whether the cbsd_id's grant lists a frequency needed for an incumbent.
    assert sas.check_incumbent(heart_req.cbsd_id) == False