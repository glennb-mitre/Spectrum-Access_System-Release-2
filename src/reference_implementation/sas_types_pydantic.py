"""
This module contains class definitions for objects used in SAS-CBSD interactions according to the following documents:
<1> WINNF-TS-0016-V1.2.7 SAS to CBSD Technical Specification
<2> WINNF-SSC-0002 v6.0.0.0 Signaling Protocols and Procedures for Citizens Broadband Radio Service (CBRS):
    WInnForum Recognized CBRS Air Interfaces and Measurements
*2  <1> cites <2> for several object field definitions

Note 1: <1> Marks each parameter's requirement level with (R)equired, (O)ptional, or (C)onditional.
In the case of Registration Request Message objects, some parameters are marked as "REG-Conditional," indicating that
"the parameter is required by the SAS to complete the CBSD registration process, but may be omitted from the
[Registration_Request] object. If not included in the RegistrationRequest object, the parameter, to the extent that it
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


class Cbsd_Info(BaseModel, extra=Extra.allow):
    """
    Optional argument for Registration_Request
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
    software_version: Optional[constr(max_length=64)] = None
    # Hardware version of the CBSD
    hardware_version: Optional[constr(max_length=64)] = None
    # Firmware version of the CBSD
    firmware_version: Optional[constr(max_length=64)] = None


class Radio_Technology_Enum(str, Enum):
    """
    Used to specify the possible choices for the 'radio_technology' parameter of an Air_Interface object
    The peritted values are specified in section 6 of <2>
    """
    E_UTRA = "E_UTRA"
    CAMBRIUM_NETWORKS = "CAMBRIUM_NETWORKS"
    FOURG_BBW_SAA_1 = "4G_BBW_SAA_1"
    NR = "NR"
    DOODLE_CBRS = "DOODLE_CBRS"


class Air_Interface(BaseModel):
    """
    A data object that includes information on the air interface technology of the CBSD.
    REG-Conditional for Registration_Request
    Defined in 10.1.2 of <1>
    """
    # REG-Conditional
    radio_technology: Radio_Technology_Enum


class Height_Type_Enum(str, Enum):
    """
    Used to specify the possible choices for the 'height_type' parameter of an Installation_Param object
    """
    agl = "AGL" # measured relative to ground level
    amsl = "AMSL" # measured relative to mean sea level


class Installation_Param(BaseModel):
    """
    A data object that includes information on CBSD installation.
    REG-Conditional for Registration_Request
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
    height_type: Optional[Height_Type_Enum] = None
    # Optional
    horizontal_accuracy: Optional[condecimal(lt=Decimal(50))] = None
    # Optional
    vertical_accuracy: Optional[condecimal(lt=Decimal(3))] = None
    # REG-Conditional
    indoor_deployment: Optional[bool] = None
    # REG-Conditional - Optional for Category A CBSD; REG-Conditional for Cat B
    antenna_azimuth: Optional[conint(ge=0, le=359)] = None
    # REG-Conditional - Opt for Cat A; REG-Conditional for Cat B
    antenna_downtilt: Optional[conint(ge=-90, le=90)] = None
    # REG-Conditional
    antenna_gain: Optional[conint(ge=-127, le=128)] = None
    # Optional - This parameter is the maximum EIRP in units of dBm/10MHz to be used by this CBSD and shall be no
    # more than the rounded-up FCC certified maximum EIRP. The Value of this parameter is an integer with a value
    # between -127 and +47 (dBm/10MHz) inclusive. If not included, SAS shall set eirpCapability as the rounded up FCC
    # certified maximum EIRP of the CBSD.
    eirp_capability: Optional[conint(ge=-127, le=4)] = None
    # REG-Conditional - Opt for Cat A; REG-Conditional for Cat B
    antenna_beamwitdth: Optional[conint(ge=0, le=360)] = None
    # Optional
    antenna_model: Optional[constr(max_length=128)] = None


class Meas_Report_Type(str, Enum):
    """
    Used to specify the possible choices for the 'meas_capability' parameter of a Registration_Request object
    The permitted values are specified in section 7 of <2>
    """
    RECEIVED_POWER_WITHOUT_GRANT = "RECEIVED_POWER_WITHOUT_GRANT"
    RECEIVED_POWER_WITH_GRANT = "RECEIVED_POWER_WITH_GRANT"
    INDOOR_LOSS_USING_GNSS = "INDOOR_LOSS_USING_GNSS"


class Group_Type_Enum(str, Enum):
    """
    Used to specify the possible choices for the 'group_type' parameter of a Group_Param object
    Note that there is currently only one permitted value as of version 1.2.7 of <1>, but it notes that "additional group
    types are expected to be defined in future revisions."
    """
    interference_coordination = "INTERFERENCE_COORDINATION"


class Group_Param(BaseModel):
    """
    Object that includes information on CBSD grouping.
    A list of these objects are included as the optional group_param parameter in Registration_Request
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
    group_type: Group_Type_Enum
    group_id: str


