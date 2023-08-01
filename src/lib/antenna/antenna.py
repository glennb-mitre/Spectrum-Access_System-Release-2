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

"""Antenna gain routines for SAS.

Typical usage:
  # Get the gains for a given antenna horizontal and/or vertical pattern.
  # To be used for ESC and CBSD with actual antenna patterns.
  gains = GetAntennaPatternGains(hor_dirs, ant_azimuth, pattern)

  # Get CBSD antenna gain (from antenna defined by beamwidth and gain only).
  gains = GetStandardAntennaGains(hor_dirs, ant_azimuth, beamwidth, ant_gain)

  # Get Radar normalized antenna gain for DPA protection.
  gains = GetRadarNormalizedAntennaGains(hor_dirs, radar_azimuth)

  # Get FSS earth station antenna gains
  gains = GetFssAntennaGains(hor_dirs, ver_dirs,
                             fss_azimuth, fss_elevation, fss_ant_gain)
"""
from typing import List, Dict, Tuple, Optional, Union, Iterable, Mapping, TypeVar
import numpy as np
from numpy.typing import NDArray

T = TypeVar("T")

def get_dirs_relative_boresight(
    dirs: Dict[str, Union[int, float]],
    ant_az: int,
    downtilt: Optional[int] = None
) -> Dict[str, int]:
    """
    Helper function to calculate the relative_boresight (see Returns).

    Args:
        dirs: Horizontal and vertical directions (degrees) at which the gain needs to be calculated. Either a scalar or
            an iterable.
        ant_az: Antenna azimuth (degrees).
        downtilt: Antenna mechanical downtilt(degrees), limited to +-15 degrees. If not used, then the value of the
            "ver" key in the returned dictionary is 0.

    Returns: A mapping with the keys "hor" and "ver" with the following respective valuse: azimuth angle of the line
        between the CBSD main beam and the receiver location relative to the CBSD antenna boresight, and the vertical
        angle of the line between the CBSD main beam and the receiver location relative to the CBSD antenna boresight
    """
    # azimuth angle of the line between the CBSD main beam and the receiver location relative to the CBSD antenna
    # boresight
    theta_r = dirs['hor'] - ant_az
    theta_r = np.atleast_1d(theta_r)
    theta_r[theta_r > 180] -= 360
    theta_r[theta_r < -180] += 360

    # if downtilt is not provided, phi_r remains 0
    phi_r = 0

    if downtilt is not None:
        # vertical angle of the line between the CBSD main beam and the receiver location relative to the CBSD antenna
        # boresight
        phi_r = dirs['ver'] + downtilt * np.cos(theta_r * 180 / np.pi)

    return {'hor': theta_r, 'ver': phi_r}


def limit_downtilt_value(downtilt: int) -> int:
    """
    Restrict the value of downtilt to within +- 15 (degrees)
    Args:
        downtilt: An integer

    Returns: downtilt but restricted to the above range.
    """
    if downtilt < -15:
        downtilt = -15
    # Use saturating counter behavior
    downtilt = min(downtilt, 15)
    return downtilt


def get_multiple_indices(lst: Union[Iterable[T], np.ndarray], key: T) -> List[int]:
    """
    Find multiple list indices at which a certain value is found.

    Returns: A list of integer indices at which the key value is found within lst.

    Args:
        lst (List of elements of type T): the List on which to search for the given key.
        key (a value of type T): the element for which to obtain the indices in
            the lst at which the value appears.
    """
    if isinstance(lst, np.ndarray):
        # np.where returns a Tuple of np.ndarray objects
        return list(np.where(lst == key)[0])
    if isinstance(lst, Iterable):
        return [idx for idx, value in enumerate(lst) if value == key]
    raise TypeError("lst must be of an Iterable type or Numpy NDArray.")


