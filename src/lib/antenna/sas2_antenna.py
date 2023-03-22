# Copyright 2023 SAS Release 2 Project Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Classes and methods implementing Spectrum Access System Release 2 Enhanced Antenna modelling """

import numpy as np


class SAS1Antenna:
    """Class implementing the Antenna Pattern calculations for SAS rel. 1
    """

    def __init__(self, hor_dirs, ant_azimuth, hor_pattern, ant_gain=0.0):
        """Constructor for a SAS1Antenna model

        :param hor_dirs: A single or list of ray directions (degrees) in the horizontal plane.
        :type hor_dirs: float
        :param ant_azimuth: Antenna azimuth (degrees)
        :type ant_azimuth: float
        :param hor_pattern: A list of the antenna horizontal pattern defined as a ndarray of
            360 values with the following conventions:
            - clockwise increments of 1 degree.
            - 0 degree corresponds to the antenna boresight.
            - values are 'gain' (and not attenuation)
        :type hor_pattern: float
        :param ant_gain: Additional antenna gain in dBi. To be used if not included in the pattern
            (i.e., when using a normalized pattern). (Default: 0)
        :type ant_gain: float, optional
        """
        self.is_scalar = np.isscalar(hor_dirs)
        self.hor_dirs = np.atleast_1d(hor_dirs)
        self.ant_azimuth = ant_azimuth
        self.hor_pattern = hor_pattern
        self.ant_gain = ant_gain
