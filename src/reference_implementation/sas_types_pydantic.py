"""
This module contains class definitions for objects used in SAS-CBSD interactions according to the following documents:
<1> WINNF-TS-0016-V1.2.7 SAS to CBSD Technical Specification
<2> WINNF-SSC-0002 v10.0.0 Signaling Protocols and Procedures for Citizens Broadband Radio Service (CBRS):
    WInnForum Recognized CBRS Air Interfaces and Measurements
*2  <1> cites <2> for several object field definitions
<3> WINNF-TS-0096-V1.4.0 Signaling Protocols and Procedures for Citizens Broadband Radio Service (CBRS): Spectrum Access
    System (SAS) - SAS Interface Technical Specification

The above documents may be found at https://cbrs.wirelessinnovation.org/release-1-standards-specifications

Note 1: <1> Marks each parameter's requirement level with (R)equired, (O)ptional, or (C)onditional.
In the case of Registration Request Message objects, some parameters are marked as "REG-Conditional," indicating that
"the parameter is required by the SAS to complete the CBSD registration process, but may be omitted from the
[RegistrationRequest] object. If not included in the RegistrationRequest object, the parameter, to the extent that it
is needed by the SAS to satisfy the Part 96 Rules, shall be provided to the SAS by other means outside the protocol
specified in this document, e.g., it may be provided by a CPI as required by Part 96 Rules for category B CBSDs or CBSDs
without automatic location determination, or for operational reasons. Other means based on CBSD device characteristics
that are beyond the scope of this specification, are not precluded from use.


This module uses pydantic to validate objects, inputs, and outputs
"""

from enum import Enum, IntEnum
from decimal import Decimal
from typing import Optional, Any, Union, List, Dict, Tuple
# See https://docs.pydantic.dev/latest/usage/types/#constrained-types
from pydantic import (
    BaseModel,
    NegativeFloat,
    NegativeInt,
    PositiveFloat,
    PositiveInt,
    NonNegativeFloat,
    NonNegativeInt,
    NonPositiveFloat,
    NonPositiveInt,
    conbytes,
    condecimal,
    confloat,
    conint,
    conlist,
    conset,
    constr,
    Field,
    Extra,
)

OptStr = Optional[str]
OptFloat = Optional[float]
OptInt = Optional[int]
OptDec = Optional[Decimal]

# The following classes are for SAS-CBSD interactions and are derived from the definitions given in <1> and <2>

class CbsdInfo(BaseModel, extra=Extra.allow):
    """
    Optional argument for RegistrationRequest
    Defined in 10.1.5 of <1>

    Note: The maximum length of each parameter is 64 octets
    Note 2: The CbsdInfo object can be extended with other vendor information in additional key-value pairs.
    This is captured in the pydantic model by using 'extra=Extra.allow'.

    All fields are optional
    """
    # Name of CBSD Vendor
    vendor: Optional[constr(max_length=64)] = None
    # Name of the CBSD model
    model: Optional[constr(max_length=64)] = None
    # Software version of the CBSD
    softwareVersion: Optional[constr(max_length=64)] = None
    # Hardware version of the CBSD
    hardwareVersion: Optional[constr(max_length=64)] = None
    # Firmware version of the CBSD
    firmwareVersion: Optional[constr(max_length=64)] = None


class RadioTechnologyEnum(str, Enum):
    """
    Used to specify the possible choices for the 'radio_technology' parameter of an AirInterface object
    The peritted values are specified in section 6 of <2>
    """
    E_UTRA = "E_UTRA"
    CAMBRIUM_NETWORKS = "CAMBRIUM_NETWORKS"
    FOURG_BBW_SAA_1 = "4G_BBW_SAA_1"
    NR = "NR"
    DOODLE_CBRS = "DOODLE_CBRS"
    # See documentation; should never request nor grant an EIRP of > 20 dBm for Category A or 37 dBm for Category B
    CW = "CW"
    REDLINE = "REDLINE"
    TARANA_WIRELESS = "TARANA_WIRELESS"
    FAROS = "FAROS"


class AirInterface(BaseModel):
    """
    A data object that includes information on the air interface technology of the CBSD.
    REG-Conditional for RegistrationRequest
    Defined in 10.1.2 of <1>
    """
    # REG-Conditional
    radioTechnology: RadioTechnologyEnum


class HeightTypeEnum(str, Enum):
    """
    Used to specify the possible choices for the 'height_type' parameter of an InstallationParam object
    """
    AGL = "AGL" # measured relative to ground level
    AMSL = "AMSL" # measured relative to mean sea level


