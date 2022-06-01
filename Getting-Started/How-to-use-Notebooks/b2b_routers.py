# DESCRIPTION: This is a small library that can be reused to bring up a 2 routers back-to-back topology 
# PLATFORM: Emulator for CISCO 8000
# TOPOLOGY: PE1----------PE2                             
# AUTHORS: Sarah Samuel (sasamuel@cisco.com)
# DATE: 28 September 2020

from pyvxr.vxr import Vxr
from pathlib import Path

import sys
import os
import telnetlib
import logging
import shutil
import getpass
import string
import random
print(sys.version)
logging.basicConfig(level=logging.INFO)
sys.path.append("../../")
from image_version import *

# Setting up scratch space for the simulation
sim_dir = '/nobackup/' + getpass.getuser() + '/pyvxr/' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

ssh_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh
"""

pe1_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh

hostname PE1
line console
 exec-timeout 0 0
 absolute-timeout 0
 session-timeout 0
!
line default
 exec-timeout 0 0
 absolute-timeout 0
 session-timeout 0
!
interface Loopback0
 ipv4 address 10.0.0.3 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_PE2
 mtu 9216
 ipv4 address 10.11.11.1 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/1
 mtu 9216
 ipv4 address 10.22.22.1 255.255.255.0
 no shutdown
!
 """

pe2_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh

hostname PE2
line console
 exec-timeout 0 0
 absolute-timeout 0
 session-timeout 0
!
line default
 exec-timeout 0 0
 absolute-timeout 0
 session-timeout 0
!
interface Loopback0
 ipv4 address 10.0.0.9 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_PE1
 mtu 9216
 ipv4 address 10.11.11.2 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/1
 mtu 9216
 ipv4 address 10.33.33.1 255.255.255.0
 no shutdown
!
 """

cfg = { 'simulation':
         {'skip_auto_bringup': False, 
          'sim_dir': sim_dir, 
          'sim_host': 'localhost',
          'sim_rel': '/opt/cisco/vxr2/latest',
          'pyvxr_flags': {'port_file_timeout': 500 }
         },
        'devices':
        {'r1': {'platform':'spitfire_f-baked',
                 'xr_port_redir': [22, 23],
                 'linecard_types': ['8201-sys'], 
                 'data_ports': ['FourH0/0/0/0', 'FourH0/0/0/1', 'FourH0/0/0/2'],
                 'xr_username': 'cisco',
                 'xr_password': 'cisco123',
                 'xr_config' : pe1_config_str,
                 'image': sim_image_global,
                 'vxr_sim_config': {
                     'shelf': {
                       'ConfigOvxr': ConfigOvxr_global,
                       'ConfigEnableNgdp': ConfigEnableNgdp_global,
                       'ConfigS1SdkVer': ConfigS1SdkVer_global,
                       'ConfigS1NpsuiteVer': ConfigS1NpsuiteVer_global
                     }
                  }
                },
         'r2': {'platform':'spitfire_f-baked',
                 'xr_port_redir': [22, 23],
                 'linecard_types': ['8201-sys'],
                 'data_ports': ['FourH0/0/0/0', 'FourH0/0/0/1', 'FourH0/0/0/2', 'FourH0/0/0/3'],
                 'xr_username': 'cisco',
                 'xr_password': 'cisco123',
                 'xr_config' : pe2_config_str,
                 'image': sim_image_global,
                 'vxr_sim_config': {
                     'shelf': {
                       'ConfigOvxr': ConfigOvxr_global,
                       'ConfigEnableNgdp': ConfigEnableNgdp_global,
                       'ConfigS1SdkVer': ConfigS1SdkVer_global,
                       'ConfigS1NpsuiteVer': ConfigS1NpsuiteVer_global
                     }
                   }
                } 
        },
       'connections':
           {'hubs':
               {'hub570':['r1.FourH0/0/0/0', 'r2.FourH0/0/0/0']
               }
           },
      }

# Defining two little helpers for obtaining the telnet and ssh access details.

def get_telnet_cmd(sim, router):
    """Get a telnet command to a router in a VXR simulation.

    Keyword arguments:
    sim -- an instance of the Vxr object
    router -- the router name in the simulation
    """
    console_ports = sim.ports()
    return "telnet " + str(console_ports[router]['HostAgent']) + ' ' + str(console_ports[router]['serial0'])

def get_ssh_cmd(sim, device, is_server=False):
    """Get a telnet command to a router in a VXR simulation.

    Keyword arguments:
    sim -- an instance of the Vxr object
    router -- the router name in the simulation
    """
    console_ports = sim.ports()
    if (is_server):
        return "ssh root@" + str(console_ports[device]['HostAgent']) + ' -p' + str(console_ports[device]['xr_redir22'])
    else:
        return "ssh cisco@" + str(console_ports[device]['HostAgent']) + ' -p' + str(console_ports[device]['xr_redir22'])
