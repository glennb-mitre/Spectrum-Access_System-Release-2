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
import numpy as np
import os
import csv
from reference_models.propagation import wf_itm

# Frequency used in propagation model (in MHz) [R2-SGN-04]
FREQ_PROP_MODEL_MHZ = 3625.0
ANT_PAT_DATABASE_FILENAME = os.path.dirname(os.path.realpath(__file__)) + '/antenna database/antennaPatternDatabase.csv'

def import_antenna_pattern_database():
    ant_pat_file = ANT_PAT_DATABASE_FILENAME
    ant_database = []
    with open(ant_pat_file) as f:
        for line in csv.DictReader(f):
            ant_database.append(line)
    return ant_database
            


def calculate_antenna_gain_EAP(tx, rx):
    
    _, incidence_angles, _ = wf_itm.CalcItmPropagationLoss(
                                                            tx['installationParam']['latitude'], tx['installationParam']['longitude'], tx['installationParam']['height'],
                                                            rx['latitude'], rx['longitude'], rx['height'],
                                                            tx['installationParam']['indoorDeployment'], reliability=-1,
                                                            freq_mhz=FREQ_PROP_MODEL_MHZ)
    
    dirs = {}
    dirs["hor"] = incidence_angles.hor_cbsd
    dirs["ver"] = incidence_angles.ver_cbsd
    ant_database = import_antenna_pattern_database()
    gain  = []
    
    if 'azimuth' not in tx['installationParam'] or not  tx['installationParam']['azimuth'] :
        gain  = antenna_gain_method_f(dirs,tx['installationParam']['antennaGain'])
        return gain
    
    if ('frontToBackRatio' not in tx['installationParam']) or not  tx['installationParam']['frontToBackRatio']:
        tx['installationParam']['frontToBackRatio'] = 20

    if 'antennaModel' in tx['installationParam']:
        if tx['installationParam']['antennaModel']:        
            antennaModel = tx['installationParam']['antennaModel'] 
            if 'horizontalPattern' in antennaModel :
                if antennaModel['horizontalPattern']:
                    antennaPatternId = antennaModel['horizontalPattern']['antennaPatternId']
                    for i, dic in enumerate(ant_database):
                        if dic['antennaPatternId'] == antennaPatternId:
                            patt_filename = os.path.dirname(os.path.realpath(__file__)) + '/antenna database/' + dic['azimuthRadiationPattern']
                            break
                    hor_pattern = {}
                    angles = []
                    gains = []
                    with open(patt_filename,'r') as csvfile:
                        csv_reader = csv.reader(csvfile,delimiter=',')
                        for row in csv_reader:
                            if any(row):
                                angles.append(float(row[0]))            
                                gains.append(float(row[1]))
                    hor_pattern['angle'] = list(angles)
                    hor_pattern['gain'] = list(gains)
                
                    if 'antennaDowntilt'in tx['installationParam']:
                        if tx['installationParam']['antennaDowntilt']:
                            if 'verticalPattern' in antennaModel:
                                if antennaModel['verticalPattern']:                               
                                    ver_pattern = {}
                                    angles = []
                                    gains = []      
                                    with open(patt_filename) as csvfile:
                                        csv_reader = csv.reader(csvfile,delimiter=',')
                                        for row in csv_reader:
                                            if any(row):
                                                angles.append(float(row[0]))            
                                                gains.append(float(row[1]))              
                                    ver_pattern['angle'] = list(angles)
                                    ver_pattern['gain'] = list(gains)

                                    gain  = antenna_gain_method_b1(
                                        dirs, tx['installationParam']['azimuth'], tx['installationParam']['antennaGain'], 
                                        hor_pattern, ver_pattern,tx['installationParam']['antennaDowntilt'])[0]
                                    
                                    return gain
                                
                            if 'antennaVerticalBeamwidth' in tx['installationParam']:
                                if tx['installationParam']['antennaVerticalBeamwidth']:
                                    gain = antenna_gain_method_d(dirs, tx['installationParam']['azimuth'], tx['installationParam']['antennaGain'], 
                                                hor_pattern, tx['installationParam']['antennaDowntilt'],
                                                tx['installationParam']['antennaVerticalBeamwidth'], 
                                                tx['installationParam']['frontToBackRatio'])[0]
                                    
                                    return gain
                                
                    if not gain:
                        gain  = antenna_gain_method_e(dirs, tx['installationParam']['azimuth'], tx['installationParam']['antennaGain'], hor_pattern)[0]

                        return gain
                
                      
    if all(k in tx['installationParam'] for k in ('antennaBeamwidth','antennaDowntilt', 'antennaVerticalBeamwidth')):
        if  all((tx['installationParam']['antennaBeamwidth'],tx['installationParam']['antennaDowntilt'],tx['installationParam']['antennaVerticalBeamwidth'])):
            gain = antenna_gain_method_c(dirs, tx['installationParam']['antennaGain'], tx['installationParam']['azimuth'],  
                                tx['installationParam']['antennaDowntilt'], tx['installationParam']['antennaBeamwidth'],
                                tx['installationParam']['antennaVerticalBeamwidth'], tx['installationParam']['frontToBackRatio'])[0]
            return gain

    if not gain:
        gain  = antenna_gain_method_f(dirs,tx['installationParam']['antennaGain'])

    
        
    return gain
        
    