class InstallationParam(BaseModel):
    """
    A data object that includes information on CBSD installation.
    REG-Conditional for RegistrationRequest
    Defined in 10.1.3 of <1>

    All fields are either Conditionally Required (REG_Conditional) or Optional.
    """
    # REG-Conditional ... May need to write a custom validator since condecimal's arguments don't include trailing
    # zeroes
    latitude: Optional[condecimal(ge=Decimal(-90.000000), le=Decimal(90.000000), decimal_places=6)]
    # REG-Conditional
    longitude: Optional[condecimal(ge=Decimal(-180.000000), le=Decimal(180.000000), decimal_places=6)]
    # REG-Conditional - The CBSD antenna height in meters.When the heightType parameter value is “AGL”, the antenna
    # height should be given relative to ground level. When the heightType parameter value is “AMSL”, it is given
    # with respect to WGS84 datum. For reporting the CBSD location to the FCC, the SAS is responsible forconverting
    # coordinates from the WGS84 datum to the NAD83 datum.See “REG-Conditional Registration Request Parameters” above.
    height: Optional[Decimal] = None
    # REG-Conditional
    heightType: Optional[HeightTypeEnum] = None
    # Optional
    horizontalAccuracy: Optional[condecimal(lt=Decimal(50))] = None
    # Optional
    verticalAccuracy: Optional[condecimal(lt=Decimal(3))] = None
    # REG-Conditional
    indoorDeployment: Optional[bool] = None
    # REG-Conditional - Optional for Category A CBSD; REG-Conditional for Cat B
    antennaAzimuth: Optional[conint(ge=0, le=359)] = None
    # REG-Conditional - Opt for Cat A; REG-Conditional for Cat B
    antennaDowntilt: Optional[conint(ge=-90, le=90)] = None
    # REG-Conditional
    antennaGain: Optional[conint(ge=-127, le=128)] = None
    # Optional - This parameter is the maximum EIRP in units of dBm/10MHz to be used by this CBSD and shall be no
    # more than the rounded-up FCC certified maximum EIRP. The Value of this parameter is an integer with a value
    # between -127 and +47 (dBm/10MHz) inclusive. If not included, SAS shall set eirpCapability as the rounded up FCC
    # certified maximum EIRP of the CBSD.
    eirpCapability: Optional[conint(ge=-127, le=4)] = None
    # REG-Conditional - Opt for Cat A; REG-Conditional for Cat B
    antennaBeamwitdth: Optional[conint(ge=0, le=360)] = None
    # Optional
    antennaModel: Optional[constr(max_length=128)] = None


class MeasReportType(str, Enum):
    """
    Used to specify the possible choices for the 'meas_capability' parameter of a RegistrationRequest object
    The permitted values are specified in section 7 of <2>
    """
    RECEIVED_POWER_WITHOUT_GRANT = "RECEIVED_POWER_WITHOUT_GRANT"
    RECEIVED_POWER_WITH_GRANT = "RECEIVED_POWER_WITH_GRANT"
    INDOOR_LOSS_USING_GNSS = "INDOOR_LOSS_USING_GNSS"


class GroupTypeEnum(str, Enum):
    """
    Used to specify the possible choices for the 'group_type' parameter of a GroupParam object
    Note that there is currently only one permitted value as of version 1.2.7 of <1>, but it notes that "additional group
    types are expected to be defined in future revisions."
    """
    interferenceCoordination = "INTERFERENCE_COORDINATION"


class GroupParam(BaseModel):
    """
    Object that includes information on CBSD grouping.
    A list of these objects are included as the optional group_param parameter in RegistrationRequest
    Defined in 10.1.4 of <1>

    <1> 8.3.1: Successful Operation of the CBSD Registration Procedure:
        "If the RegistrationRequest object contains a groupingParam parameter containing a GroupParam object having the
        groupType parameter set to "INTERFERENCE_COORDINATION", the CBSD is requesting the SAS to not provide any
        intra-group, inter-CBSD interference coordination between CBSDs sharing the value of the groupId parameter
        provided in the request (Ref [n.8] 96.35(e), 96.41(d)(1)).

        Notes:
            The procedure by which CBSDs determine a common value of groupId, and therefore Interference Coordination
                Group membership, is outside the scope of this specification.
            The CBSD's use of an Interference Coordination Group declares to the SAS that all members of the particular
                Group are using methods defined outside the scope of this specification to manage radio interference
                among themselves.

    All fields are required.
    """
    groupType: GroupTypeEnum
    groupId: str


class ProfessionalInstallerData(BaseModel):
    """
    "The value of this parameter is the data identifying the CPI vouching for the installation parameters included in
    the installationParam value contained in this object"
    A required parameter of the CpiSignedData constructor, which is itself, the unencoded parameter of a
    CpiSignatureData object, which finally, is an optional parameter for RegistrationRequest.
    Defined in 10.1.8 of <1>

    All fields are required.
    The maximum length of cpi_id and cpi_name is 256 octets.
    installation_certification_time is the UTC datetime at which the CPI identified in this object cerified the CBSD's
    installed parameters. It is expressed using the format, YYYY-MM-DDThh:mm:ssZ, as defined by [n.7]
    """
    cpiId: constr(max_length=256)
    cpiName: constr(max_length=256)
    # YYYY-MM-DDThh:mm:ssZ
    # install_certification_time: str
    # The ellipsis indicates that the field is required
    installCertificationTime: str = Field(..., regex=r'\d{4}-[01]\d-[0123]\dT[012]\d:[012345]\d:[012345]\dZ')


class CpiSignedData(BaseModel):
    """
    The un-encoded "encoded_cpi_signed_data" parameter of a Cpi_Signature Data object
    Defined in 10.1.7 in <1>
    All fields are required.

    TODO: Ensure that this object is included in the Cpi_Signature object definition...
    """
    fccId: str
    cbsdSerialNumber: str
    installationParam: InstallationParam
    professionalInstallerData: ProfessionalInstallerData

    def base64_encode(self):
        pass