def b1_antenna_gain(
    dirs: Dict[str, Union[int, float]],
    ant_az: int,
    peak_ant_gain: Union[float, int],
    hor_pattern: Dict[str, List[float]],
    ver_pattern: Dict[str, List[float]],
    downtilt: int
):
    """
    REL2-R3-SGN-52105: Method B1 based antenna gain calculation.
    Use of two one-dimensional antenna patterns (denoted as GH(theta) and GV(phi), respectively)
    derived from the CBSD Registration parameters.

    Directions and azimuth are defined compared to the north in clockwise
    direction and shall be within [0..360] degrees.

    Args:
        dirs:           Horizontal and vertical directions (degrees) at which the gain needs to be
                        calculated Either a scalar or an iterable.
        ant_az:         Antenna azimuth (degrees).
        peak_ant_gain:  cbsd antenna gain(dBi) at boresight
        hor_pattern:    antenna gain pattern in horizontal plane
        ver_pattern:    antenna gain pattern in vertical plane
        downtilt:       Antenna mechanical downtilt(degrees), limited to +-15 degrees

    Returns:
        The CBSD two-dimensional antenna gains (in dB) relative to peak antenna gain
        Either a scalar if dirs is scalar or an ndarray otherwise.
    """
    dirs_relative_boresight = get_dirs_relative_boresight(dirs, ant_az, downtilt)

    downtilt = limit_downtilt_value(downtilt)

    # REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step a

    # horizontal gain at thetaR, G_H (thetaR), vertical gains at phiR and at 180-phiR angle,
    # G_V (phiR) and G_V (180-phiR)
    g_h_theta_r, g_v_phi_r, g_v_phi_rsup = get_given_2d_pattern_gains(
        dirs_relative_boresight, hor_pattern, ver_pattern, ant_az, downtilt
    )
    # REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step b
    # gain_two_dimensional AKA g_cbsd
    gain_two_dimensional = get_2d_antenna_gain(
        dirs, g_h_theta_r, g_v_phi_r, g_v_phi_rsup, hor_pattern['gain'][180],
        hor_pattern['gain'][0], peak_ant_gain
    )

    return gain_two_dimensional


def c_antenna_gain(
    dirs: Union[Mapping, Iterable],
    ant_az: int,
    peak_ant_gain: int,
    downtilt: int,
    hor_beamwidth: int,
    ver_beamwidth: int,
    fbr: int
) -> Union[Mapping, np.ndarray]:
    """REL2-R3-SGN-52106: Method C based Antenna Gain Calculation
    Use of two one-dimensional antenna patterns (denoted as GH(theta) and GV(phi), respectively)
    derived from the CBSD Registration parameters.

    Directions and azimuth are defined compared to the north in clockwise
    direction and shall be within [0..360] degrees.

    Inputs:

    dirs:           Horizontal and vertical directions (degrees) at which the gain needs to be
                    calculated. Either a scalar or an iterable.
    ant_az:         antenna azimuth (degrees).
    peak_ant_gain:  cbsd antenna gain(dBi) at boresight
    donwtilt:       antenna mechanical downtilt(degrees), positive below horizon.
    hor_beamwidth:  antenna 3dB beamwidth in horizontal plane
    ver_beamwidth:  antenna 3dB beamwidth in vertical plane
    fbr:            antenna front-to-back-ratio(dB)

    Returns:
    The CBSD two-dimensional antenna gains (in dB) relative to peak antenna gain
    Either a scalar if dirs is scalar or an ndarray otherwise.
    """
    # azimuth angle of the line between the CBSD main beam and the receiver location relative to
    # the CBSD antenna boresight
    dirs_relative_boresight = get_dirs_relative_boresight(dirs, ant_az, downtilt)

    downtilt = limit_downtilt_value(downtilt)

    # horizontal gain at thetaR, vertical gains at phiR
    g_h_theta_r, g_v_phi_r = get_standard_2d_gains(
        dirs_relative_boresight, ant_az, peak_ant_gain, downtilt,
        hor_beamwidth, ver_beamwidth, ant_fbr=fbr
    )

    # in degrees
    dirs_0 = {'hor': 0}
    dirs_180 = {'hor': 180}

    phi_r = dirs_relative_boresight['ver']
    # supplementary angle of phi
    dirs_phi_r_sup = {'ver': 180 - phi_r}

    # horizontal gain at 0 degrees, G_H (0)
    g_h_theta_0, _ = get_standard_2d_gains(
        dirs_0, ant_az, peak_ant_gain, ant_hor_beamwidth=hor_beamwidth,
        ant_fbr=fbr
    )

    # horizontal gain at 180 degrees, G_H (180)
    g_h_theta_180, _ = get_standard_2d_gains(
        dirs_180, ant_az, peak_ant_gain, ant_hor_beamwidth=hor_beamwidth,
        ant_fbr=fbr
    )

    # vertical gain at 180-phiR vertical angle, G_V (180-phiR)
    _, g_v_phi_r_sup = get_standard_2d_gains(
        dirs_phi_r_sup, ant_az, peak_ant_gain, ant_mech_downtilt=downtilt,
        ant_ver_beamwidth=ver_beamwidth, ant_fbr=fbr
    )

    # REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step b
    # gain_two_dimensional AKA g_cbsd
    gain_two_dimensional = get_2d_antenna_gain(
        dirs, g_h_theta_r, g_v_phi_r, g_v_phi_r_sup, g_h_theta_0,
        g_h_theta_180, peak_ant_gain
    )

    return gain_two_dimensional