def antenna_gain_method_b1(dirs, ant_az, peak_ant_gain,
                    hor_pattern, ver_pattern, downtilt):
    """REL2-R3-SGN-52105: Method B1 based antenna gain calculation.
      Use of two one-dimensional antenna patterns (denoted as GH(theta) and GV(phi), respectively)
      derived from the CBSD Registration parameters.

      Directions and azimuth are defined compared to the north in clockwise
      direction and shall be within [0..360] degrees.

      Inputs:
        dirs:           Horizontal and vertical directions (degrees) at which the gain needs to be
                        calculated Either a scalar or an iterable.
        ant_az:         Antenna azimuth (degrees).
        peak_ant_gain:  cbsd antenna gain(dBi) at boresight
        hor_pattern:    antenna gain pattern in horizontal plane
        ver_pattern:    antenna gain pattern in vertical plane
        donwtilt:       Antenna mechanical downtilt(degrees), limited to +-15 degrees

      Returns:
        The CBSD two dimensional antenna gains (in dB) relative to peak antenna gain
        Either a scalar if dirs is scalar or an ndarray otherwise.
   """

    alpha = dirs['hor']
    # azimuth angle of the line between the CBSD main beam and the receiver location relative to
    # the CBSD antenna boresight
    theta_r = alpha - ant_az
    theta_r = np.atleast_1d(theta_r)
    theta_r[theta_r > 180] -= 360
    theta_r[theta_r < -180] += 360

    if downtilt < -15:
        downtilt = -15
    if downtilt > 15:
        downtilt = 15

    beta = dirs['ver']
    # vertical angle of the line between the CBSD main beam and the receiver location relative to
    # the CBSD antenna boresight
    phi_r = beta + downtilt * np.cos(theta_r * 180 / np.pi)

    dirs_relative_boresight = {}
    dirs_relative_boresight['hor'] = theta_r
    dirs_relative_boresight['ver'] = phi_r

    # REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step a

    # horizontal gain at thetaR, G_H (thetaR), vertical gains at phiR and at 180-phiR angle,
    # G_V (phiR) and G_V (180-phiR)
    [g_h_theta_r, g_v_phi_r, g_v_phi_rsup] = calculate_gain_from_given_patterns(dirs_relative_boresight,
                                                                        hor_pattern,
                                                                        ver_pattern,
                                                                        ant_az, downtilt)
    # REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step b
    g_cbsd = get_2d_antenna_gain(dirs, g_h_theta_r, g_v_phi_r, g_v_phi_rsup,
                                 hor_pattern['gain'][180], hor_pattern['gain'][0],
                                 peak_ant_gain)

    gain_two_dimensional = g_cbsd

    return gain_two_dimensional