class CpiSignatureData(BaseModel):
    """
    The CPI is vouching for the parameters in this object. In addition, the digital signature for these parameters is
    included.
    Optional parameter for RegistrationRequest.
    Defined in 10.1.6 of <1>

    protected_header: "The value of this parameter is the BASE64-encoded JOSE [(Javascript Object Signing and
        Encryption)] protected header. This is a JSON object equivalent to the JWT RS256 method or the ES256 method
        described in RFC 7515 [n.19] Section 3. BASE64 encoding is per RFC 4648 (see [n.20]). Valid values are
        equivalent to the JSON: { "typ": "JWT", "alg": "RS256" } or { "typ": "JWT", "alg": "ES256" }"
        Note: The definition specified in 10.1.6 of <1> uses 'smart quotes' (i.e., “typ”), which is invalid JSON.
        Objects of this class use 'straight quotation marks.'
    encoded_cpi_signed_Data: "The value of this parameter is the encoded JOSE payload data
        to be signed by the CPI’s private key.This parameter is calculated by taking the BASE64 encoding of a
        CpiSignedDataobject (see Table 10) according to the procedures in RFC 7515 [n.19], Section 3."
    digital_signature: "The value of this parameter is the CPI digital signature applied to the encodedCpiSignedData
        field.This signature is the BASE64URLencoding of the digital signature, prepared according to the procedures in
        RFC 7515 [n.19] Section 3, using the algorithm as declared in the protectedHeader field."

    "Note: The JOSE JSON Web Signature per RFC-7515 (see [n.19]) is used to ensure data integrity and CPI
    non-repudiation of the signed parameters. The JOSE compact serialization is formed by concatenating the
    protectedHeader, encodedCpiSignedData, and digitalSignature fields with "." Characters, as described in section 3
    of RFC 7515 [n.19]."

    All fields are required.
    """
    protectedHeader: str
    encodedCpiSignedData: str
    digitalSignature: str


class CbsdCategoryEnum(str, Enum):
    """
    Allowed values for the cbsd_category parameter of a RegistrationRequest object, as defined in table 4 of <1>.
    """
    A = "A"
    B = "B"


class RegistrationRequest(BaseModel):
    """
    RegistrationRequest object as defined in section 10.1.1 of <1>

    <1> 8.3.1: CBSD Registration Procedure: "The CBSD then initiates the Registration procedure by sending a
        RegistrationRequestobject(userId, fccId, cbsdSerialNumber, callSign, cbsdCategory, cbsdInfo, airInterface,
        installationParam, measCapability, groupingParam) to the SAS. The fccId, callSign, cbsdSerialNumber, and userId
        parameters identify the CBSD to the SAS. The cbsdCategory, cbsdInfo, airInterface, and installationParam
        parameters provide specific information on the CBSD equipment capabilities. The measCapability parameter
        identifies the measurement reporting capabilities of the CBSD. The optional GroupingParam object requests the
        SAS to enroll the CBSD as a member of one or more Groups."

    """
    # Required
    userId: str
    # Required; TODO: there's a constraint here
    fccId: constr(max_length=19)
    # Required
    cbsdSerialNumber: constr(max_length=64)
    # Optional
    callSign: Optional[str] = None
    # REG-Conditional
    cbsdCategory: Optional[CbsdCategoryEnum] = None
    # Optional
    cbsdInfo: Optional[CbsdInfo] = None
    # REG-Conditional
    airInterface: Optional[AirInterface] = None
    # REG-Conditional
    installationParam: Optional[InstallationParam] = None
    # REG-Conditional
    measCapability: Optional[List[MeasReportType]] = None
    # Optional
    groupingParam: Optional[List[GroupParam]] = None
    # Optional
    cpiSignatureData: Optional[CpiSignatureData] = None