class Professional_Installer_Data(BaseModel):
    """
    "The value of this parameter is the data identifying the CPI vouching for the installation parameters included in
    the installationParam value contained in this object"
    A required parameter of the Cpi_Signed_Data constructor, which is itself, the unencoded parameter of a
    Cpi_Signature_Data object, which finally, is an optional parameter for Registration_Request.
    Defined in 10.1.8 of <1>

    All fields are required.
    The maximum length of cpi_id and cpi_name is 256 octets.
    installation_certification_time is the UTC datetime at which the CPI identified in this object cerified the CBSD's
    installed parameters. It is expressed using the format, YYYY-MM-DDThh:mm:ssZ, as defined by [n.7]
    """
    cpi_id: constr(max_length=256)
    cpi_name: constr(max_length=256)
    # YYYY-MM-DDThh:mm:ssZ
    # install_certification_time: str
    # The ellipsis indicates that the field is required
    install_certification_time: str = Field(..., regex=r'\d{4}-[01]\d-[0123]\dT[012]\d:[012345]\d:[012345]\dZ')


class Cpi_Signed_Data(BaseModel):
    """
    The un-encoded "encoded_cpi_signed_data" parameter of a Cpi_Signature Data object
    Defined in 10.1.7 in <1>
    All fields are required.
    """
    fcc_id: str
    cbsd_serial_number: str
    installation_param: Installation_Param
    professional_installer_data: Professional_Installer_Data

    def base64_encode(self):
        pass

class Cpi_Signature_Data(BaseModel):
    """
    The CPI is vouching for the parameters in this object. In addition, the digital signature for these parameters is
    included.
    Optional parameter for Registration_Request.
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
    protected_header: str
    encoded_cpi_signed_data: str
    digital_signature: str


class Cbsd_Category_Enum(str, Enum):
    """
    Allowed values for the cbsd_category parameter of a RegistrationRequest object, as defined in table 4 of <1>.
    """
    A = "A"
    B = "B"


class Registration_Request(BaseModel):
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
    user_id: str
    # Required
    fcc_id: str
    # Required
    cbsd_serial_number: str
    # Optional
    call_sign: Optional[str] = None
    # REG-Conditional
    cbsd_category: Optional[Cbsd_Category_Enum] = None
    # Optional
    cbsd_info: Optional[Cbsd_Info] = None
    # REG-Conditional
    air_interface: Optional[Air_Interface] = None
    # REG-Conditional
    installation_param: Optional[Installation_Param] = None
    # REG-Conditional
    meas_capability: Optional[List[Meas_Report_Type]] = None
    # Optional
    grouping_param: Optional[List[Group_Param]] = None
    # Optional
    cpi_signature_data: Optional[Cpi_Signature_Data] = None


class Response_Code_Enum(IntEnum):
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
    Required parameter of Registration_Response.
    """
    # Required
    response_code: Response_Code_Enum
    # Optional
    response_message: Optional[str] = None
    # Optional
    # If response_code is 100, the error data is a list of Protocol versions supported by the SAS administrator;
    # if 102, a list of missing parameters
    # if 103, a list of parameter names with invalid values
    # if 200, a list of missing registration parameters
    # if 401, the Grant ID of an existing Grant that causes the conflict (also in List[str] format)
    # the response_data is not present for any other response_code value
    response_data: Optional[List[str]] = None


class Registration_Response(BaseModel):
    """
    RegistrationResponse object as defined in 10.2.1 of <1>
    """
    # Required
    response: Response
    # Conditional; included IFF response_code indicates SUCCESS
    cbsd_id: Optional[constr(max_length=256)] = None
    # Optional
    meas_report_config: Optional[List[Meas_Report_Type]] = None


class Frequency_Range(BaseModel):
    """
    A data object that "describes the spectrum for which the CBSD seeks information on spectrum availability."
    Defined in section 10.3.2 of <1>.
    Required parameter of Spectrum_Inquiry_Request.
    All fields are required
    """
    low_frequency: condecimal(gt=Decimal(0))
    high_frequency: condecimal(gt=Decimal(0))