def antenna_gain_method_c(dirs, ant_az, peak_ant_gain, downtilt, hor_beamwidth,
                   ver_beamwidth, fbr):
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
    hor_beamwidth:  antenna 3dB beamwidth in horizontal plane
    ver_beamwidth:  antenna 3dB beamwidth in vertical plane
    donwtilt:       antenna mechanical downtilt(degrees), positive below horizon.
    fbr:            antenna front-to-back-ratio(dB)

    Returns:
    The CBSD two-dimensional antenna gains (in dB) relative to peak antenna gain
    Either a scalar if dirs is scalar or an ndarray otherwise.
    """

    alpha = dirs['hor']
    # azimuth angle of the line between the CBSD main beam and the receiver location relative to
    # the CBSD antenna boresight
    theta_r = alpha - ant_az
    theta_r = np.atleast_1d(theta_r)
    theta_r[theta_r > 180] -= 360
    theta_r[theta_r < -180] += 360

    beta = dirs['ver']
    # vertical angle of the line between the CBSD main beam and the receiver location relative to
    # the CBSD antenna boresight
    phi_r = beta + downtilt * np.cos(theta_r * 180 / np.pi)

    if downtilt < -15:
        downtilt = -15
    if downtilt > 15:
        downtilt = 15

    dirs_relative_boresight = {}
    dirs_relative_boresight['hor'] = theta_r
    dirs_relative_boresight['ver'] = phi_r

    # horizontal gain at thetaR, vertical gains at phiR
    [g_h_theta_r, g_v_phi_r] = get_standard_antenna_gains_hor_ver(dirs_relative_boresight,
                                                     ant_az, peak_ant_gain,
                                                     downtilt, hor_beamwidth,
                                                     ver_beamwidth, ant_fbr=fbr)

    # in degrees
    theta_0 = 0
    theta_180 = 180
    phi_r_sup = 180 - phi_r  # supplementary angle of phi

    dirs_0 = {}
    dirs_180 = {}
    dirs_phi_r_sup = {}

    dirs_0['hor'] = theta_0
    dirs_180['hor'] = theta_180
    dirs_phi_r_sup['ver'] = phi_r_sup

    # horizontal gain at 0 degrees, G_H (0)
    [g_h_theta_0, _] = get_standard_antenna_gains_hor_ver(dirs_0, ant_az, peak_ant_gain,
                                             ant_hor_beamwidth=hor_beamwidth,
                                             ant_fbr=fbr)
    # horizontal gain at 180 degrees, G_H (180)
    [g_h_theta_180, _] = get_standard_antenna_gains_hor_ver(dirs_180, ant_az, peak_ant_gain,
                                               ant_hor_beamwidth=hor_beamwidth,
                                               ant_fbr=fbr)
    # vertical gain at 180-phiR vertical angle, G_V (180-phiR)
    [_, g_v_phi_r_sup] = get_standard_antenna_gains_hor_ver(dirs_phi_r_sup, ant_az, peak_ant_gain,
                                               ant_mech_downtilt=downtilt,
                                               ant_ver_beamwidth=ver_beamwidth,
                                               ant_fbr=fbr)
    # REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step b
    g_cbsd = get_2d_antenna_gain(dirs, g_h_theta_r, g_v_phi_r, g_v_phi_r_sup,
                                 g_h_theta_0, g_h_theta_180, peak_ant_gain)

    gain_two_dimensional = g_cbsd

    return gain_two_dimensional


def antenna_gain_method_d(dirs, ant_az, peak_ant_gain, hor_patt, downtilt, ver_beamwidth, fbr):
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
    The CBSD two dimensional antenna gains (in dB) relative to peak antenna gain.
    Either a scalar if dirs is scalar or an ndarray otherwise.
    """

    alpha = dirs['hor']
    # azimuth angle of the line between the CBSD main beam and the receiver location relative to
    # the CBSD antenna boresight
    theta_r = alpha - ant_az
    theta_r = np.atleast_1d(theta_r)
    theta_r[theta_r > 180] -= 360
    theta_r[theta_r < -180] += 360

    beta = dirs['ver']
    # vertical of the line between the CBSD main beam and the receiver location relative to
    # the CBSD antenna boresight
    phi_r = beta + downtilt * np.cos(theta_r * 180 / np.pi)

    if downtilt < -15:
        downtilt = -15
    if downtilt > 15:
        downtilt = 15

    dirs_relative_boresight = {}
    dirs_relative_boresight['hor'] = theta_r
    dirs_relative_boresight['ver'] = phi_r

    # in degrees
    theta_0 = 0
    theta_180 = 180

    phi_r_sup = 180 - phi_r

    dirs_0 = {}
    dirs_180 = {}
    dirs_phi_r_sup = {}

    dirs_0['hor'] = theta_0
    dirs_180['hor'] = theta_180
    dirs_phi_r_sup['ver'] = phi_r_sup

    # horizontal gain at thetaR angle, G_H (thetaR)
    [g_h_theta_r, _, _] = calculate_gain_from_given_patterns(dirs_relative_boresight,
                                                     hor_pattern=hor_patt,
                                                     ant_azimuth=ant_az)
    # G_H(0)
    g_h_theta_0 = hor_patt['gain'][180]
    # G_H(180)
    g_h_theta_180 = hor_patt['gain'][0]

    # G_V(phiR)
    [_, g_v_phi_r] = get_standard_antenna_gains_hor_ver(dirs_relative_boresight, ant_az,
                                           peak_ant_gain,
                                           ant_mech_downtilt=downtilt,
                                           ant_ver_beamwidth=ver_beamwidth, ant_fbr=fbr)
    # G_V(180-phiR)
    [_, g_v_phi_r_sup] = get_standard_antenna_gains_hor_ver(dirs_phi_r_sup, ant_az, peak_ant_gain,
                                               ant_mech_downtilt=downtilt,
                                               ant_ver_beamwidth=ver_beamwidth,
                                               ant_fbr=fbr)
    # REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step b
    g_cbsd = get_2d_antenna_gain(dirs_relative_boresight, g_h_theta_r, g_v_phi_r,
                                 g_v_phi_r_sup, g_h_theta_0,
                                 g_h_theta_180, peak_ant_gain)
    gain_two_dimensional = g_cbsd

    return gain_two_dimensional