class ResponseCodeEnum(IntEnum):
    """
    Contains the valid response codes for the response_code parameter of a Response object.
    Defined in 10.1.3 of <1>

    The response codes are grouped into the following categories and defined in the following table. The name associated
    with each responseCode parameter is not included in the Response object, but can be attached to a responseCode
    parameter by the CBSD or other network entity for logging or human-involved troubleshooting.
        0: success
        100 – 199: general errors related to the SAS-CBSD protocol
        200 – 299: error events related to the CBSD Registration procedure
        300 – 399: error events related to the Spectrum Inquiry procedure
        400 – 499: error events related to the Grant procedure
        500 – 599: error events related to the Heartbeat procedure
    """
    # "CBSD request is approved by SAS"
    SUCCESS = 0
    # "SAS protocol version used by CBSD is not supported by SAS"
    VERSION = 100
    # "CBSD is blacklisted. This responseCode is returned if the CBSD is under a SAS or FCC enforcement action and is
    # barred from CBRS operation. In general, the CBSD should not try to re-register until actions external to this
    # specification are taken. Note: Blacklisting behavior by the SAS and CBSD is FFS."
    BLACKLISTED = 101
    # "Required parameters missing"
    MISSING_PARAM = 102
    # "One or more parameters have invalid value"
    INVALID_VALUE = 103
    # "There is an error in the certificate used to make the request (e.g. the credential is of the wrong role). Note:
    # Most certificate errors, such as expired or syntactically invalid certificates, will cause errors at the TLS
    # connection."
    CERT_ERROR = 104
    # "A CBSD receiving this responseCode is automatically deregistered by the SAS. The CBSD shall cease all
    # transmissions, terminate all Grants, and consider itself Unregistered. The SAS may include this responseCode
    # parameter in any message. The responseMessage parameter may contain a string describing the reason for
    # deregistration."
    DEREGISTER = 105
    # "Incomplete registration information. The registration process is pending. One or more REG-Conditional parameters
    # have not yet been supplied to the SAS. The CBSD is likely to accomplish a successful registration when the missing
    # registration information is made available to the SAS."
    REG_PENDING = 200
    # "An error has been identified in the grouping parameters of the CBSD."
    GROUP_ERROR = 201
    # "The frequency range indicated in the spectrum inquiry request or grant request is at least partially outside of
    # the CBRS band."
    UNSUPPORTED_SPECTRUM = 300
    # "Requested operation parameters cause too much interference. This responseCode value indicates that the Grant
    # request is unlikely to be successful if retried by the CBSD."
    INTERFERENCE = 400
    # "Conflict with an existing Grant of the same CBSD. The CBSD should be able to remediate this using the data
    # returned in the responseData structure, by synchronizing its Grant state with the SAS and relinquishing any
    # out-of-sync Grants."
    GRANT_CONFLICT = 401
    # "The Grant is terminated. This condition occurs if, for example, incumbent status has changed permanently causing
    # the current Grant to terminate. The CBSD shall terminate radio operation by turning off its radio transmission
    # associated with this Grant within 60 seconds after the value of the transmitExpireTime parameter expires, in
    # accordance with part 96.39(c)(2) (ref. [n.8]). The Grant is considered terminated by the SAS, but the CBSD may
    # relinquish the Grant. If the operationParam parameter is included in the HeartbeatResponse object, the CBSD should
    # consider it as a recommendation by the SAS to obtain a new Grant using the included operational parameter values,
    # and may request a new Grant using those operational parameters."
    TERMINATED_GRANT = 500
    # "The Grant is suspended. This condition occurs if incumbent status has changed temporarily. The CBSD shall
    # terminate radio operation by turning off its radio transmission associated with this Grant within 60 seconds
    # after the value of the transmitExpireTime parameter expires, in accordance with part 96.39(c)(2) (ref. [n.8]).
    # In such a case the CBSD may continue to send HeartbeatRequest objects and waiting until the Grant is re-enabled,
    # or may relinquish the Grant and request another. If the operationParam parameter is included in the
    # HeartbeatResponse object, the CBSD should consider it as a recommendation by the SAS to obtain a new Grant using
    # the included operational parameter values, and may request a new Grant using those parameters."
    SUSPENDED_GRANT = 501
    # "The Grant state is out of sync between the CBSD and the SAS. The CBSD shall turn off the radio transmission
    # associated with this Grant within 60 seconds from receiving this responseCode value, in accordance with Part
    # 96.39(c)(2) (ref. [n.8]), and shall relinquish this Grant."
    UNSYNC_OF_PARAM = 502


class Response(BaseModel):
    """
    A data object that "includes information on whether the corresponding CBSD request is approved or disapproved for a
    response," defined in 10.2.2 of <1>.
    Required parameter of RegistrationResponse.
    """
    # Required
    responseCode: ResponseCodeEnum
    # Optional
    responseMessage: Optional[str] = None
    # Optional
    # If response_code is 100, the error data is a list of Protocol versions supported by the SAS administrator;
    # if 102, a list of missing parameters
    # if 103, a list of parameter names with invalid values
    # if 200, a list of missing registration parameters
    # if 401, the Grant ID of an existing Grant that causes the conflict (also in List[str] format)
    # the response_data is not present for any other response_code value
    responseData: Optional[List[str]] = None


class RegistrationResponse(BaseModel):
    """
    RegistrationResponse object as defined in 10.2.1 of <1>
    """
    # Required
    response: Response
    # Conditional; included IFF response_code indicates SUCCESS
    cbsdId: Optional[constr(max_length=256)] = None
    # Optional
    measReportConfig: Optional[List[MeasReportType]] = None


class FrequencyRange(BaseModel):
    """
    A data object that "describes the spectrum for which the CBSD seeks information on spectrum availability."
    Defined in section 10.3.2 of <1>.
    Required parameter of SpectrumInquiryRequest.
    All fields are required
    """
    lowFrequency: condecimal(gt=Decimal(0))
    highFrequency: condecimal(gt=Decimal(0))


class SpectrumInquiryRequest(BaseModel):
    """
    SpectrumInquiryRequest object as defined in 10.3.1 of <1>
    """
    # Required
    cbsdId: str
    # Required
    inquiredSpectrum: FrequencyRange
    # Conditional; the document does not specify when this parameter should be included
    measReport: MeasReportType