class Spectrum_Inquiry_Request(BaseModel):
    """
    SpectrumInquiryRequest object as defined in 10.3.1 of <1>
    """
    # Required
    cbsd_id: str
    # Required
    inquired_spectrum: Frequency_Range
    # Conditional; the document does not specify when this parameter should be included
    meas_report: Meas_Report_Type


class Channel_Type_Enum(str, Enum):
    """
    Contains the valid choices for the channel_type parameter of an Available_Channel object.
    Defined in 10.4.2 of <1>
    """
    PAL = "PAL"
    GAA = "GAA"


class Available_Channel(BaseModel):
    """
    "A data object that describes a channel that is available for the CBSD"
    Defined in 10.4.2 of <1>
    Required as available_channel parameter of Spectrum_Inquiry_Response IFF the inquiry is successful
    """
    # Required
    frequency_range: Frequency_Range
    # Req
    channel_type: Channel_Type_Enum
    # Req; "the regulatory rule used to generate this response, e.g., 'FCC_PART_96'."
    rule_applied: str
    # Optional; Maximum EIRP likely to be permitted for a Grant on this frequencyRange, given the CBSD registration
    # parameters, including location, antenna orientation and antenna pattern. The maximum EIRP is in the units of
    # dBm/MHz and is an integer or a floating point value between -137 and +37 (dBm/MHz) inclusive.
    max_eirp: Optional[Union[conint(ge=-137, le=37), confloat(ge=-137.0, le=37.0)]] = None


class Spectrum_Inquiry_Response(BaseModel):
    """
    SpectrumInquiryResponse object as defined in 10.4.1 of <1>
    """
    # Required
    response: Response
    # Conditional; included IFF the request contains a valid CBSD Identity
    cbsd_id: Optional[str] = None
    # Conditional; included IFF the Spectrum Inquiry is successful
    available_channel: Optional[List[Available_Channel]] = None


class Operation_Param(BaseModel):
    """
    "This data object includes operation parameters of the requested Grant."
    Required param for Grant_Request.
    All fields are required.
    """
    max_eirp: Union[conint(ge=-137, le=37), confloat(ge=-137.0, le=37.0)]
    operation_frequency_range = Frequency_Range


class Grant_Request(BaseModel):
    """
    GrantRequest object as defined in 10.5.1 of <1>

    "A GrantRequest object contains operating parameters that the CBSD plans to operate with. Operation parameters
    include a continuous segment of spectrum and the maximum EIRP."
    """
    # Req
    cbsd_id: str
    # Req
    operation_param: Operation_Param
    # Cond; the document does not specify when this parameter should be included
    meas_report: Optional[Meas_Report_Type] = None


class Grant_Response(BaseModel):
    """
    GrantResponse object as defined in 10.6.1 of <1>

    grant_expire_time: "The grantExpireTime indicates the time when the Grant associated with the grantId expires. This
    parameter is UTC time expressed in the format, YYYY-MM-DDThh:mm:ssZ as defined by [n.7]. This parameter shall be
    included if and only if the responseCode parameter indicates SUCCESS. If the channelType parameter is included in
    this object and the value is set to 'PAL', the grantExpireTime parameter shall be set to the value that does not
    extend beyond the licenseExpiration of the corresponding PAL recorded in the PAL Database [n.23]."
    """
    # Req
    response: Response
    # Conditional; included IFF cbsd_id param in Grant_Request is a valid CBSD identity
    cbsd_id: Optional[str] = None
    # Cond; ID provided by the SAS for this grant, included IFF the Grant request is approved
    grant_id: Optional[str] = None
    # Cond; see docstring
    grant_expire_time: Optional[str] = None
    # Cond; included IFF response_code indicates SUCCESS
    heartbeat_interval: Optional[conint(gt=0)] = None
    # Optional
    meas_report_config: Optional[List[Meas_Report_Type]] = None
    # Optional
    operation_param: Optional[Operation_Param] = None
    # Cond; included IFF response_code indicates SUCCESS
    channel_type: Optional[Channel_Type_Enum] = None


class Operation_State_Enum(str, Enum):
    """
    Defines the possible values of the required operation_state parameter of a Heartbeat_Request object
    """
    AUTHORIZED = "AUTHORIZED"
    GRANTED = "GRANTED"