def antenna_gain_method_e(dirs, ant_az, peak_ant_gain, hor_patt):
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

    alpha = dirs['hor']
    # azimuth angle of the line between the CBSD main beam and the receiver location relative
    # to the CBSD antenna boresight
    theta_r = alpha - ant_az
    theta_r = np.atleast_1d(theta_r)
    theta_r[theta_r > 180] -= 360
    theta_r[theta_r < -180] += 360

    dirs_relative_boresight = {}
    dirs_relative_boresight['hor'] = theta_r
    dirs_relative_boresight['ver'] = 0

    # in degrees
    theta_0 = 0
    theta_180 = 180

    dirs_0 = {}
    dirs_180 = {}

    dirs_0['hor'] = theta_0
    dirs_180['hor'] = theta_180

    # horizontal gain at thetaR angle, G_H (thetaR)
    [g_h_theta_r, _, _] = calculate_gain_from_given_patterns(dirs_relative_boresight,
                                                     hor_pattern=hor_patt,
                                                     ant_azimuth=ant_az)
    # G_H(0)
    g_h_theta_0 = hor_patt['gain'][180]
    # G_H(180)
    g_h_theta_180 = hor_patt['gain'][0]

    g_v_phi_r = 0
    g_v_phi_r_sup = 0

    # REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step b
    g_cbsd = get_2d_antenna_gain(dirs_relative_boresight, g_h_theta_r, g_v_phi_r,
                                 g_v_phi_r_sup, g_h_theta_0,
                                 g_h_theta_180, peak_ant_gain)
    gain_two_dimensional = g_cbsd

    return gain_two_dimensional