class ChannelTypeEnum(str, Enum):
    """
    Contains the valid choices for the channelType parameter of an AvailableChannel object.
    Defined in 10.4.2 of <1>
    """
    PAL = "PAL"
    GAA = "GAA"


class AvailableChannel(BaseModel):
    """
    "A data object that describes a channel that is available for the CBSD"
    Defined in 10.4.2 of <1>
    Required as available_channel parameter of SpectrumInquiryResponse IFF the inquiry is successful
    """
    # Required
    frequencyRange: FrequencyRange
    # Req
    channelType: ChannelTypeEnum
    # Req; "the regulatory rule used to generate this response, e.g., 'FCC_PART_96'."
    ruleApplied: str
    # Optional; Maximum EIRP likely to be permitted for a Grant on this frequencyRange, given the CBSD registration
    # parameters, including location, antenna orientation and antenna pattern. The maximum EIRP is in the units of
    # dBm/MHz and is an integer or a floating point value between -137 and +37 (dBm/MHz) inclusive.
    maxEirp: Optional[Union[conint(ge=-137, le=37), confloat(ge=-137.0, le=37.0)]] = None


class SpectrumInquiryResponse(BaseModel):
    """
    SpectrumInquiryResponse object as defined in 10.4.1 of <1>
    """
    # Required
    response: Response
    # Conditional; included IFF the request contains a valid CBSD Identity
    cbsdId: Optional[str] = None
    # Conditional; included IFF the Spectrum Inquiry is successful
    availableChannel: Optional[List[AvailableChannel]] = None


class OperationParam(BaseModel):
    """
    "This data object includes operation parameters of the requested Grant."
    Required param for GrantRequest.
    All fields are required.
    """
    maxEirp: Union[conint(ge=-137, le=37), confloat(ge=-137.0, le=37.0)]
    operationFrequencyRange: FrequencyRange


class GrantRequest(BaseModel):
    """
    GrantRequest object as defined in 10.5.1 of <1>

    "A GrantRequest object contains operating parameters that the CBSD plans to operate with. Operation parameters
    include a continuous segment of spectrum and the maximum EIRP."
    """
    # Req
    cbsdId: str
    # Req
    operationParam: OperationParam
    # Cond; the document does not specify when this parameter should be included
    measReport: Optional[MeasReportType] = None


class GrantResponse(BaseModel):
    """
    GrantResponse object as defined in 10.6.1 of <1>

    grantExpireTime: "The grantExpireTime indicates the time when the Grant associated with the grantId expires. This
    parameter is UTC time expressed in the format, YYYY-MM-DDThh:mm:ssZ as defined by [n.7]. This parameter shall be
    included if and only if the responseCode parameter indicates SUCCESS. If the channelType parameter is included in
    this object and the value is set to 'PAL', the grantExpireTime parameter shall be set to the value that does not
    extend beyond the licenseExpiration of the corresponding PAL recorded in the PAL Database [n.23]."
    """
    # Req
    response: Response
    # Conditional; included IFF cbsdId param in GrantRequest is a valid CBSD identity
    cbsdId: Optional[str] = None
    # Cond; ID provided by the SAS for this grant, included IFF the Grant request is approved
    grantId: Optional[str] = None
    # Cond; see docstring
    grantExpireTime: Optional[str] = None
    # Cond; included IFF response_code indicates SUCCESS
    heartbeatInterval: Optional[conint(gt=0)] = None
    # Optional
    measReportConfig: Optional[List[MeasReportType]] = None
    # Optional
    operationParam: Optional[OperationParam] = None
    # Cond; included IFF response_code indicates SUCCESS
    channelType: Optional[ChannelTypeEnum] = None


class OperationStateEnum(str, Enum):
    """
    Defines the possible values of the required operationState parameter of a HeartbeatRequest object
    """
    AUTHORIZED = "AUTHORIZED"
    GRANTED = "GRANTED"


class RcvdPowerMeasReport(BaseModel):
    """
    A data object containing information about the "Recived Power" measurement, a "Measurement of the radio frequency
    energy received over a set of frequency ranges during a measurement interval with results reported to a SAS for each
    of the frequency ranges in terms of effective received power for each frequency range."

    Defined in table 7.1-2 of section 7.1.1 and table 7.1-4 of section 7.1.2 of <2> as RcvdPowerMeasReport

    7.1.1: RECEIVED_POWER_WITHOUT_GRANT:
        "Semantics: Received Power can be measured and reported when the CBSD does
        not have a spectrum grant from the SAS. If this measurement report capability is indicated by the SAS to the
        CBSD, the CBSD performs and reports Received Power measurements over the entire CBRS band in segments that do not
        exceed 10 MHz per measurement report. Those measurement reports are sent to the SAS in the first Spectrum Inquiry
        Request message and first Grant Request message.

        A given CBSD can include unsolicited (i.e., even if SAS did not send measReportConfig to CBSD) measReport object
        in spectrumInquiryRequest object or grantRequest object, if the CBSD included measCapability parameter in
        registrationRequest object to SAS with a value of RECEIVED_POWER_WITHOUT_GRANT.

        A given CBSD must include measReport parameter in spectrumInquiryRequest object, if SAS included measReportConfig
        parameter in registrationResponse object to CBSD."

    7.1.2: RECEIVED_POWER_WITH_GRANT:
        "Semantics: Received Power can be measured and reported when the CBSD has a
        spectrum grant from the SAS. If this measurement report capability is indicated by the SAS to the CBSD,
        the CBSD performs and reports Received Power measurements over one or more frequency ranges that do not exceed 10
        MHz per measurement report. The measurement report(s) are sent to the SAS in the subsequent Heartbeat Request
        message.

        A given CBSD can include unsolicited (i.e., even if SAS did not send measReportConfig to CBSD) measReport object
        in spectrumInquiryRequest or heartbeatRequest object, if the CBSD included measCapability parameter in
        registrationRequest object to SAS with a value of RECEIVED_POWER_WITH_GRANT.

        A given CBSD must include measReport parameter in the first heartbeatRequest object, if SAS included
        measReportConfig parameter in either grantResponse or heartbeatResponse objects to CBSD."

    All fields are required
    """
    measFrequency: conint(gt=0)
    measBandwidth: conint(gt=0)
    # TODO: Verify that this param given in units of dBm is (possibly) a FP quantity; Also, that the range is inclusive.
    measRcvdPower: confloat(ge=-100, le=-25)