def d_antenna_gain(
    dirs: Dict[str, Union[int, float]],
    ant_az: Union[int, float],
    peak_ant_gain: Union[int, float],
    hor_patt: Dict[str, List[Union[int, float]]],
    downtilt: Union[int, float],
    ver_beamwidth: Union[int, float],
    fbr: Union[int, float],
) -> Union[Mapping, np.ndarray]:
    """REL2-R3-SGN-52107: Method D based Antenna Gain Calculation:
    Use of two one-dimensional antenna patterns (denoted as GH(theta) and GV(phi), respectively),
    where the horizontal antenna pattern (denoted as GH(theta)) is recorded in the CBSD Antenna
    Pattern Database, and the vertical antenna pattern is derived from the CBSD Registration
    parameters.

    Directions and azimuth are defined compared to the north in clockwise
    direction and shall be within [0..360] degrees.

    Inputs:

    dirs:           Horizontal and vertical directions (degrees) at which the gain needs to
                    be calculated. Either a scalar or an iterable.
    ant_az:         antenna azimuth (degrees).
    peak_ant_gain:  cbsd antenna gain(dBi) at boresight
    hor_patt:       antenna gain pattern in horizontal database
    ver_beamwidth:  antenna 3dB beamwidth in vertical plane
    donwtilt:       antenna mechanical downtilt(degrees)
    fbr:            antenna front-to-back-ratio(dB)

    Returns:
    The CBSD two-dimensional antenna gains (in dB) relative to peak antenna gain.
    Either a scalar if dirs is scalar or an ndarray otherwise.
    """
    dirs_relative_boresight = get_dirs_relative_boresight(dirs, ant_az, downtilt)

    downtilt = limit_downtilt_value(downtilt)

    phi_r = dirs_relative_boresight['ver']
    # supplementary angle of phi (in degrees)
    dirs_phi_r_sup = {'ver': 180 - phi_r}

    # horizontal gain at thetaR angle, G_H (thetaR)
    g_h_theta_r, *_ = get_given_2d_pattern_gains(
        dirs_relative_boresight, hor_pattern=hor_patt, ant_azimuth=ant_az
    )
    # G_H(0)
    g_h_theta_0 = hor_patt['gain'][180]
    # G_H(180)
    g_h_theta_180 = hor_patt['gain'][0]

    # G_V(phiR)
    _, g_v_phi_r = get_standard_2d_gains(
        dirs_relative_boresight, ant_az, peak_ant_gain,
        ant_mech_downtilt=downtilt, ant_ver_beamwidth=ver_beamwidth,
        ant_fbr=fbr
    )

    # G_V(180-phiR)
    _, g_v_phi_r_sup = get_standard_2d_gains(
        dirs_phi_r_sup, ant_az, peak_ant_gain, ant_mech_downtilt=downtilt,
        ant_ver_beamwidth=ver_beamwidth, ant_fbr=fbr
    )

    # REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step b
    # gain_two_dimensional AKA g_cbsd
    gain_two_dimensional = get_2d_antenna_gain(
        dirs_relative_boresight, g_h_theta_r, g_v_phi_r, g_v_phi_r_sup,
        g_h_theta_0, g_h_theta_180, peak_ant_gain
    )

    return gain_two_dimensional