def antenna_gain_method_f(dirs,peak_ant_gain,ant_az=None,hor_beamwidth=None):
    """Use of the horizontal antenna pattern (denoted as GH(θ)) derived 
    from the CBSD Registration parameters (i.e., Release 1 method specified in R2-SGN-20 [1]).
    
    Directions and azimuth are defined compared to the north in clockwise
    direction and shall be within [0..360] degrees.    
    
    Inputs:

      dirs:       Ray directions in horizontal plane (degrees).
                      Either a scalar or an iterable.
      ant_az:     Antenna azimuth (degrees).
      hor_beamwidth:  Antenna 3dB cutoff beamwidth (degrees).
                      If None, then antenna is isotropic (default).
      peak_ant_gain:       Antenna gain (dBi).
    
    
    Returns:
    The CBSD  antenna gains (in dBi) in horizontal plane relative to peak antenna gain, 
    Either a scalar if dirs is scalar or an ndarray otherwise.
    
    """

    gain = get_standard_antenna_gain(dirs,peak_ant_gain,ant_az,hor_beamwidth)

    return gain

def get_standard_antenna_gain(dirs,peak_ant_gain,ant_az=None,hor_beamwidth=None):
    
    """Computes the antenna gains from a standard antenna defined by beamwidth.
    (This has been copied from the Rel-1 codebase)

    See R2-SGN-20.
    This uses the standard 3GPP formula for pattern derivation from a given
    antenna 3dB cutoff beamwidth.
    Directions and azimuth are defined compared to the north in clockwise
    direction and shall be within [0..360] degrees.

    Inputs:
      dirs:       Ray directions in horizontal plane (degrees).
                      Either a scalar or an iterable.
      ant_az:     Antenna azimuth (degrees).
      hor_beamwidth:  Antenna 3dB cutoff beamwidth (degrees).
                      If None, then antenna is isotropic (default).
      peak_ant_gain:       Antenna gain (dBi).

    Returns:
      The CBSD antenna gains (in dBi) in horizontal plane.
      Either a scalar if hor_dirs is scalar or an ndarray otherwise.
    """
    hor_dirs = dirs['hor']
    is_scalar = np.isscalar(hor_dirs)
    hor_dirs = np.atleast_1d(hor_dirs)

    if (hor_beamwidth is None or ant_az is None or
            hor_beamwidth == 0 or hor_beamwidth == 360):
        gains = peak_ant_gain * np.ones(hor_dirs.shape)
    else:
        bore_angle = hor_dirs - ant_az
        bore_angle[bore_angle > 180] -= 360
        bore_angle[bore_angle < -180] += 360
        gains = -12 * (bore_angle / float(hor_beamwidth)) ** 2
        gains[gains < -20] = -20.
        gains += peak_ant_gain

    if is_scalar:
        return gains[0]
    return gains    
    
def get_standard_antenna_gains_hor_ver(dirs, ant_azimuth=None, peak_ant_gain=0,
                          ant_mech_downtilt=None, ant_hor_beamwidth=None,
                          ant_ver_beamwidth=None, ant_fbr=None):
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

    dirs_keys = list(dirs.keys())

    if 'hor' in dirs_keys:
        theta_r = dirs['hor']
        theta_r = np.atleast_1d(theta_r)
        if (ant_hor_beamwidth is None or ant_azimuth is None or
                ant_hor_beamwidth == 0 or ant_hor_beamwidth == 360):
            g_h_theta_r = peak_ant_gain * np.ones(theta_r.shape)
        else:
            g_h_theta_r = -min([12 * (theta_r / float(ant_hor_beamwidth)) ** 2, ant_fbr])
            g_h_theta_r += peak_ant_gain

    if 'ver' in dirs_keys:
        phi_r = dirs['ver']
        phi_r = np.atleast_1d(phi_r)
        if (ant_ver_beamwidth is None or ant_mech_downtilt is None or
                ant_ver_beamwidth == 0 or ant_ver_beamwidth == 360):
            g_v_phi_r = peak_ant_gain * np.ones(phi_r.shape)
        else:
            g_v_phi_r = -min([12 * (phi_r / float(ant_ver_beamwidth)) ** 2, ant_fbr])
            g_v_phi_r += peak_ant_gain

    return g_h_theta_r, g_v_phi_r