class IndoorLossTechnologyTypeEnum(str, Enum):
    """
    Contains the permitted values for the "technologyType" parameter of an IndoorLossGnssMeasReport object.
    Defined in table 7.2-2 of section 7.2.1 of <2>
    """
    GPS_L1 = "GPS_L1"
    GPS_L2 = "GPS_L2"
    GPS_L5 = "GPS_L5"
    GLONASS_G1 = "GLONASS_G1"
    GLONASS_G2 = "GLONASS_G2"
    GLONASS_G3 = "GLONASS_G3"
    GALILEO_E1 = "GALILEO_E1"
    GALILEO_E5A = "GALILEO_E5A"
    GALILEO_E5B = "GALILEO_E5B"
    GALILEO_E6 = "GALILEO_E6"
    BEIDOU_B1 = "BEIDOU_B1"
    BEIDOU_B2 = "BEIDOU_B2"
    BEIDOU_B3 = "BEIDOU_B3"


class IndoorLossGnssMeasReport(BaseModel):
    """
    A data object containing information about the "Indoor Loss" measurement, a "Measurement of indoor loss at physical
    location of CBSD. This indoor attenuation data will be sent to a SAS to provide power and frequency management of the CBSD"

    Defined in table 7.2-2 of section 7.2.1 of <2>

    7.2.1: INDOOR_LOSS_USING_GNSS:
        "Semantics: A GNSS receiver along with its antenna, embedded inside a CBSD
        measures received power levels at 1575.42 MHz. GNSS power levels outdoors are well regulated and are maintained
        uniformly at -128.5 dBm into a 0 dBic antenna at ground level to 5 degrees elevation angle. By using an extremely
        sensitive GPS L1 C/A code receiver, this method can measure indoor losses up to 46.5 dB.

        This does not fulfill the requirement of Part 96.39(d) but can provide supplemental information to the SAS.

        The indoor loss measurements are sent to the SAS upon request."

    All fields are required.
    """
    indoorLoss: confloat(ge=0, le=70)
    azimuthAngleWithGnss: conint(ge=0, le=359)
    elevationAngleWithGnss: conint(ge=0, le=90)
    technologyType: IndoorLossTechnologyTypeEnum


MeasReport = Union[List[RcvdPowerMeasReport], List[IndoorLossGnssMeasReport]]


class HeartbeatRequest(BaseModel):
    """
    HeartbeatRequest object as defined in 10.7.1 of <1>
    """
    # Required
    cbsdId: str
    # Req
    grantId: str
    # Req
    operationState: OperationStateEnum
    # Opt
    grantRenew: Optional[bool] = None
    # Conditional; see 8.6 for inclusion rules
    measReport: Optional[MeasReport] = None


class HeartbeatResponse(BaseModel):
    """
    HeartbeatResponse object as defined in 10.8.1. of <1>
    """
    # Req
    response: Response
    # Req
    transmitExpireTime: str = Field(..., regex=r'\d{4}-[01]\d-[0123]\dT[012]\d:[012345]\d:[012345]\dZ')
    # Cond; This parameter is included if and only if  the cbsdId parameter in the HeartbeatRequest object contains a
    # valid CBSD identity. If included, the SAS shall set this parameter to the value of thein the corresponding
    # HeartbeatRequest object.
    cbsdId: Optional[str] = None
    # Cond; included iff "the grantId parameter in the HeartbeatRequest object contains a valid Grant identity. If
    # included, the SAS shall set this parameter to the value of the grantId parameter in the corresponding
    # HeartbeatRequest object"
    grantId: Optional[str] = None
    # Cond; "Required if the responseCode parameter indicates SUCCESS or SUSPENDED_GRANT and the grantRenew parameter
    # was included and set to True in the corresponding HeartbeatRequest object. This parameter may be included at
    # other times by SAS choice. When included, if the channelType of this Grant is “PAL”, this parameter shall be
    # set to the value that does not extend beyond the licenseExpiration of the corresponding PAL recorded in the PAL
    # Database [n.23]."
    grantExpireTime: Optional[str] = None
    # Optional
    heartbeatInterval: Optional[conint(gt=0)] = None
    # Optional
    operationParam: Optional[OperationParam] = None
    # Optional
    measReportConfig: Optional[List[MeasReportType]]


