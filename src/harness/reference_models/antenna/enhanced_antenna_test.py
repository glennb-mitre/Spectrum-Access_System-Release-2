
import numpy as np
import unittest
import csv
import os
import json

import antenna

test_data_dir = os.path.dirname(os.path.realpath(__file__)) + '/test data/'

class TestEnhancedAntenna(unittest.TestCase):

  def test_calculate_antenna_gain(self):
     cbsd_filename = test_data_dir + 'device_a1.json'
     with open(cbsd_filename) as fd:
      tx =  json.load(fd)
     rx = {}
     rx['latitude'] = 39.9
     rx['longitude'] = -120.5
     rx['height'] = 40
     antenna.calculate_antenna_gain_EAP(tx,rx)

                                                                
  def test_MethodB1basedAntennaGainCalculation(self):
      
      hor_pattern = {}
      #hor_antenna_patt_filename = '3GHz_450bHG_SM_BH_INT_AZ.csv'
      hor_antenna_patt_filename = test_data_dir + 'simulated_data_az.csv'
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
      ver_antenna_patt_filename = test_data_dir + 'simulated_data_el.csv'
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

      two_dimensional_gain_filename = test_data_dir + 'simulated_data_two_dimensional_gain.csv'
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

      test_angles_hor = list(range(-180,180,1))
      test_angles_ver = list(range(-180,180,1))
      """ test_angles_hor = list([-6])
      test_angles_ver = list([-8])  """     
      gain_hor_ver = [[0 for i in range(0,len(test_angles_hor))] for j in range(0,len(test_angles_ver))]
      for idx1,angle_ver in enumerate(test_angles_ver):
        for idx2,angle_hor in enumerate(test_angles_hor):
          dirs = {'hor':angle_hor,'ver':angle_ver}
          gain  = antenna.antenna_gain_method_b1(dirs, ant_azimuth, peak_ant_gain, hor_pattern, ver_pattern, ant_mech_downtilt)
          gain_hor_ver[idx1][idx2] = gain
      
      
      results_file = test_data_dir + 'results_updated.csv'
      with open(results_file,'w') as csvfile:
         csvwriter = csv.writer(csvfile)
         csvwriter.writerows(gain_hor_ver)

      #gain  = antenna.MethodB1basedAntennaGainCalculation(dirs, ant_azimuth, peak_ant_gain, hor_pattern, ver_pattern, ant_mech_downtilt) 

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

      gain  = antenna.antenna_gain_method_c(dirs, ant_azimuth, peak_ant_gain, ant_mech_downtilt, ant_hor_beamwidth,
                                     ant_ver_beamwidth, ant_fbr)
      
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

      gain  = antenna.antenna_gain_method_d(dirs, ant_azimuth, peak_ant_gain, hor_pattern, ant_mech_downtilt,
                                     ant_ver_beamwidth, ant_fbr)
      
  def test_MethodEbasedAntennaGainCalculation(self):
      
      dirs = {'hor':20}
      ant_azimuth = 20
      peak_ant_gain = 10
      
      hor_pattern = {}
      hor_pattern['angle'] = list(range(-180,180,1))
      hor_pattern['gain'] = list(range(0,360,1))

      gain  = antenna.antenna_gain_method_e(dirs, ant_azimuth, peak_ant_gain, hor_pattern)
  
  
  def test_get_standard_gains_hor(self):
      
      # Vectorized vs scalar
      dirs = {'hor':[3.5, 47.3, 342]}
      ant_azimuth = 123.3
      peak_ant_gain = 12.4
      ant_beamwidth = 90     
      
      gains = antenna.get_standard_antenna_gain(dirs, 123.3, 90, 12.4)
      for k, hor in enumerate(dirs['hor']):
        dir = {'hor': hor}
        gain = antenna.get_standard_antenna_gain(dir, 123.3, 90, 12.4)
        self.assertEqual(gain, gains[k])

      dirs = {'hor':[0, 90, 180, 270]}
      ant_azimuth = 0
      peak_ant_gain = 5
      ant_beamwidth = None

          # Isotropic antenna
      gains = antenna.get_standard_antenna_gain(dirs,
                                        peak_ant_gain, ant_azimuth, ant_beamwidth)
      self.assertEqual(np.max(np.abs(
          gains - 5 * np.ones(4))), 0)
      
      dirs = {'hor':[0, 90, 180, 270]}
      ant_azimuth = 0
      peak_ant_gain = 5
      ant_beamwidth = 90

      gains = antenna.get_standard_antenna_gain(dirs, 5, None, 90)
      self.assertEqual(np.max(np.abs(
          gains - 5 * np.ones(4))), 0)
      
      dirs = {'hor':[0, 90, 180, 270]}
      ant_azimuth = 0
      peak_ant_gain = 5
      ant_beamwidth = 0      

      gains = antenna.get_standard_antenna_gain(dirs,5, 0, 0)
                                        
      self.assertEqual(np.max(np.abs(
          gains - 5 * np.ones(4))), 0)
      
      dirs = {'hor':[0, 90, 180, 270]}
      ant_azimuth = 0
      peak_ant_gain = 5
      ant_beamwidth = 360

      gains = antenna.get_standard_antenna_gain(dirs,5, 0, 360)
                                        
      self.assertEqual(np.max(np.abs(
          gains - 5 * np.ones(4))), 0)

      dirs = {'hor':180}
      ant_azimuth = 0
      peak_ant_gain = 10
      ant_beamwidth = 120
      # Back lobe: maximum attenuation
      gain = antenna.get_standard_antenna_gain(dirs, 10, 0, 120)
      self.assertEqual(gain, -10)

      # At beamwidth, cutoff by 3dB (by definition)
      dirs = {'hor':60}
      ant_azimuth = 0
      peak_ant_gain = 10
      ant_beamwidth = 120
      
      gain = antenna.get_standard_antenna_gain(dirs, 10, 0, 120)
      self.assertEqual(gain, 10-3)

      dirs = {'hor':5.5}
      ant_azimuth = 50.5
      peak_ant_gain = 10
      ant_beamwidth = 90
      gain = antenna.get_standard_antenna_gain(dirs, 10, 50.5, 90)
      self.assertEqual(gain, 10-3)

      # Bore sight: full gain
      dirs = {'hor':50.5}
      ant_azimuth = 50.5
      peak_ant_gain = 10
      ant_beamwidth = 90      
      gain = antenna.get_standard_antenna_gain(dirs, 10, 50.5, 90)
      self.assertEqual(gain, 10)

      # At half beamwidth, -0.75dB + integer values well managed
      dirs = {'hor':25}
      ant_azimuth = 50
      peak_ant_gain = 10
      ant_beamwidth = 100      
      gain = antenna.get_standard_antenna_gain(dirs, 10, 50, 100)
      self.assertEqual(gain, 10-0.75)

      # At twice beamwidth, -12dB
      dirs = {'hor':310}
      ant_azimuth = 50
      peak_ant_gain = 10
      ant_beamwidth = 100      
      gain = antenna.get_standard_antenna_gain(dirs, 10, 50, 100)
      self.assertEqual(gain, 10-12)


  def test_get_standard_gains_hor_ver(self):
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

      [hor_gain,ver_gain] = antenna.get_standard_antenna_gains_hor_ver(dirs_relative_boresight, ant_azimuth = ant_az, ant_mech_downtilt = downtilt,
                                                          ant_hor_beamwidth = beamwidth_hor, ant_ver_beamwidth = beamwidth_ver, peak_ant_gain = peak_gain)
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

      [hor_gain,ver_gain] = antenna.get_standard_antenna_gains_hor_ver(dirs_relative_boresight, ant_azimuth = ant_az, ant_mech_downtilt = downtilt,
                                                          ant_hor_beamwidth = beamwidth_hor, ant_ver_beamwidth = beamwidth_ver, peak_ant_gain = peak_gain)
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

      [hor_gain,ver_gain] = antenna.get_standard_antenna_gains_hor_ver(dirs_relative_boresight, ant_azimuth = ant_az, ant_mech_downtilt = downtilt,
                                                          ant_hor_beamwidth = beamwidth_hor, ant_ver_beamwidth = beamwidth_ver, peak_ant_gain = peak_gain)

      if not isinstance(dirs,list):
          if isinstance(hor_gain,np.ndarray):
            hor_gain = hor_gain[0]
          if isinstance(ver_gain,np.ndarray):
            ver_gain = ver_gain[0]
             

      np.testing.assert_array_equal([hor_gain,ver_gain],[10-3,10-3])

  def test_calculate_gain_from_given_patterns(self):
      
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

      [g_h_theta_r, g_v_phi_r, g_v_phi_rsup] = antenna.calculate_gain_from_given_patterns(dirs_relative_boresight, hor_pattern, ver_pattern, ant_azimuth, ant_mech_downtilt)

      
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
      
      [g_h_theta_r, g_v_phi_r, g_v_phi_rsup] = antenna.calculate_gain_from_given_patterns(dirs_relative_boresight, hor_pattern, ver_pattern, ant_azimuth, ant_mech_downtilt)

      if not isinstance(dirs,list):
        if isinstance(g_h_theta_r,np.ndarray):
          g_h_theta_r = g_h_theta_r[0]
        if isinstance(g_v_phi_r,np.ndarray):
          g_v_phi_r = g_v_phi_r[0]   
          g_v_phi_rsup = g_v_phi_rsup[0]    

      gain_two_dimensional = antenna.get_2d_antenna_gain(dirs, g_h_theta_r, g_v_phi_r, g_v_phi_rsup,
                                                         hor_pattern['gain'][0], hor_pattern['gain'][179], peak_ant_gain)      
  

if __name__ == '__main__':
  unittest.main()