def calculate_gain_from_given_patterns(dirs, hor_pattern=None, ver_pattern=None, ant_azimuth=None,
                               ant_mech_downtilt=None):
    """ REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step a

    Computes the gain at a given direction from a given antenna pattern(horizontal and vertical).

    Directions and azimuth are defined compared to the north in clockwise
    direction and shall be within [0..360] degrees.

    Inputs:
      hor_pattern: contains horizontal plane angles and associated gains
      ver_pattern: contains vertical plane angles and associated gains

      ant_azimuth:     Antenna azimuth (degrees).
      ant_mechanical_downtilt: antenna mechanical downtilt(degrees), limited to +-15 degrees

    Outputs:
      g_h_theta_r:  cbsd horizontal antenna gain(dB) at theta_r angle relative to peak antenna gain
      g_v_phi_r:    cbsd vertical antenna gain(dB) at phi_r angle, relative to peak antenna gain
      g_v_phi_rsup: cbsd vertical antenna gain(dB) at supplementary angle of phi_r(180-phi_r),
                    relative to peak antenna gain
    """

    hor_dir = dirs['hor']
    ver_dir = dirs['ver']

    theta_r = hor_dir
    phi_r = ver_dir

    g_h_theta_r = []
    g_v_phi_r = []
    g_v_phi_rsup = []

    if not hor_pattern == None:
        theta_list = hor_pattern['angle']
        g_h_list = hor_pattern['gain']
        theta_r_idx = [i for i, j in enumerate(theta_list) if j == theta_r]
        if theta_r_idx:
            g_h_theta_r = g_h_list[theta_r_idx[0]]
        else:
            theta_diff = [theta_r - i for i in theta_list]
            theta_diff_pos = [i for i in theta_diff if i > 0]
            theta_m = theta_list[theta_diff.index(min(theta_diff_pos))]

            theta_diff_neg = [i for i in theta_diff if i < 0]

            theta_m_1 = theta_list[theta_diff.index(max(theta_diff_neg))]

            theta_m_idx = [i for i, j in enumerate(theta_list) if j == theta_m]
            g_h_theta_m = g_h_list[theta_m_idx[0]]

            theta_m_1_idx = [i for i, j in enumerate(theta_list) if j == theta_m_1]
            g_h_theta_m_1 = g_h_list[theta_m_1_idx[0]]

            g_h_theta_r_interp = ((theta_m_1 - theta_r) * g_h_theta_m + (theta_r - theta_m) *
                                  g_h_theta_m_1) / (theta_m_1 - theta_m)
            g_h_theta_r = g_h_theta_r_interp

    if not ver_pattern == None:

        phi_list = list(ver_pattern['angle'])

        g_v_list = list(ver_pattern['gain'])
        phi_r_idx = [i for i, j in enumerate(phi_list) if j == phi_r]

        phi_r_supplementary_angle = 180 - phi_r
        phi_r_supplementary_angle = np.atleast_1d(phi_r_supplementary_angle)

        # if(phi_r_supplementary_angle>180 or phi_r_supplementary_angle<-180):
        # print("stop")

        phi_r_supplementary_angle[phi_r_supplementary_angle >= 180] -= 360

        phi_rs_idx = [i for i, j in enumerate(phi_list) if j == phi_r_supplementary_angle]

        if phi_r_idx:
            g_v_phi_r = g_v_list[phi_r_idx[0]]
        else:
            phi_diff = [phi_r - i for i in phi_list]
            phi_diff_pos = [i for i in phi_diff if i > 0]
            phi_n = phi_list[phi_diff.index(min(phi_diff_pos))]

            phi_diff_neg = [i for i in phi_diff if i < 0]

            phi_n_1 = phi_list[phi_diff.index(max(phi_diff_neg))]

            phi_n_idx = [i for i, j in enumerate(phi_list) if j == phi_n]
            g_v_phi_n = g_v_list[phi_n_idx[0]]

            phi_n_1_idx = [i for i, j in enumerate(phi_list) if j == phi_n_1]
            g_v_phi_n_1 = g_v_list[phi_n_1_idx[0]]

            g_v_phi_r_interp = ((phi_n_1 - phi_r) * g_v_phi_n + (phi_r - phi_n) * g_v_phi_n_1) /\
                               (phi_n_1 - phi_n)
            g_v_phi_r = g_v_phi_r_interp

        if phi_rs_idx:
            g_v_phi_rsup = g_v_list[phi_rs_idx[0]]
        else:
            phi_rsup_diff = [phi_r_supplementary_angle - i for i in phi_list]
            phi_rs_diff_pos = [i for i in phi_rsup_diff if i > 0]
            phi_k = phi_list[phi_rsup_diff.index(min(phi_rs_diff_pos))]

            phi_rs_diff_neg = [i for i in phi_rsup_diff if i < 0]
            phi_k_1 = phi_list[phi_rsup_diff.index(max(phi_rs_diff_neg))]

            phi_k_idx = [i for i, j in enumerate(phi_list) if j == phi_k]
            g_v_phi_k = g_v_list[phi_k_idx[0]]

            phi_k_1_idx = [i for i, j in enumerate(phi_list) if j == phi_k_1]
            g_v_phi_k_1 = g_v_list[phi_k_1_idx[0]]

            g_v_phi_rsup_interp = ((phi_k_1 - phi_r_supplementary_angle) * g_v_phi_k + (
                        phi_r_supplementary_angle - phi_k) * g_v_phi_k_1) / (phi_k_1 - phi_k)
            g_v_phi_rsup = g_v_phi_rsup_interp

    return g_h_theta_r, g_v_phi_r, g_v_phi_rsup