class RelinquishmentRequest(BaseModel):
    """
    RelinquishmentRequest object as defined in 10.9.1 of <1>
    All fields are required.
    """
    cbsdId: str
    grantId: str


class RelinquishmentResponse(BaseModel):
    """
    RelinquishmentResponse object as defined in 10.10.1 of <1>
    """
    response: Response
    # Conditional; "Included IFF the cbsdId parameter in the RelinquishmentRequest object
    # contains a valid CBSD identity. If included, the SAS shall set this parameter to the value of the cbsdId
    # parameter in the corresponding RelinquishmentRequest object"
    cbsdId: str
    # Conditional; "Included IFF the grantId parameter in the RelinquishmentRequest object contains a valid Grant
    # identity. If included, the SAS shall set this parameter to the value of the grantId parameter in the
    # corresponding RelinquishmentRequest object"
    grantId: str


class DeregistrationRequest(BaseModel):
    """
    DeregistrationRequest object as defined in 10.11.1 of <1>
    All fields are required.
    """
    cbsdId: str


class DeregistrationResponse(BaseModel):
    """
    DeregistrationResponse object as defined in 10.12.1 of <1>
    """
    response: Response
    # Conditional; "Included IFF the cbsdId parameter in the DeregistrationRequest object
    # contains a valid CBSD identity. If included, the SAS shall set this parameter to the value of the cbsdId
    # parameter in the corresponding DeregistrationRequest object"
    cbsdId: str


# Type aliases for the JSON Arrays that are used as inputs and outputs to each of the SAS functions.
# The JSON Array names and format is specified in section 9 and table 1 of <1>.
# Each of the following SAS-CBSD message types are sent as JSON (or a Python dictionary), with a single key-value pair.
# The single key for a given message type is named f"{sas_method_name}Request" or f"{sas_method_name}Response", where
# sas_method_name is one of the following: registration, spectrumInquiry, grant, heartbeat, relinquishment, or
# deregistration. The single value for a given message type is a JSON Array (or Python list) of the following types:
# RegistrationRequest, RegistrationResponse, SpectrumInquiryRequest, SpectrumInquiryResponse, GrantRequest,
# GrantResponse, HeartbeatRequest, HeartbeatResponse, RelinquishmentRequest, RelinquishmentResponse,
# DeregistrationRequest, DeregistrationResponse
registrationRequest = Dict[str, List[RegistrationRequest]]
registrationResponse = Dict[str, List[RegistrationResponse]]
spectrumInquiryRequest = Dict[str, List[SpectrumInquiryRequest]]
spectrumInquiryResponse = Dict[str, List[SpectrumInquiryResponse]]
grantRequest = Dict[str, List[GrantRequest]]
grantResponse = Dict[str, List[GrantResponse]]
heartbeatRequest = Dict[str, List[HeartbeatRequest]]
heartbeatResponse = Dict[str, List[HeartbeatResponse]]
relinquishmentRequest = Dict[str, List[RelinquishmentRequest]]
relinquishmentResponse = Dict[str, List[RelinquishmentResponse]]
deregistrationRequest = Dict[str, List[DeregistrationRequest]]
deregistrationResponse = Dict[str, List[DeregistrationResponse]]


# The following classes are used in SAS-SAS interactions and are derived from the definitions given in <3>
# See section 5.2 of <3> for a description of SAS-SAS Record Exchanges, and in particular, see section 5.2.1: SAS-SAS
# exchange entities and IDs for a description of each Protocol Exchange Entity.
# The following CBRS Entities are defined in Table 1 of <3>:
# [Name of CBRS Entity] with ID of the form: "
# "SAS Administrators" : "sas_admin/$ADMINISTRATOR_ID"
# "SAS Implementations" : "sas_impl/$ADMINISTRATOR_ID/$SAS_IMPLEMENTATION"
# "CBSDs" : "cbsd/$CBSD_REFERENCE_ID"
# "ESC Sensors" : "esc_sensor/$ADMINISTRATOR_ID/$SENSOR_ID"
# "Zones" : "zone/$CREATOR/$ZONE_ID"
# "Coordination events" : "coordination/$ADMINISTRATOR_ID/$EVENT_ID"
# Note: "the symbol “$” before any token refers to a token chosen by the entity issuing the token."
#
# Notes:
# 1) "All messages in the [SAS-SAS] Protocol are extensible using JSON extension mechanisms."
# 2) "In every message and object, all fields are optional unless specifically described as required.


