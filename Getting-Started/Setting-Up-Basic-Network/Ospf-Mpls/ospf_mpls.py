# This is a small library that can be reused to bring up a 4 router Service-Provider network topology with OSPF and MPLS.
# TOPOLOGY: PE1-------------P1--------------P3--------------PE3
#               OSPF+MPLS       OSPF+MPLS        OSPF+MPLS   
# AUTHOR: Sarah Samuel (sasamuel@cisco.com)
# DATE: 5 November 2019

from pathlib import Path
from pyvxr.vxr import Vxr
import sys
import os
import logging
import telnetlib
import shutil
import getpass
import string
import random
print(sys.version)
logging.basicConfig(level=logging.INFO)
sys.path.append("../../../")
from image_version import *

# Setting the scratch space for the simulation
sim_dir = '/nobackup/' + getpass.getuser() + '/pyvxr/' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))


ssh_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh
"""

p1_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh

hostname P1
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
 
ipv4 unnumbered mpls traffic-eng Loopback0
!
interface Loopback0
 ipv4 address 10.0.0.5 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_P3
 mtu 9216
 ipv4 address 10.5.7.1 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/1
 description Connected_to_PE1
 mtu 9216
 ipv4 address 10.20.7.1 255.255.255.0
 no shutdown
 !
router ospf 10
 router-id 10.0.0.5
 area 0
  interface FourHundredGigE0/0/0/0
  interface FourHundredGigE0/0/0/1
  interface Loopback0
  !
 !
!
mpls oam
!
mpls ldp
 router-id 10.0.0.5
 interface FourHundredGigE0/0/0/0
 interface FourHundredGigE0/0/0/1
 !
!
multicast-routing
 address-family ipv4
  interface all enable
 !
 """

p3_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh

hostname P3
!
ipv4 unnumbered mpls traffic-eng Loopback0
!
interface Loopback0
 ipv4 address 10.0.0.7 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_P1
 mtu 9216
 ipv4 address 10.5.7.2 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/1
 description Connected_to_PE3
 mtu 9216
 ipv4 address 10.21.7.1 255.255.255.0
 no shutdown
!
router ospf 10
 router-id 10.0.0.7
 area 0
  interface FourHundredGigE0/0/0/0
  interface FourHundredGigE0/0/0/1
  interface Loopback0
  !
 !
!
mpls oam
!
mpls ldp
 router-id 10.0.0.7
 interface FourHundredGigE0/0/0/0
 interface FourHundredGigE0/0/0/1
 !
!
multicast-routing
 address-family ipv4
  interface all enable
 !
!
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
 
ipv4 unnumbered mpls traffic-eng Loopback0
!
interface Loopback0
 ipv4 address 10.0.0.3 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 no shutdown
!
interface FourHundredGigE0/0/0/1
 description Connected_to_P1
 mtu 9216
 ipv4 address 10.20.7.2 255.255.255.0
 no shutdown
 !
router ospf 10
 router-id 10.0.0.3
 area 0
  interface FourHundredGigE0/0/0/0
  interface FourHundredGigE0/0/0/1
  interface Loopback0
  !
 !
!
mpls oam
!
mpls ldp
 router-id 10.0.0.3
 interface FourHundredGigE0/0/0/0
 interface FourHundredGigE0/0/0/1
 !
!
multicast-routing
 address-family ipv4
  interface all enable
 !
 """

pe3_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh

hostname PE3
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
 
ipv4 unnumbered mpls traffic-eng Loopback0
!
interface Loopback0
 ipv4 address 10.0.0.9 255.255.255.255
!
interface HundredGigE0/0/0/0
 no shutdown
!
interface FourHundredGigE0/0/0/1
 description Connected_to_P3
 mtu 9216
 ipv4 address 10.21.7.2 255.255.255.0
 no shutdown
 !
router ospf 10
 router-id 10.0.0.9
 area 0
  interface FourHundredGigE0/0/0/0
  interface FourHundredGigE0/0/0/1
  interface Loopback0
  !
 !
!
mpls oam
!
mpls ldp
 router-id 10.0.0.9
 interface FourHundredGigE0/0/0/0
 interface FourHundredGigE0/0/0/1
 !
!
multicast-routing
 address-family ipv4
  interface all enable
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
        {'rp1': {'platform':'spitfire_f-baked',
                'xr_port_redir': [22, 161, 830],
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
         'p3': {'platform':'spitfire_f-baked',
                'xr_port_redir': [22, 161, 830],
                'linecard_types': ['8201-sys'], 
                'data_ports': ['FourH0/0/0/0', 'FourH0/0/0/1'],
                'xr_config' : p3_config_str,
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
         'pe1': {'platform':'spitfire_f-baked',
                'xr_port_redir': [22, 161, 830],
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
         'pe3': {'platform':'spitfire_f-baked',
                'xr_port_redir': [22, 161, 830],
                'linecard_types': ['8201-sys'],  
                'data_ports': ['FourH0/0/0/0', 'FourH0/0/0/1'],
                'xr_config' : pe3_config_str,
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
         'ser1': {'platform':'linux'},
        },
       'connections':
           {'hubs':
               {'hub570':['p1.FourH0/0/0/0', 'p3.FourH0/0/0/0'],
               'hub571':['pe1.FourH0/0/0/1', 'p1.FourH0/0/0/1'],
               'hub572':['pe3.FourH0/0/0/1', 'p3.FourH0/0/0/1']}
           },
      }


# Defining two little helpers to make easy to cut and paste commands.

def get_telnet_cmd(sim, router):
    """Get a telnet command to a router in a VXR simulation.
    Keyword arguments:
    sim -- an instance of the Vxr object
    router -- the router name in the simulation
    """
    console_ports = sim.ports()
    return "telnet " + str(console_ports[router]['HostAgent']) + ' ' + str(console_ports[router]['serial0'])

def get_ssh_cmd(sim, device, is_server=False):
    """Get a telnet command to a router in a VXR simulation
    Keyword arguments:
    sim -- an instance of the Vxr object
    router -- the router name in the simulation
    """
    console_ports = sim.ports()
    if (is_server):
        return "ssh root@" + str(console_ports[device]['HostAgent']) + ' -p' + str(console_ports[device]['xr_redir22'])
    else:
        return "ssh cisco@" + str(console_ports[device]['HostAgent']) + ' -p' + str(console_ports[device]['xr_redir22'])