def get_2d_antenna_gain(dirs, hor_gain, ver_gain, ver_gain_sup_angle, hor_gain_0,
                        hor_gain_180, peak_ant_gain=0):
    """REL2-R3-SGN-52105: Method B1 based Antenna Gain Calculation, step b

    Computes the two-dimensional antenna gain at a given direction, from horizontal and
    vertical gain.

    Directions and azimuth are defined compared to the north in clockwise
    direction and shall be within [0..360] degrees.

    Inputs:
      dirs:                Horizontal and vertical directions at which antenna gain is to be
                           calculated (degrees). Either a scalar or an iterable.
      hor_gain:            antenna relative gain(w.r.t peak antenna gain) at the given
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
      gain_two_dimensional: cbsd two dimensional antenna gain(dB) relative to peak antenna gain

    """
    hor_dir = dirs['hor']

    g_h_theta_r = hor_gain
    g_0 = peak_ant_gain
    g_h_theta_0 = hor_gain_0
    g_h_theta_180 = hor_gain_180
    g_v_phi_r = ver_gain
    g_v_phi_rsup = ver_gain_sup_angle

    g_cbsd_relative = g_h_theta_r + ((1 - abs(hor_dir) / 180) * (g_v_phi_r - g_h_theta_0) +
                                     (abs(hor_dir) / 180) * (g_v_phi_rsup - g_h_theta_180))
    g_cbsd = g_cbsd_relative + g_0
    gain_two_dimensional = g_cbsd

    return gain_two_dimensional


def calculate_gain_from_hor_pattern(hor_dirs, ant_azimuth,
                               hor_pattern,
                               ant_gain=0):
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


def get_fss_gains(hor_dirs, ver_dirs,
                  fss_pointing_azimuth, fss_pointing_elevation,
                  fss_antenna_gain,
                  w_1=0, w_2=1.0):
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


def get_gso_gains(theta, nominal_gain):
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