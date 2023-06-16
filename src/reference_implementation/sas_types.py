"""
This module contains class definitions for objects used by SAS-CBSD interactions according to the following documents:
<1> WINNF-TS-0016-V1.2.7 SAS to CBSD Technical Specification

"""
from dataclasses import dataclass, field
from typing import Optional, Any, Union, List, Dict, Tuple

OptStr = Optional[str]

@dataclass
class Cbsd_Info:
    """
    Optional argument for Registration_Request
    Defined in 10.1.5 of <1>

    Note: The maximum length of each parameter is 64 octets
    Note 2: The CbsdInfo object can be extended with other vendor information in additional key-value pairs.
    """
    # Name of CBSD Vendor
    vendor: str = field(default_factory=str)
    # Name of the CBSD model
    model: str = field(default_factory=str)
    # Software version of the CBSD
    software_version: str = field(default_factory=str)
    # Hardware version of the CBSD
    hardware_version: str = field(default_factory=str)
    # Firmware version of the CBSD
    firmware_version: str = field(default_factory=str)
    # Optional additional vendor information
    extended_vendor_info: Dict = field(default_factory=dict)

@dataclass
class Air_Interface:
    """
    A data object that includes information on the air interface technology of the CBSD.
    REG-Conditional for Registration_Request
    Defined in 10.1.2 of <1>
    """
    # REG-Conditional
    radio_technology: str

@dataclass
class Installation_Param:
    """
    A data object that includes information on CBSD installation.
    REG-Conditional for Registration_Request
    Defined in 10.1.3 of <1>
    """
    # REG-Conditional
    latitude: float
    # REG-Conditional
    longitude: float
    # REG-Conditional
    height: float
    # REG-Conditional
    height_type: str
    # Optional
    horizontal_accuracy: float
    # Optional
    vertical_accuracy: float
    # REG-Conditional
    indoor_deployment: bool
    # REG-Conditional
    antenna_azimuth: int
    # REG-Conditional
    antenna_downtilt: int
    # REG-Conditional
    antenna_gain: int
    # Optional
    eirp_capability: int
    # REG-Conditional
    antenna_beamwitdth: int
    # Optional
    antenna_model: str

@dataclass
class Group_Param:
    """
    Object that includes information on CBSD grouping.
    A list of these objects are included as the optional group_param parameter in Registration_Request
    Defined in 10.1.4 of <1>
    """
    # Required
    group_type: str
    # Required
    group_id: str

@dataclass
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

@dataclass
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


@dataclass
class Cpi_Signature_Data:
    """
    The CPI is vouching for the parameters in this object. In addition, the digital signature for these parameters is included.
    Optional parameter for Registration_Request.
    Defined in 10.1.6 of <1>

    protected_header: "The value of this parameter is the BASE64-encoded JOSE [(Javascript Object Signing and
        Encryption)] protected header. This is a JSON object equivalent to the JWT RS256 method or the ES256 method
        described in RFC 7515 [n.19] Section 3. BASE64 encoding is per RFC 4648 (see [n.20]). Valid values are
        equivalent to the JSON: { “typ”: “JWT”, “alg”: “RS256” } or { “typ”: “JWT”, “alg”: “ES256” }"
    encoded_cpi_signed_Data: "The value of this parameter is the encoded JOSE payload data
        to be signed by the CPI’s private key.This parameter is calculated by taking the BASE64 encoding of a
        CpiSignedDataobject (see Table 10) according to the procedures in RFC 7515 [n.19], Section 3."
    digital_signature: "The value of this parameter is the CPI digital signature applied to the encodedCpiSignedData field.This
        signature is the BASE64URLencoding of the digital signature, prepared according to the procedures in RFC 7515 [
        n.19] Section 3, using the algorithm as declared in the protectedHeader field."

    "Note: The JOSE JSON Web Signature per RFC-7515 (see [n.19]) is used to ensure data integrity and CPI
    non-repudiation of the signed parameters. The JOSE compact serialization is formed by concatenating the
    protectedHeader, encodedCpiSignedData, and digitalSignature fields with “.” Characters, as described in section 3
    of RFC 7515 [n.19]."

    All fields are required.
    """
    protected_header: str
    encoded_cpi_signed_data: str
    digital_signature: str

@dataclass
class Registration_Request:
    """
    RegistrationRequest object per section 10.1.1 of <1>
    """
    #
    user_id: str
    #
    fcc_id: str
    #
    cbsd_serial_number: str
    # Optional
    call_sign: str
    # REG-Conditional
    cbsd_category: str
    # Optional
    cbsd_info: Cbsd_Info
    # REG-Conditional
    air_interface: Air_Interface
    # REG-Conditional
    installation_param: Installation_Param
    # REG-Conditional
    meas_capability: List[str]
    # Optional
    grouping_param: List[Group_Param]
    cpi_signature_data: Cpi_Signature_Data