def e_antenna_gain(dirs, ant_az, peak_ant_gain, hor_patt):
    """REL2-R3-SGN-52108: Method E based Antenna Gain Calculation:
    Use of the horizontal antenna pattern (denoted as GH(theta)) recorded in the CBSD 
    Antenna Pattern Database. No vertical antenna pattern information is used.

    Directions and azimuth are defined compared to the north in clockwise
    direction and shall be within [0..360] degrees.    
    
    Inputs:

    dirs:           Horizontal and vertical directions (degrees) at which the gain needs to
                    be calculated. Either a scalar or an iterable.
    ant_az:         antenna azimuth (degrees).
    peak_ant_gain:  peak antenna gain(dBi)
    hor_patt:       antenna gain pattern in horizontal database
    
    Returns:
    The CBSD  antenna gains (in dB) in vertical plane relative to peak antenna gain, 
    Either a scalar if dirs is scalar or an ndarray otherwise.
    """
    dirs_relative_boresight = get_dirs_relative_boresight(dirs, ant_az)

    # horizontal gain at thetaR angle, G_H (thetaR)
    g_h_theta_r, *_ = get_given_2d_pattern_gains(
        dirs_relative_boresight, hor_pattern=hor_patt, ant_azimuth=ant_az
    )
    # G_H(0)
    g_h_theta_0 = hor_patt['gain'][180]
    # G_H(180)
    g_h_theta_180 = hor_patt['gain'][0]

    g_v_phi_r = 0
    g_v_phi_r_sup = 0

    # REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step b
    # gain_two_dimensional AKA g_cbsd
    gain_two_dimensional = get_2d_antenna_gain(
        dirs_relative_boresight, g_h_theta_r, g_v_phi_r, g_v_phi_r_sup,
        g_h_theta_0, g_h_theta_180, peak_ant_gain
    )

    return gain_two_dimensional


def get_standard_2d_gains(
    dirs, ant_azimuth=None, peak_ant_gain=0,
    ant_mech_downtilt=None, ant_hor_beamwidth=None,
    ant_ver_beamwidth=None, ant_fbr=None
):
    """REL2-R3-SGN-52106: Method C based Antenna Gain Calculation, step a
    Computes the antenna gain pattern using both horizontal and vertical properties.


    Directions and azimuth are defined compared to the north in clockwise
    direction and shall be within [0..360] degrees.

    Inputs:

    dirs:               Horizontal and vertical directions (degrees) at which the gain needs to
                        be calculated. Either a scalar or an iterable.
    ant_az:             antenna azimuth (degrees).
    peak_ant_gain:      peak antenna gain(dBi)
    ant_hor_beamwidth:  antenna 3dB beamwidth in horizontal plane
    ant_ver_beamwidth:  antenna 3dB beamwidth in vertical plane
    ant_mech_donwtilt:  antenna mechanical downtilt(degrees), limited to +-15 degrees
    ant_fbr:            antenna front-to-back-ratio(dB)

    Returns:
    g_h_theta_r:  cbsd horizontal antenna gain(dB) at theta_r angle relative to peak antenna gain
    g_v_phi_r:    cbsd vertical antenna gain(dB) at phi_r angle, relative to peak antenna gain

    Either a scalar if dirs is scalar or an ndarray otherwise.
    """
    g_h_theta_r = []
    g_v_phi_r = []

    if ant_fbr is None:
        ant_fbr = 20

    if 'hor' in dirs:
        theta_r = dirs['hor']
        theta_r = np.atleast_1d(theta_r)
        if (ant_hor_beamwidth is None or ant_azimuth is None or
                ant_hor_beamwidth == 0 or ant_hor_beamwidth == 360):
            g_h_theta_r = peak_ant_gain * np.ones(theta_r.shape)
        else:
            g_h_theta_r = -min([12 * (theta_r / float(ant_hor_beamwidth)) ** 2, ant_fbr])
            g_h_theta_r += peak_ant_gain

    if 'ver' in dirs:
        phi_r = dirs['ver']
        phi_r = np.atleast_1d(phi_r)
        if (ant_ver_beamwidth is None or ant_mech_downtilt is None or
                ant_ver_beamwidth == 0 or ant_ver_beamwidth == 360):
            g_v_phi_r = peak_ant_gain * np.ones(phi_r.shape)
        else:
            g_v_phi_r = -min([12 * (phi_r / float(ant_ver_beamwidth)) ** 2, ant_fbr])
            g_v_phi_r += peak_ant_gain

    return g_h_theta_r, g_v_phi_r


