"""
This module contains class definitions for objects used by SAS-CBSD interactions according to the following documents:
<1> WINNF-TS-0016-V1.2.7 SAS to CBSD Technical Specification

This module uses pydantic to validate objects, inputs, and outputs
"""
from dataclasses import dataclass, field
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
)

OptStr = Optional[str]
OptFloat = Optional[float]
OptInt = Optional[int]
OptDec = Optional[Decimal]

# @dataclass
class Cbsd_Info:
    """
    Optional argument for Registration_Request
    Defined in 10.1.5 of <1>

    Note: The maximum length of each parameter is 64 octets
    Note 2: The CbsdInfo object can be extended with other vendor information in additional key-value pairs.

    All fields are optional
    """
    # Name of CBSD Vendor
    vendor: OptStr = None
    # Name of the CBSD model
    model: OptStr = None
    # Software version of the CBSD
    software_version: OptStr = None
    # Hardware version of the CBSD
    hardware_version: OptStr = None
    # Firmware version of the CBSD
    firmware_version: OptStr = None
    # Optional additional vendor information
    extended_vendor_info: Dict = field(default_factory=dict)

# @dataclass
class Air_Interface:
    """
    A data object that includes information on the air interface technology of the CBSD.
    REG-Conditional for Registration_Request
    Defined in 10.1.2 of <1>
    """
    # REG-Conditional
    radio_technology: OptStr

class Height_Type_Enum(str, Enum):
    """
    Used to specify the possible choices for the 'height_type' parameter of an Installation_Param object
    """
    agl = "AGL" # measured relative to ground level
    amsl = "AMSL" # measured relative to mean sea level

# @dataclass
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

# @dataclass
class Group_Param:
    """
    Object that includes information on CBSD grouping.
    A list of these objects are included as the optional group_param parameter in Registration_Request
    Defined in 10.1.4 of <1>

    All fields are required.
    """
    group_type: str
    group_id: str

# @dataclass
class Professional_Installer_Data:
    """
    "The value of this parameter is the data identifying the CPI vouching for the installation parameters included in
    the installationParam value contained in this object"
    A required parameter of the Cpi_Signed_Data constructor, which is itself, the unencoded parameter of a
    Cpi_Signature_Data object, which finally, is an optional parameter for Registration_Request.
    Defined in 10.1.8 of <1>

    All fields are required.
    The maximum length of cpi_id and cpi_name is 256 octets.
    installation_certification_time is the UTC datetime at which the CPI identified in this object cerified the CBSD's
    installed parameters. It is expressed using the format, YYYY-MM-DDThh:mm:ssZ, as defined by [n.7]/
    """
    cpi_id: str
    cpi_name: str
    # (See documentation)
    install_certification_time: str

# @dataclass
class Cpi_Signed_Data:
    """
    The un-encoded "encoded_cpi_signed_data" parameter of a Cpi_Signature Data object
    Defined in 10.1.7 in <1>
    All fields are required.
    """
    fcc_id: str
    cbsd_serial_number: str
    installation_param: Installation_Param
    professional_installer_data: Professional_Installer_Data


# @dataclass
class Cpi_Signature_Data:
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

# @dataclass
class Registration_Request:
    """
    RegistrationRequest object per section 10.1.1 of <1>
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
    cbsd_category: Optional[str] = None
    # Optional
    cbsd_info: Optional[Cbsd_Info] = field(default_factory=Cbsd_Info)
    # REG-Conditional
    air_interface: Optional[Air_Interface] = field(default_factory=Air_Interface)
    # REG-Conditional
    installation_param: Optional[Installation_Param] = field(default_factory=Installation_Param)
    # REG-Conditional
    meas_capability: Optional[List[str]] = field(default_factory=list)
    # Optional
    grouping_param: Optional[List[Group_Param]] = field(default_factory=Group_Param)
    # Optional
    cpi_signature_data: Optional[Cpi_Signature_Data] = field(default_factory=Cpi_Signature_Data)
