from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import unittest
import csv

import antenna

class TestEnhancedAntenna(unittest.TestCase):

  def test_standard_gain_ver_hor(self):
      #dirs = [{'hor':3.5,'ver':-30},{'hor':47.3,'ver':45},{'hor':342,'ver':70}]
      #gains = antenna.GetStandardAntennaGainsHorAndVer(dirs,30,10,peak_ant_gain = 5)
      #self.assertEqual(np.max(np.abs(gains - 5 * np.ones(4))), 0)
      
      ant_az = 20
      downtilt = 0
      beamwidth_hor = 120
      beamwidth_ver = 60
      peak_gain = 10

      dirs = {'hor':20,'ver':0}

      alpha = dirs['hor']
      theta_r = alpha - ant_az
      theta_r = np.atleast_1d(theta_r)
      theta_r[theta_r > 180] -= 360
      theta_r[theta_r < -180] += 360

      beta = dirs['ver']
      phi_r = beta + downtilt*np.cos(theta_r*180/np.pi) 

      dirs_relative_boresight = {}
      dirs_relative_boresight['hor'] = theta_r
      dirs_relative_boresight['ver'] = phi_r    

      [hor_gain,ver_gain] = antenna.GetStandardAntennaGainsHorAndVer(dirs_relative_boresight,ant_azimuth = ant_az,ant_mech_downtilt = downtilt,
                                                                     ant_hor_beamwidth = beamwidth_hor,ant_ver_beamwidth = beamwidth_ver,peak_ant_gain = peak_gain)
      if not isinstance(dirs,list):
        if isinstance(hor_gain,np.ndarray):
          hor_gain = hor_gain[0]
        if isinstance(ver_gain,np.ndarray):
          ver_gain = ver_gain[0]   

      np.testing.assert_array_equal([hor_gain,ver_gain],[10,10])

      ant_az = 0
      dirs = {'hor':60,'ver':30}
      alpha = dirs['hor']
      theta_r = alpha - ant_az
      theta_r = np.atleast_1d(theta_r)
      theta_r[theta_r > 180] -= 360
      theta_r[theta_r < -180] += 360

      beta = dirs['ver']
      phi_r = beta + downtilt*np.cos(theta_r*180/np.pi) 

      dirs_relative_boresight = {}
      dirs_relative_boresight['hor'] = theta_r
      dirs_relative_boresight['ver'] = phi_r 

      [hor_gain,ver_gain] = antenna.GetStandardAntennaGainsHorAndVer(dirs_relative_boresight,ant_azimuth = ant_az,ant_mech_downtilt = downtilt,
                                                                     ant_hor_beamwidth = beamwidth_hor,ant_ver_beamwidth = beamwidth_ver,peak_ant_gain = peak_gain)
      if not isinstance(dirs,list):
        if isinstance(hor_gain,np.ndarray):
          hor_gain = hor_gain[0]
        if isinstance(ver_gain,np.ndarray):
          ver_gain = ver_gain[0]      
      
      np.testing.assert_array_equal([hor_gain,ver_gain],[10-3,10-3])

      ant_az = 45
      downtilt = 0
      beamwidth_hor = 120
      beamwidth_ver = 20
      peak_gain = 10

      dirs = {'hor':-15,'ver':10}
      alpha = dirs['hor']
      theta_r = alpha - ant_az
      theta_r = np.atleast_1d(theta_r)
      theta_r[theta_r > 180] -= 360
      theta_r[theta_r < -180] += 360

      beta = dirs['ver']
      phi_r = beta + downtilt*np.cos(theta_r*180/np.pi) 

      dirs_relative_boresight = {}
      dirs_relative_boresight['hor'] = theta_r
      dirs_relative_boresight['ver'] = phi_r 

      [hor_gain,ver_gain] = antenna.GetStandardAntennaGainsHorAndVer(dirs_relative_boresight,ant_azimuth = ant_az,ant_mech_downtilt = downtilt,
                                                                     ant_hor_beamwidth = beamwidth_hor,ant_ver_beamwidth = beamwidth_ver,peak_ant_gain = peak_gain)     

      if not isinstance(dirs,list):
          if isinstance(hor_gain,np.ndarray):
            hor_gain = hor_gain[0]
          if isinstance(ver_gain,np.ndarray):
            ver_gain = ver_gain[0]
             

      np.testing.assert_array_equal([hor_gain,ver_gain],[10-3,10-3])

  def test_GetAntennaGainsFromGivenPattern(self):
      
      hor_pattern = {}
      hor_pattern['angle'] = list(range(-180,180,1))
      hor_pattern['gain'] = list(range(0,360,1))
      
      ver_pattern = {}
      ver_pattern['angle'] = list(range(-90,270,1))
      ver_pattern['gain'] = list(range(0,360,1))

      ant_azimuth = 0
      ant_mech_downtilt = 0
      dirs = {'hor':20.5,'ver':10.5}

      alpha = dirs['hor']
      theta_r = alpha - ant_azimuth
      theta_r = np.atleast_1d(theta_r)      
      theta_r[theta_r > 180] -= 360
      theta_r[theta_r < -180] += 360

      beta = dirs['ver']
      phi_r = beta + ant_mech_downtilt*np.cos(theta_r*180/np.pi) 

      dirs_relative_boresight = {}
      dirs_relative_boresight['hor'] = theta_r
      dirs_relative_boresight['ver'] = phi_r   

      [g_h_theta_r, g_v_phi_r, g_v_phi_rsup] = antenna.GetAntennaGainsFromGivenPattern(dirs_relative_boresight,hor_pattern,ver_pattern,ant_azimuth,ant_mech_downtilt)  

      
      if not isinstance(dirs,list):
        if isinstance(g_h_theta_r,np.ndarray):
          g_h_theta_r = g_h_theta_r[0]
        if isinstance(g_v_phi_r,np.ndarray):
          g_v_phi_r = g_v_phi_r[0]   
          g_v_phi_rsup = g_v_phi_rsup[0]      
      

      np.testing.assert_array_equal([g_h_theta_r, g_v_phi_r, g_v_phi_rsup],[200.5,100.5,259.5])
      
  def test_GetTwoDimensionalAntennaGain(self):
      
      hor_pattern = {}
      hor_pattern['angle'] = list(range(-180,180,1))
      hor_pattern['gain'] = list(range(0,360,1))
      
      ver_pattern = {}
      ver_pattern['angle'] = list(range(-90,270,1))
      ver_pattern['gain'] = list(range(0,360,1))

      ant_azimuth = 0
      peak_ant_gain = 0
      ant_mech_downtilt = 0

      dirs = {'hor':20.5,'ver':10.5}

      alpha = dirs['hor']
      theta_r = alpha - ant_azimuth
      theta_r = np.atleast_1d(theta_r)      
      theta_r[theta_r > 180] -= 360
      theta_r[theta_r < -180] += 360

      beta = dirs['ver']
      phi_r = beta + ant_mech_downtilt*np.cos(theta_r*180/np.pi) 

      dirs_relative_boresight = {}
      dirs_relative_boresight['hor'] = theta_r
      dirs_relative_boresight['ver'] = phi_r      
      
      [g_h_theta_r, g_v_phi_r, g_v_phi_rsup] = antenna.GetAntennaGainsFromGivenPattern(dirs_relative_boresight,hor_pattern,ver_pattern,ant_azimuth,ant_mech_downtilt) 

      if not isinstance(dirs,list):
        if isinstance(g_h_theta_r,np.ndarray):
          g_h_theta_r = g_h_theta_r[0]
        if isinstance(g_v_phi_r,np.ndarray):
          g_v_phi_r = g_v_phi_r[0]   
          g_v_phi_rsup = g_v_phi_rsup[0]    

      gain_two_dimensional = antenna.GetTwoDimensionalAntennaGain(dirs,g_h_theta_r,g_v_phi_r,g_v_phi_rsup,
                                                                  hor_pattern['gain'][0],hor_pattern['gain'][179],peak_ant_gain)
                                                                  

  def test_MethodB1basedAntennaGainCalculation(self):
      
      hor_pattern = {}
      #hor_antenna_patt_filename = '3GHz_450bHG_SM_BH_INT_AZ.csv'
      hor_antenna_patt_filename = 'simulated_data_az.csv'
      angles = []
      gains = []
      with open(hor_antenna_patt_filename,'r') as csvfile:
         csv_reader = csv.reader(csvfile,delimiter='\t')
         for row in csv_reader:
            if any(row):
              angles.append(float(row[0]))            
              gains.append(float(row[1]))
      hor_pattern['angle'] = list(angles)
      hor_pattern['gain'] = list(gains)
     

      ver_pattern = {}
      ver_antenna_patt_filename = 'simulated_data_el.csv'
      angles = []
      gains = []      
      with open(ver_antenna_patt_filename) as csvfile:
         csv_reader = csv.reader(csvfile,delimiter='\t')
         for row in csv_reader:
            if any(row):
              angles.append(float(row[0]))            
              gains.append(float(row[1]))              
      ver_pattern['angle'] = list(angles)
      ver_pattern['gain'] = list(gains)

      two_dimensional_gain_filename = 'simulated_data_two_dimensional_gain.csv'
      gain_two_dimensional =[]
      with open(two_dimensional_gain_filename) as csvfile:
         csv_reader = csv.reader(csvfile,delimiter='\t')
         for row in csv_reader:
            if any(row):
                       
              gain_two_dimensional.append(row)              
         
      
      #hor_pattern['angle'] = list(range(-180,180,1))
      #hor_pattern['gain'] = list(range(0,360,1))
      
      
      #ver_pattern['angle'] = list(range(-90,270,1))
      #ver_pattern['gain'] = list(range(0,360,1))

      #ant_azimuth = 20
      #ant_mech_downtilt = 5
      #peak_ant_gain = 10

      ant_azimuth = 0
      ant_mech_downtilt = 0
      peak_ant_gain = 18.8

      dirs = {'hor':50,'ver':20}

      gain  = antenna.MethodB1basedAntennaGainCalculation(dirs, ant_azimuth, peak_ant_gain, hor_pattern, ver_pattern, ant_mech_downtilt) 

      alpha = dirs['hor']
      #azimuth angle of the line between the CBSD main beam and the receiver location relative to the CBSD antenna boresight 
      theta_r = alpha - ant_azimuth

      beta = dirs['ver']
      #vertical angle of the line between the CBSD main beam and the receiver location relative to the CBSD antenna boresight 
      phi_r = beta + ant_mech_downtilt*np.cos(theta_r*180/np.pi)    

      angles_list = list(range(-180,180,1))

      theta_r_idx = [i for i,j in enumerate(angles_list) if j == theta_r]
      phi_r_idx = [i for i,j in enumerate(angles_list) if j ==phi_r]
      if any(theta_r_idx):
        if any(phi_r_idx):
          gain_at_given_dir = float(gain_two_dimensional[phi_r_idx[0]][theta_r_idx[0]])
          diff = gain - gain_at_given_dir
          print_str = "calculated gain is within " + str(abs(float(diff))) + " dB of actual gain"
          print(print_str)


  def test_MethodCbasedAntennaGainCalculation(self):
      
      dirs = {'hor':20,'ver':0}
      ant_azimuth = 20
      peak_ant_gain = 10
      
      ant_hor_beamwidth = 120

      ant_mech_downtilt = 0      
      ant_ver_beamwidth = 60
      
      ant_fbr = 10

      gain  = antenna.MethodCbasedAntennaGainCalculation(dirs, ant_azimuth, peak_ant_gain, ant_mech_downtilt, ant_hor_beamwidth, 
                                                         ant_ver_beamwidth,ant_fbr)
      
  def test_MethodDbasedAntennaGainCalculation(self):
      
      dirs = {'hor':20,'ver':0}
      ant_azimuth = 20
      peak_ant_gain = 10
      ant_fbr = 10

      hor_pattern = {}
      hor_pattern['angle'] = list(range(-180,180,1))
      hor_pattern['gain'] = list(range(0,360,1))

      ant_mech_downtilt = 0
      ant_ver_beamwidth = 60
      
      ant_fbr = 10

      gain  = antenna.MethodDbasedAntennaGainCalculation(dirs, ant_azimuth, peak_ant_gain, hor_pattern, ant_mech_downtilt, 
                                                         ant_ver_beamwidth,ant_fbr)
      
  def test_MethodEbasedAntennaGainCalculation(self):
      
      dirs = {'hor':20,'ver':0}
      ant_azimuth = 20
      peak_ant_gain = 10
      
      hor_pattern = {}
      hor_pattern['angle'] = list(range(-180,180,1))
      hor_pattern['gain'] = list(range(0,360,1))

      gain  = antenna.MethodEbasedAntennaGainCalculation(dirs, ant_azimuth, peak_ant_gain, hor_pattern)

          

if __name__ == '__main__':
  unittest.main()