def _get_gain_at_angle(
    angle: Union[float, int, NDArray],
    pattern: Dict[str, List[int]]
) -> Union[NDArray, float, int]:
    """
    Calculates the gain at a given direction with a given antenna pattern.

    Subfunction of get_given_2d_pattern_gains, which is specified in
        REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step a

    Depending on the inputs, this function computes one of the following:
        g_h_theta_r: cbsd horizontal antenna gain(dB) at theta_r angle relative
            to peak antenna gain
        g_v_phi_r: cbsd vertical antenna gain(dB) at phi_r angle, relative to
            peak antenna gain
        g_v_phi_rsup: cbsd vertical antenna gain(dB) at supplementary angle of
            phi_r(180-phi_r), relative to peak antenna gain

    Args:
        angle: the angle at which to compute the vertical gain OR horizontal
            gain (depending on the pattern given)
        pattern: contains either vertical plane angles and associated gains OR
            horizontal plane angles and associated gains

    Returns:
        gain_at_given_direction_from_pattern: the CBSD horizontal OR vertical
            gain at the given angle relative to the peak antenna gain
    """
    # this is either the list of angles from the horizontal pattern OR the list
    # of angles from the vertical pattern
    angle_list = pattern['angle']
    # this is either the list of gains from the horizontal pattern OR the list
    # of gains from the vertical pattern
    gain_list = pattern['gain']

    angle_idx_list = get_multiple_indices(angle_list, angle)
    if angle_idx_list:
        gain_at_given_direction_from_pattern = gain_list[angle_idx_list[0]]
    else:
        # Find the two values that are closest to angle, one being positive, the other being negative
        angle_diff = [angle - i for i in angle_list]
        positive_angle_diff = [i for i in angle_diff if i > 0]
        # either theta_m, phi_n, or phi_k in the specification
        angle_a_pos = angle_list[angle_diff.index(min(positive_angle_diff))]

        negative_angle_diff = [i for i in angle_diff if i < 0]
        # either theta_m_1, phi_n_1, or angle_a_neg in the spec
        angle_a_neg = angle_list[angle_diff.index(max(negative_angle_diff))]

        # the index at which angle_a_pos appears in angle_list
        angle_a_pos_idx = get_multiple_indices(angle_list, angle_a_pos)
        # the gain at the above index
        gain_at_pos_angle_idx = gain_list[angle_a_pos_idx[0]]

        # the index at which angle_a_neg appears in angle_list
        angle_a_neg_idx = get_multiple_indices(angle_list, angle_a_neg)
        # the gain at the above index
        gain_at_neg_angle_idx = gain_list[angle_a_neg_idx[0]]

        # either g_h_theta_r, g_v_phi_r, or g_v_phi_rsup in the Spec
        gain_at_given_direction_from_pattern = ((angle_a_neg - angle) * gain_at_pos_angle_idx + (
                    angle - angle_a_pos) * gain_at_neg_angle_idx) / (angle_a_neg - angle_a_pos)
    return gain_at_given_direction_from_pattern


