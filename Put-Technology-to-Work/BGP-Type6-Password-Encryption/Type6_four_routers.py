# This is a small library that can be reused to bring up a 3 router Service-Provider network topology with BGP.
# TOPOLOGY: PE1-------------P1--------------P2----------PE2
#             BGP          BGP              BGP         BGP
# DATE: Mar 26, 2020

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


pe1_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh
!
hostname PE1
!
password6 encryption aes
key chain type6_password
 key 1
  accept-lifetime 01:00:00 october 24 2005 infinite
  key-string password6 606745575e6565
  send-lifetime 01:00:00 october 24 2005 infinite
  cryptographic-algorithm MD5
 !
!
interface Loopback1
 ipv4 address 10.10.10.10 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_P1
 mtu 9216
 ipv4 address 10.1.1.1 255.255.255.0
 no shutdown
 !
! 
router bgp 65537
 bgp router-id 10.10.10.10
 address-family ipv4 unicast
  network 10.1.1.0/24
  network 10.10.10.10/32
 !
 session-group bgp-type6-session
  keychain type6_password
 !
 neighbor 10.1.1.11
  remote-as 65537
  address-family ipv4 unicast
  !
 !
 neighbor 10.20.20.20/32
 !
 neighbor 10.20.20.20
  remote-as 65537
  update-source Loopback1
  address-family ipv4 unicast 
  !
"""

p1_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh
!
hostname P1
!
password6 encryption aes
key chain type6_password
 key 1
  accept-lifetime 01:00:00 october 24 2005 infinite
  key-string password6 606745575e6565
  send-lifetime 01:00:00 october 24 2005 infinite
  cryptographic-algorithm MD5
 !
!
interface Loopback1
 ipv4 address 10.20.20.20 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_PE1
 mtu 9216
 ipv4 address 10.1.1.11 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/1
 description Connected_to_P2
 mtu 9216
 ipv4 address 10.2.2.11 255.255.255.0
 no shutdown
!
router bgp 65537
 bgp router-id 10.20.20.20
 address-family ipv4 unicast
  network 10.1.1.0/24
  network 10.2.2.0/24
  network 10.20.20.20/32
 !
 session-group bgp-type6-session
  keychain type6_password
 !
 neighbor 10.1.1.1
  remote-as 65537
  address-family ipv4 unicast
  !
 !
 neighbor 10.2.2.1
  remote-as 65537
  address-family ipv4 unicast
  !
 !
 neighbor 10.10.10.10/32
 !
 neighbor 10.10.10.10
  remote-as 65537
  update-source Loopback1
  address-family ipv4 unicast
  !
 !
 neighbor 10.30.30.30/32
 !
 neighbor 10.30.30.30
  remote-as 65537
  update-source Loopback1
  address-family ipv4 unicast
  !
"""

p2_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh
!
hostname P2
!
password6 encryption aes
key chain type6_password
 key 1
  accept-lifetime 01:00:00 october 24 2005 infinite
  key-string password6 606745575e6565
  send-lifetime 01:00:00 october 24 2005 infinite
  cryptographic-algorithm MD5
 !
!
interface Loopback1
 ipv4 address 10.30.30.30 255.255.255.255
!
interface FourHundredGigE0/0/0/1
 description Connected_to_P1
 mtu 9216
 ipv4 address 10.2.2.1 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/0
 description Connected_to_pe2
 mtu 9216
 ipv4 address 10.3.3.1 255.255.255.0
 no shutdown
!
router bgp 65537
 bgp router-id 30.30.30.30
 address-family ipv4 unicast
  network 10.2.2.0/24
  network 10.3.3.0/24
  network 10.30.30.30/32
 !
 session-group bgp-type6-session
  keychain type6_password
 !
 neighbor 10.2.2.11
  remote-as 65537
  address-family ipv4 unicast
  !
 !
 neighbor 10.3.3.11
  remote-as 65537
  address-family ipv4 unicast
  !
 !
 neighbor 10.20.20.20/32
 !
 neighbor 10.20.20.20
  remote-as 65537
  update-source Loopback1
  address-family ipv4 unicast
  !
 !
 neighbor 10.40.40.40/32
 !
 neighbor 10.40.40.40
  remote-as 65537
  update-source Loopback1
  address-family ipv4 unicast
  !
"""

pe2_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh
!
hostname PE2
!
password6 encryption aes
key chain type6_password
 key 1
  accept-lifetime 01:00:00 october 24 2005 infinite
  key-string password6 606745575e6565
  send-lifetime 01:00:00 october 24 2005 infinite
  cryptographic-algorithm MD5
 !
!
interface Loopback1
 ipv4 address 10.40.40.40 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_P2
 mtu 9216
 ipv4 address 10.3.3.11 255.255.255.0
 no shutdown
! 
router bgp 65537
 bgp router-id 10.40.40.40
 address-family ipv4 unicast
  network 10.3.3.0/24
  network 10.40.40.40/32
 !
 session-group bgp-type6-session
  keychain type6_password
 !
 neighbor 10.3.3.1
  remote-as 65537
  address-family ipv4 unicast
  !
 !
 neighbor 10.30.30.30/32
 !
 neighbor 10.30.30.30
  remote-as 65537
  update-source Loopback1
  address-family ipv4 unicast 
  !
"""

cfg = { 'simulation':
         {'skip_auto_bringup': False, 
          'sim_dir': sim_dir, 
          'sim_host': 'localhost',
          'sim_rel': '/opt/cisco/vxr2/latest',
          'pyvxr_flags': {'port_file_timeout': 1200 }
         },
        'devices':
        {'rpe1': {'platform':'spitfire_f-baked',
                'xr_port_redir': [22, 830],
                'linecard_types': ['8201-sys'],
                'data_ports': ['FourH0/0/0/0', 'FourH0/0/0/1'],
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
         'rp1': {'platform':'spitfire_f-baked',
                'xr_port_redir': [22, 830],
                'linecard_types': ['8201-sys'],
                'data_ports': ['FourH0/0/0/0', 'FourH0/0/0/1'],
                'xr_config' : p1_config_str,
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
         'rp2': {'platform':'spitfire_f-baked',
                'xr_port_redir': [22, 830],
                'linecard_types': ['8201-sys'],
                'data_ports': ['FourH0/0/0/0', 'FourH0/0/0/1'],
                'xr_config' : p2_config_str,
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
         'rpe2': {'platform':'spitfire_f-baked',
                'xr_port_redir': [22, 830],
                'linecard_types': ['8201-sys'],
                'data_ports': ['FourH0/0/0/0', 'FourH0/0/0/1'],
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
               {'hub570':['rpe1.FourH0/0/0/0', 'rp1.FourH0/0/0/0'],
                'hub571':['rp1.FourH0/0/0/1', 'rp2.FourH0/0/0/1'],
                'hub572':['rp2.FourH0/0/0/0', 'rpe2.FourH0/0/0/0']}
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
    """Get a ssh command to a router in a VXR simulation.

    Keyword arguments:
    sim -- an instance of the Vxr object
    router -- the router name in the simulation
    """
    console_ports = sim.ports()
    if (is_server):
        return "ssh root@" + str(console_ports[device]['HostAgent']) + ' -p' + str(console_ports[device]['xr_redir22'])
    else:
        return "ssh cisco@" + str(console_ports[device]['HostAgent']) + ' -p' + str(console_ports[device]['xr_redir22'])