class Rcvd_Power_Meas_Report(BaseModel):
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
    meas_frequency: conint(gt=0)
    meas_bandwidth: conint(gt=0)
    # TODO: Verify that this param given in units of dBm is (possibly) a FP quantity; Also, that the range is inclusive.
    meas_rcvd_power: confloat(ge=-100, le=-25)


class Indoor_Loss_Technology_Type_Enum(str, Enum):
    """
    Contains the permitted values for the "technology_type" parameter of an Indoor_Loss_GNSS_Meas_Report object.
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


class Indoor_Loss_GNSS_Meas_Report(BaseModel):
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
    indoor_loss: confloat(ge=0, le=70)
    azimuth_angle_with_gnss: conint(ge=0, le=359)
    elevation_angle_with_gnss: conint(ge=0, le=90)
    technology_type: Indoor_Loss_Technology_Type_Enum


Meas_Report = Union[List[Rcvd_Power_Meas_Report], List[Indoor_Loss_GNSS_Meas_Report]]


class Heartbeat_Request(BaseModel):
    """
    HeartbeatRequest object as defined in 10.7.1 of <1>
    """
    # Required
    cbsd_id: str
    # Req
    grant_id: str
    # Req
    operation_state: Operation_State_Enum
    # Opt
    grant_renew: Optional[bool] = None
    # Conditional; see 8.6 for inclusion rules
    # TODO: Check if this is a List of Meas_Report objects
    meas_report: Optional[Meas_Report] = None


class Heartbeat_Response(BaseModel):
    """
    HeartbeatResponse object as defined in 10.8.1. of <1>
    """
    # Req
    response: Response
    # Req
    transmit_expire_time: str = Field(..., regex=r'\d{4}-[01]\d-[0123]\dT[012]\d:[012345]\d:[012345]\dZ')
    # Cond; This parameter is included if and only if  the cbsdId parameter in the HeartbeatRequest object contains a
    # valid CBSD identity. If included, the SAS shall set this parameter to the value of thein the corresponding
    # HeartbeatRequest object.
    cbsd_id: Optional[str] = None
    # Cond; included iff "the grantId parameter in the HeartbeatRequest object contains a valid Grant identity. If
    # included, the SAS shall set this parameter to the value of the grantId parameter in the corresponding
    # HeartbeatRequest object"
    grant_id: Optional[str] = None
    # Cond; "Required if the responseCode parameter indicates SUCCESS or SUSPENDED_GRANT and the grantRenew parameter
    # was included and set to True in the corresponding HeartbeatRequest object. This parameter may be included at
    # other times by SAS choice. When included, if the channelType of this Grant is “PAL”, this parameter shall be
    # set to the value that does not extend beyond the licenseExpiration of the corresponding PAL recorded in the PAL
    # Database [n.23]."
    grant_expire_time: Optional[str] = None
    # Optional
    heartbeat_interval: Optional[conint(gt=0)] = None
    # Optional
    operation_param: Optional[Operation_Param] = None
    # Optional
    meas_report_config: Optional[List[Meas_Report_Type]]


class Relinquishment_Request(BaseModel):
    """
    RelinquishmentRequest object as defined in 10.9.1 of <1>
    All fields are required.
    """
    cbsd_id: str
    grant_id: str


class Relinquishment_Response(BaseModel):
    """
    RelinquishmentResponse object as defined in 10.10.1 of <1>
    """
    response: Response
    # Conditional; "Included IFF the cbsdId parameter in the RelinquishmentRequest object
    # contains a valid CBSD identity. If included, the SAS shall set this parameter to the value of the cbsdId
    # parameter in the corresponding RelinquishmentRequest object"
    cbsd_id: str
    # Conditional; "Included IFF the grantId parameter in the RelinquishmentRequest object contains a valid Grant
    # identity. If included, the SAS shall set this parameter to the value of the grantId parameter in the
    # corresponding RelinquishmentRequest object"
    grant_id: str


class Deregistration_Request(BaseModel):
    """
    DeregistrationRequest object as defined in 10.11.1 of <1>
    All fields are required.
    """
    cbsd_id: str


class Deregistration_Response(BaseModel):
    """
    DeregistrationResponse object as defined in 10.12.1 of <1>
    """
    response: Response
    # Conditional; "Included IFF the cbsdId parameter in the DeregistrationRequest object
    # contains a valid CBSD identity. If included, the SAS shall set this parameter to the value of the cbsdId
    # parameter in the corresponding DeregistrationRequest object"
    cbsd_id: str