def get_given_2d_pattern_gains(
    dirs: Dict[str, Union[Union[int, float], Iterable]],
    hor_pattern: Optional[Dict[str, List[Union[int, float]]]] = None,
    ver_pattern: Optional[Dict[str, List[Union[int, float]]]] = None,
    ant_azimuth: Optional[float] = None,
    ant_mech_downtilt: Optional[float] = None
) -> Tuple[Union[List, float, NDArray], ...]:
    """ REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step a

    Computes the gain at a given direction from a given antenna pattern (horizontal and vertical).

    Directions and azimuth are defined compared to the north in clockwise
    direction and shall be within [0..360] degrees.

    Inputs:
        hor_pattern: contains horizontal plane angles and associated gains
        ver_pattern: contains vertical plane angles and associated gains
        ant_azimuth: Antenna azimuth (degrees).
        ant_mechanical_downtilt: antenna mechanical downtilt(degrees), limited
            to +-15 degrees

    Outputs:
        g_h_theta_r: cbsd horizontal antenna gain(dB) at theta_r angle relative
            to peak antenna gain
        g_v_phi_r: cbsd vertical antenna gain(dB) at phi_r angle, relative to
            peak antenna gain
        g_v_phi_rsup: cbsd vertical antenna gain(dB) at supplementary angle of
            phi_r(180-phi_r), relative to peak antenna gain
    """
    # horizontal direction
    theta_r = dirs['hor']

    # vertical direction
    phi_r = dirs['ver']

    g_h_theta_r = []
    g_v_phi_r = []
    g_v_phi_rsup = []

    if hor_pattern is not None:
        g_h_theta_r = _get_gain_at_angle(theta_r, hor_pattern)

    if ver_pattern is not None:
        g_v_phi_r = _get_gain_at_angle(phi_r, ver_pattern)

        phi_r_supplementary_angle = 180 - phi_r
        phi_r_supplementary_angle = np.atleast_1d(phi_r_supplementary_angle)
        phi_r_supplementary_angle[phi_r_supplementary_angle >= 180] -= 360

        g_v_phi_rsup = _get_gain_at_angle(phi_r_supplementary_angle, ver_pattern)

    return g_h_theta_r, g_v_phi_r, g_v_phi_rsup


def get_2d_antenna_gain(
    dirs,
    hor_gain,
    ver_gain,
    ver_gain_sup_angle,
    hor_gain_0,
    hor_gain_180,
    peak_ant_gain=0
):
    """REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step b

    Computes the two-dimensional antenna gain at a given direction, from horizontal and
    vertical gain.

    Directions and azimuth are defined compared to the north in clockwise
    direction and shall be within [0..360] degrees.

    Inputs:
      dirs:                Horizontal and vertical directions at which antenna gain is to be
                           calculated (degrees). Either a scalar or an iterable.
      hor_gain:            (AKA g_h_theta_r) antenna relative gain(w.r.t peak antenna gain) at the given
                           direction(theta_R) in horizontal plane(dB)
      ver_gain:            antenna relative gain(w.r.t peak antenna gain) at the given
                           direction(phi_R) in vertical plane(dB)
      ver_gain_sup_angle:  antenna relative gain(w.r.t peak antenna gain) at the supplementary
                           angle of given direction(180-phi_R) in vertical plane(dB)
      ant_hor_beamwidth:   Antenna 3dB cutoff beamwidth (degrees) in horizontal plane
                           If None, then antenna is isotropic (default).
      ant_ver_beamwidth:   Antenna 3dB cutoff beamwidth (degrees) in vertical plane
                           If None, then antenna is isotropic (default).
      hor_gain_0:          antenna gain at 0 degree (G(0))
      hor_gain_180:        antenna gain at 180 degrees(G(180))

      peak_ant_gain:       Antenna gain (dBi)at boresight

    Outputs:
      gain_two_dimensional: cbsd two-dimensional antenna gain(dB) relative to peak antenna gain

    """
    hor_dir = dirs['hor']
    g_cbsd_relative = hor_gain + ((1 - abs(hor_dir) / 180) * (ver_gain - hor_gain_0) +
                                  (abs(hor_dir) / 180) * (ver_gain_sup_angle - hor_gain_180))
    g_cbsd = g_cbsd_relative + peak_ant_gain

    return g_cbsd