class MessageAggregation(BaseModel):
    """
    Defined in Table 3 of <3>

    7.3: "Multiple required data elements may be placed into a single request for a push exchange, and similarly,
    in a pull exchange, the response message may contain aggregated data elements.

    When using the individual record GET or POST methods described in Table 2, the SAS shall encode message payloads
    as a JSON object. When responding to the time-range record GET or POST methods, the SAS shall encode message
    payloads as a MessageAggregation object of the type in Table 3. This payload includes an array of JSON objects.
    The elements in such an array will be objects of the requested (or provided) message type.

    In the case of error conditions in the SAS-SAS requests, the SAS shall use the appropriate HTTP status codes and
    an empty response. For example, an error in constructing the appropriate URL or a URL unsupported by the target
    SAS should be answered by a 404 status code. A syntactically correct request for which the SAS has no data shall
    produce the response of an empty JSON object (equivalent to “{}”)."

    All fields are required.
    """
    startTime: str = Field(..., regex=r'\d{4}-[01]\d-[0123]\dT[012]\d:[012345]\d:[012345]\dZ')
    endTime: str = Field(..., regex=r'\d{4}-[01]\d-[0123]\dT[012]\d:[012345]\d:[012345]\dZ')
    recordData: List[Any]


class ContactInformation(BaseModel):
    """
    ContactInformation object as defined in 8.1.1 of <3>
    """
    contactType: Optional[str]
    name: Optional[str]
    # Format: should follow the E.123 ITU-T recommendation
    phoneNumber: Optional[List[str]]
    # Format: should follow the E.123 ITU-T recommendation
    email: Optional[List[str]]
    address: Optional[List[str]]
    note: Optional[List[str]]


class SasAdministrator(BaseModel):
    """
    SasAdministrator object as defined in 8.1 of <3>.
    """
    id: Optional[str] = Field(default=None, regex=r'sas_admin/.*')
    name: Optional[str]
    contactInformation: Optional[List[ContactInformation]]


class FCCInformation(BaseModel):
    """
    FCCInformation object as defined in table 7 (8.2.1) of <3>
    """
    certificationId: Optional[str]
    certificationDate: Optional[str] = Field(regex=r'\d{4}-[01]\d-[0123]\d')
    certificationExpiration: Optional[str] = Field(regex=r'\d{4}-[01]\d-[0123]\d')
    certificationConditions: Optional[str]
    frn: Optional[str]
    sasPhase: str = Field(regex=r'1|2')


class SasImplementation(BaseModel):
    """
    SasImplementation object as defined in table 6 (section 8.2) of <3>
    """
    id: Optional[str] = Field(default=None, regex=r'sas_admin/.*/.*')
    name: Optional[str]
    # Reference: ID of a SasAdministrator object
    administratorId: Optional[str]
    contactInformation: Optional[List[ContactInformation]]
    # X.509 key
    publicKey: Optional[str]
    fccInformation: Optional[FCCInformation]
    url: Optional[str]


class GrantData(BaseModel):
    """
    GrantData object as defined in table 9 (8.3) of <3>
    """
    id: Optional[str]
    terminated: Optional[bool]
    operationParam: Optional[OperationParam]
    requestedOperationParam: Optional[OperationParam]
    channelType: Optional[ChannelTypeEnum]
    grantExpireTime: Optional[str] = Field(regex=r'\d{4}-[01]\d-[0123]\dT[012]\d:[012345]\d:[012345]\dZ')


class CbsdData(BaseModel):
    """
    CbsdData object as defined in table 8 (8.3) of <3>

    "The following parameters of the RegistrationRequest object included in the CbsdData object shall be exchanged as
    they are registered:
        fccId, cbsdCategory, airInterface, installationParam (see below), measCapability,
    groupingParam (see below).
    These parameters (and any others) are optional:
        userId, cbsdSerialNumber, cbsdInfo, callSign"
    "The following parameters of the InstallationParam object included in the CbsdData object shall be exchanged. Any
    other parameters are optional:
        latitude, longitude, height, heightType, indoorDeployment, antennaAzimuth,
    antennaGain, antennaBeamwidth"
    "The following parameters of the GroupParam object shall be exchanged as they are registered when the groupType
    parameter of that object is equal to “INTERFERENCE_COORDINATION” or any other group type and accompanying group
    information identified as SAS-Essential data. Otherwise, the GroupParam objects are not required to be exchanged.
        groupType, groupId, other accompanying data"

    "Other fields from the RegistrationRequest object may be optionally included in this message as registered. Fields
    not required to be exchanged in this protocol, but required by syntactic constraints of the SAS-CBSD protocol [n.10]
    to be present or carry a particular format may be populated using an empty placeholder or a dummy value."

    "The following parameters of the GrantData objects included in the CbsdData object shall be exchanged as they are
    allocated for use by the CBSD (that is, a successful Grant response has been returned for that CBSD in response
    to a Grant procedure containing these OperationParamdata elements), and the Grant has not subsequently been
    terminated.
        grantExpireTime, operationParam (see below), channelType

    In addition, requestedOperationParam shall also be exchanged to facilitate operations described in [n.8]
    R2-SGN-16. The following parameters of the OperationParam objects included in the CbsdData object within the
    grants parameter shall be exchanged as they are allocated.
        maxEirp, operationFrequencyRange (including both lowFrequency and highFrequency data elements)
    """
    # see <3>
    id: Optional[str] = Field(regex=r'cbsd/.*/[abcdefABCDEF\d]{40}')
    # TODO: Specify in some way the following:
    registration: Optional[registrationRequest]
    grants: Optional[List[GrantData]]

