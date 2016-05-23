#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2015 Jakob Luettgau
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


class FileManager(object):
    """Manages the files that exist in the system."""

    def __init__(self, simulation=None):
        print('FileManager instance.')
        
        self.simulation = simulation

        self.files = {}

#        self.files = {
#                'abc': {'tape':'t1',  'size': 123, 'pos': 40},    
#                'xyz': {'tape':'t1',  'size': 123, 'pos': 140},    
#                'f1':  {'tape':'t1',  'size': 123, 'pos': 200},    
#                'f2':  {'tape':'t10', 'size': 123, 'pos': 0},    
#                'f3':  {'tape':'t20', 'size': 123, 'pos': 0},  
#
#'0_ten/2084/208404_scout_SMO.tar': {'pos': 0, 'requests': 'r', 'tape': '14469', 'size': 8857600},
#'_ten/2084/208404_tr_sulphur.tar': {'pos': 0, 'requests': 'r', 'tape': '18418', 'size': 1493463040},
#'00_ten/2084/208404_mecca_gp.tar': {'pos': 0, 'requests': 'r', 'tape': '66180', 'size': 214712320},
#'ten/2084/208404_scout_ST109.tar': {'pos': 0, 'requests': 'r', 'tape': '23777', 'size': 3153920},
#'1/TS2100_ten/2084/208404_mm.tar': {'pos': 0, 'requests': 'r', 'tape': '37850', 'size': 141762560},
#'2100_ten/2084/208404_tropop.tar': {'pos': 0, 'requests': 'r', 'tape': '57408', 'size': 684216320},
#'0_ten/2084/208404_scout_Ala.tar': {'pos': 0, 'requests': 'r', 'tape': '55467', 'size': 3153920},
#'0_ten/2084/208404_import_ts.tar': {'pos': 0, 'requests': 'r', 'tape': '17389', 'size': 1054720},
#'_ten/2084/208404_tr_O3_tbud.tar': {'pos': 0, 'requests': 'r', 'tape': '25371', 'size': 1710520320},
#'n/2084/208404_lnox_Grewe_gp.tar': {'pos': 0, 'requests': 'r', 'tape': '42622', 'size': 450641920},
#'1/TS2100_ten/2084/208404_sp.tar': {'pos': 0, 'requests': 'r', 'tape': '57179', 'size': 336640000},
#'ten/2084/208404_scout_ST323.tar': {'pos': 0, 'requests': 'r', 'tape': '03796', 'size': 3153920},
#'0_ten/2084/208404_scout_Kua.tar': {'pos': 0, 'requests': 'r', 'tape': '20200', 'size': 3153920},
#'ten/2084/208404_scout_ST187.tar': {'pos': 0, 'requests': 'r', 'tape': '22188', 'size': 3153920},
#'/TS2100_ten/2084/208404_rad.tar': {'pos': 0, 'requests': 'r', 'tape': '09162', 'size': 14172160},
#'ten/2084/208404_scout_SCBAH.tar': {'pos': 0, 'requests': 'r', 'tape': '21624', 'size': 6789120},
#'0_ten/2084/208404_tr_O3_bud.tar': {'pos': 0, 'requests': 'r', 'tape': '69439', 'size': 2130472960},
#'0_ten/2084/208404_tr_transp.tar': {'pos': 0, 'requests': 'r', 'tape': '08801', 'size': 1918136320},
#'/TS2100_ten/2084/208404_qbo.tar': {'pos': 0, 'requests': 'r', 'tape': '47746', 'size': 639385600},
#'0_ten/2084/208404_tr_family.tar': {'pos': 0, 'requests': 'r', 'tape': '23346', 'size': 644106240},
#'0_ten/2084/208404_scout_MLO.tar': {'pos': 0, 'requests': 'r', 'tape': '13230', 'size': 8857600},
#'en/2084/208404_rad02_fubrad.tar': {'pos': 0, 'requests': 'r', 'tape': '36898', 'size': 1288192000},
#'ten/2084/208404_scout_ST067.tar': {'pos': 0, 'requests': 'r', 'tape': '01338', 'size': 6789120},
#'0_ten/2084/208404_tnudge_gp.tar': {'pos': 0, 'requests': 'r', 'tape': '15028', 'size': 464803840},
#'0_ten/2084/208404_scout_Reu.tar': {'pos': 0, 'requests': 'r', 'tape': '19524', 'size': 3153920},
#'27/remo/2050/e050027t205009.tar': {'pos': 0, 'requests': 'r', 'tape': '20655', 'size': 6055905280},
#'S2100_ten/2084/208404_cloud.tar': {'pos': 0, 'requests': 'r', 'tape': '09511', 'size': 2975088640},
#'2100_ten/2084/208404_qtimer.tar': {'pos': 0, 'requests': 'r', 'tape': '30767', 'size': 14643200},
#'ten/2084/208404_scout_ST014.tar': {'pos': 0, 'requests': 'r', 'tape': '15930', 'size': 3153920},
#'0_ten/2084/208404_airsea_gp.tar': {'pos': 0, 'requests': 'r', 'tape': '41515', 'size': 16527360},
#'/2084/208404_tracer_pdef_gp.tar': {'pos': 0, 'requests': 'r', 'tape': '24132', 'size': 1054720},
#'2100_ten/2084/208404_o3orig.tar': {'pos': 0, 'requests': 'r', 'tape': '67673', 'size': 1278750720},
#'0_ten/2084/208404_scout_Mal.tar': {'pos': 0, 'requests': 'r', 'tape': '50953', 'size': 3153920},
#'0_ten/2084/208404_scout_Wat.tar': {'pos': 0, 'requests': 'r', 'tape': '47383', 'size': 3153920},
#'S2100_ten/2084/208404_orbit.tar': {'pos': 0, 'requests': 'r', 'tape': '46436', 'size': 16537600},
#'0_ten/2084/208404_scout_CGO.tar': {'pos': 0, 'requests': 'r', 'tape': '43113', 'size': 8857600},
#'0_ten/2084/208404_scout_ALT.tar': {'pos': 0, 'requests': 'r', 'tape': '16326', 'size': 8857600},
#'100_ten/2084/208404_tr_alks.tar': {'pos': 0, 'requests': 'r', 'tape': '62688', 'size': 2130472960},
#'0_ten/2084/208404_scout_Pap.tar': {'pos': 0, 'requests': 'r', 'tape': '51004', 'size': 3153920},
#'100_ten/2084/208404_convect.tar': {'pos': 0, 'requests': 'r', 'tape': '65365', 'size': 4699740160},
#'100_ten/2084/208404_ddep_gp.tar': {'pos': 0, 'requests': 'r', 'tape': '14281', 'size': 528527360},
#'S2100_ten/2084/208404_gwave.tar': {'pos': 0, 'requests': 'r', 'tape': '38986', 'size': 2481213440},
#'TS2100_ten/2084/208404_scav.tar': {'pos': 0, 'requests': 'r', 'tape': '34624', 'size': 214712320},
#'_ten/2084/208404_tr_aerosol.tar': {'pos': 0, 'requests': 'r', 'tape': '22130', 'size': 1068779520},
#'en/2084/208404_rad01_fubrad.tar': {'pos': 0, 'requests': 'r', 'tape': '37729', 'size': 1288192000},
#'27/remo/2050/e050027e205009.tar': {'pos': 0, 'requests': 'rr', 'tape': '04792', 'size': 10737418240},
#'0_ten/2084/208404_tr_o3orig.tar': {'pos': 0, 'requests': 'r', 'tape': '50822', 'size': 3404503040},
#'0_ten/2084/208404_scout_Asc.tar': {'pos': 0, 'requests': 'r', 'tape': '05479', 'size': 3153920},
#'0_ten/2084/208404_scout_BRW.tar': {'pos': 0, 'requests': 'r', 'tape': '40475', 'size': 8857600},
#'100_ten/2084/208404_sedi_gp.tar': {'pos': 0, 'requests': 'r', 'tape': '15728', 'size': 460083200},
#
#
#        }

        pass

    def lookup(self, name):
        """Checks if file exists"""
        if name in self.files:
            return self.files[name]
        else:
            return False

    def update(self, name, tape=None, size=None, pos=0):
        # create entry if not existent
        if not (name in self.files):
            self.files[name] = {}
        
        # set fields idividually
        if tape != None:
            self.files[name]['tape'] = tape

        if size != None:
            self.files[name]['size'] = size

        self.files[name]['pos'] = pos

        return self.files[name]


    def dump(self):
        """Make snapshot of the file system state."""
        print("\nDump", self, "state.")
        print(self.files)
        print(self.simulation.persistency.path)
        