def get_given_1d_pattern_gains(
    hor_dirs,
    ant_azimuth,
    hor_pattern,
    ant_gain=0
):
    """Computes the gain for a given antenna pattern.

    Directions and azimuth are defined compared to the north in clockwise
    direction and shall be within [0..360] degrees.

    Inputs:
      hor_dirs:       Ray directions in horizontal plane (degrees).
                      Either a scalar or an iterable.
      ant_azimuth:    Antenna azimuth (degrees).
      hor_pattern:    The antenna horizontal pattern defined as a ndarray of
                      360 values with the following conventions:
                       - clockwise increments of 1 degree.
                       - 0 degree corresponds to the antenna boresight.
                       - values are 'gain' (and not attenuation)
      ant_gain:       Optional additional antenna gain (dBi).
                      To be used if not included in the pattern (ie when using
                      a normalized pattern).

    Returns:
      The antenna gains (in dB): either a scalar if hor_dirs is scalar,
      or an ndarray otherwise.
    """
    is_scalar = np.isscalar(hor_dirs)
    hor_dirs = np.atleast_1d(hor_dirs)

    bore_angle = hor_dirs - ant_azimuth
    bore_angle[bore_angle >= 360] -= 360
    bore_angle[bore_angle < 0] += 360
    idx0 = bore_angle.astype(np.int)
    alpha = bore_angle - idx0
    idx1 = idx0 + 1
    idx1[idx1 >= 360] -= 360
    gains = (1 - alpha) * hor_pattern[idx0] + alpha * hor_pattern[idx1]
    gains += ant_gain

    if is_scalar:
        return gains[0]
    return gains


def get_standard_gains(
    hor_dirs,
    ant_azimuth=None,
    ant_beamwidth=None,
    ant_gain=0
):
    """Computes the antenna gains from a standard antenna defined by beamwidth.

    See R2-SGN-20.
    This uses the standard 3GPP formula for pattern derivation from a given
    antenna 3dB cutoff beamwidth.
    Directions and azimuth are defined compared to the north in clockwise
    direction and shall be within [0..360] degrees.

    Inputs:
      hor_dirs:       Ray directions in horizontal plane (degrees).
                      Either a scalar or an iterable.
      ant_azimut:     Antenna azimuth (degrees).
      ant_beamwidth:  Antenna 3dB cutoff beamwidth (degrees).
                      If None, then antenna is isotropic (default).
      ant_gain:       Antenna gain (dBi).

    Returns:
      The CBSD antenna gains (in dB).
      Either a scalar if hor_dirs is scalar or an ndarray otherwise.
    """
    is_scalar = np.isscalar(hor_dirs)
    hor_dirs = np.atleast_1d(hor_dirs)

    if (ant_beamwidth is None or ant_azimuth is None or
            ant_beamwidth == 0 or ant_beamwidth == 360):
        gains = ant_gain * np.ones(hor_dirs.shape)
    else:
        bore_angle = hor_dirs - ant_azimuth
        bore_angle[bore_angle > 180] -= 360
        bore_angle[bore_angle < -180] += 360
        gains = -12 * (bore_angle / float(ant_beamwidth)) ** 2
        gains[gains < -20] = -20.
        gains += ant_gain

    if is_scalar:
        return gains[0]
    return gains


def get_radar_normalized_gains(hor_dirs,
                               radar_azimuth,
                               radar_beamwidth=3):
    """Computes the DPA radar normalized antenna gain.

    See R2-SGN-24.
    Directions and azimuth are defined compared to the north in clockwise
    direction and shall be within [0..360] degrees.
    Note that the DPA antenna gain is normalized to 0dBi at boresight:
    actual radar antenna gain is implicitely included in the target interference
    thresholds.

    Inputs:
      hor_dirs:       Ray directions in horizontal plane (degrees).
                      Either a scalar or an iterable.
      radar_azimuth:  The radar antenna azimuth (degrees).
      radar_beamwidth: The radar antenna beamwidth (degrees).

    Returns:
      The normalized antenna gains (in dB).
      Either a scalar if hor_dirs is scalar or an ndarray otherwise.

    """
    if radar_beamwidth == 360:
        return 0.
    is_scalar = np.isscalar(hor_dirs)
    hor_dirs = np.atleast_1d(hor_dirs)

    bore_angle = hor_dirs - radar_azimuth
    bore_angle[bore_angle > 180] -= 360
    bore_angle[bore_angle < -180] += 360
    bore_angle = np.abs(bore_angle)
    gains = -25 * np.ones(len(bore_angle))
    gains[bore_angle < radar_beamwidth / 2.] = 0

    if is_scalar:
        return gains[0]
    return gains


def get_fss_gains(
    hor_dirs,
    ver_dirs,
    fss_pointing_azimuth,
    fss_pointing_elevation,
    fss_antenna_gain,
    w_1=0,
    w_2=1.0
) -> Union[float, np.ndarray]:
    """Computes the FSS earth station antenna gain.

    See R2-SGN-21.
    Horizontal directions and azimuth are defined compared to the north in
    clockwise fashion and shall be within [0..360] degrees.
    Vertical directions are positive for above horizon, and negative below.

    Inputs:
      hor_dirs:               Ray directions in horizontal plane (degrees).
                              Either a scalar or an iterable.
      ver_dirs:               Ray directions in vertical plane (degrees).
                              Either a scalar or an iterable (same dimension
                              as hor_dirs)
      fss_pointing_azimuth:   FSS earth station azimuth angle (degrees).
      fss_pointing_elevation: FSS earth station vertical angle (degrees).
      fss_antenna_gain:       FSS earth station nominal antenna gain (dBi).
      w_1, w_2:               Weights on the tangent and perpendicular
                              components. Optional: by default only use the
                              perpendicular component.
    Returns:
      The FSS gains on the incoming ray (in dB).
      Either a scalar if hor_dirs is scalar, or an ndarray otherwise.
    """
    is_scalar = np.isscalar(hor_dirs)
    hor_dirs = np.atleast_1d(np.radians(hor_dirs))
    ver_dirs = np.atleast_1d(np.radians(ver_dirs))
    fss_pointing_elevation = np.radians(fss_pointing_elevation)
    fss_pointing_azimuth = np.radians(fss_pointing_azimuth)

    # Compute the satellite antenna off-axis angle - see formula in R2-SGN-21, iii
    theta = 180 / np.pi * np.arccos(
        np.cos(ver_dirs) * np.cos(fss_pointing_elevation)
        * np.cos(fss_pointing_azimuth - hor_dirs) +
        np.sin(ver_dirs) * np.sin(fss_pointing_elevation))

    gain_gso_t, gain_gso_p = get_gso_gains(theta, fss_antenna_gain)
    gains = w_1 * gain_gso_t + w_2 * gain_gso_p

    if is_scalar:
        return gains[0]
    return gains


def get_gso_gains(theta, nominal_gain) -> Tuple[np.ndarray, ...]:
    """Returns FSS earth station gains from the off-axis angle.

    GSO means the 'Geostationary Satellite Orbit'.

    Inputs:
      theta:        Off-axis angles (degrees), as a ndarray
      nominal_gain: Nominal antenna gain (dBi)
    Returns:
      a tuple of ndarray:
        gain_gso_t: Gains in the tangent plane of the GSO (dB).
        gain_gso_p: Gains in the perpendicular plane of the GSO (dB).
    """
    theta = np.abs(theta)
    gain_gso_t = -10 * np.ones(len(theta))
    gain_gso_p = gain_gso_t.copy()

    gain_gso_p[theta <= 3] = nominal_gain
    idx_3_to_48 = np.where((theta > 3) & (theta <= 48))[0]
    gain_gso_p[idx_3_to_48] = 32 - 25 * np.log10(theta[idx_3_to_48])

    gain_gso_t[theta <= 1.5] = nominal_gain
    idx_1_5_to_7 = np.where((theta > 1.5) & (theta <= 7))[0]
    gain_gso_t[idx_1_5_to_7] = 29 - 25 * np.log10(theta[idx_1_5_to_7])
    gain_gso_t[(theta > 7) & (theta <= 9.2)] = 8
    idx_9_2_to_48 = np.where((theta > 9.2) & (theta <= 48))[0]
    gain_gso_t[idx_9_2_to_48] = 32 - 25 * np.log10(theta[idx_9_2_to_48])

    return gain_gso_t, gain_gso_p
