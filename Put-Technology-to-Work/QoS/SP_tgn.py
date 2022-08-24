# DESCRIPTION: This is a small library that can be reused to bring up a 4 router Service-Provider network topology with OSPF and MPLS and 
# traffic generators connected to either of the PE routers.
# PLATFORM: Emulator for CISCO 8000
# TOPOLOGY: TGN--------PE1--------P1----------P2---------PE2---------TGN
#                         OSPF+MPLS  OSPF+MPLS  OSPF+MPLS  
# AUTHOR: Sarah Samuel (sasamuel@cisco.com)
# DATE: 1 April 2020

from pyvxr.vxr import Vxr
from pathlib import Path
from paramiko_expect import SSHClientInteraction
import paramiko
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
sys.path.append("..")
from trafficUtils.TrafficGenerator import generate_hipriority_traffic
from trafficUtils.TrafficGenerator import get_ssh_cmd_server

# Setting up scratch space for the simulation
sim_dir = '/nobackup/' + getpass.getuser() + '/pyvxr/' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))


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
interface Loopback0
 ipv4 address 209.165.200.225 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_PE1
 mtu 9216
 ipv4 address 198.51.100.1 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/1
 description Connected_to_P2
 mtu 9216
 ipv4 address 192.0.2.1 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/2
 description Connected_to_TREX_eth4
 mtu 9216
 ipv4 address 10.8.8.2 255.255.255.0
 no shutdown
!
router ospf 10
 router-id 209.165.200.225
 area 0
  interface FourHundredGigE0/0/0/0
  interface FourHundredGigE0/0/0/1
  interface Loopback0
  !
 !
!
mpls ldp
 router-id 209.165.200.225
 interface FourHundredGigE0/0/0/1
 interface FourHundredGigE0/0/0/0
 !
!
 """
p2_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh

hostname P2
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
 ipv4 address 209.165.200.226 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_P1
 mtu 9216
 ipv4 address 192.0.2.2 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/1
 description Connected_to_PE2
 mtu 9216
 ipv4 address 203.0.113.1 255.255.255.0
 no shutdown
!
router ospf 10
 router-id 209.165.200.226
 area 0
  interface FourHundredGigE0/0/0/0
  interface FourHundredGigE0/0/0/1
  interface Loopback0
  !
 !
!
mpls ldp
 router-id 209.165.200.226
 interface FourHundredGigE0/0/0/1
 interface FourHundredGigE0/0/0/0
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
interface Loopback0
 ipv4 address 209.165.200.227 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_TREX
 mtu 9216
 ipv4 address 10.0.0.2 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/1
 description Connected_to_P1
 mtu 9216
 ipv4 address 198.51.100.2 255.255.255.0
 no shutdown
!
router ospf 10
 router-id 209.165.200.227
 area 0
  interface FourHundredGigE0/0/0/0
  interface FourHundredGigE0/0/0/1
  interface FourHundredGigE0/0/0/2
  interface Loopback0
  !
 !
!
mpls ldp
 router-id 209.165.200.227
 interface FourHundredGigE0/0/0/0
 interface FourHundredGigE0/0/0/1
 interface FourHundredGigE0/0/0/2
 !
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
 ipv4 address 209.165.200.228 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_P2
 mtu 9216
 ipv4 address 203.0.113.2 255.255.255.0
 no shutdown
 !
interface FourHundredGigE0/0/0/1
 description Connected_to_TREX_eth2
 mtu 9216
 ipv4 address 10.1.1.2 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/2
 description Connected_to_TREX_eth3
 mtu 9216
 ipv4 address 10.9.9.1 255.255.255.0
 no shutdown
!
router ospf 10
 router-id 209.165.200.228
 area 0
  interface FourHundredGigE0/0/0/0
  interface FourHundredGigE0/0/0/1
  interface FourHundredGigE0/0/0/2
  interface Loopback0
  !
 !
!
mpls ldp
 router-id 209.165.200.228
 interface FourHundredGigE0/0/0/0
 interface FourHundredGigE0/0/0/1
 interface FourHundredGigE0/0/0/2
 !
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
                'xr_port_redir': [22, 830],
                'linecard_types': ['8201-sys'], 
                'data_ports': ['FourH0/0/0/0', 'FourH0/0/0/1', 'FourH0/0/0/2'],
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
         'rpe1': {'platform':'spitfire_f-baked',
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
         'rpe2': {'platform':'spitfire_f-baked',
                'xr_port_redir': [22, 830],
                'linecard_types': ['8201-sys'],  
                'data_ports': ['FourH0/0/0/0', 'FourH0/0/0/1', 'FourH0/0/0/2'],
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
                },
         'trex': {'platform':'linux',
                  'xr_port_redir': [21, 22, 23, 50, 53, 80],
                  'vcpu': 8,
                  'memory': '5GB',
                  'data_ports': ['eth1', 'eth2', 'eth3', 'eth4'],
                  'image': '/opt/cisco/images/linux/centos7_serial.qcow2'
                 }
        },
       'connections':
           {'hubs':
               {'hub570':['rpe1.FourH0/0/0/1', 'rp1.FourH0/0/0/0'],
               'hub571':['rp1.FourH0/0/0/1', 'rp2.FourH0/0/0/0'],
               'hub572':['rp2.FourH0/0/0/1', 'rpe2.FourH0/0/0/0'],
               'hub573':['trex.eth1', 'rpe1.FourH0/0/0/0'],
               'hub574':['trex.eth2', 'rpe2.FourH0/0/0/1'],
               'hub575':['trex.eth3', 'rpe2.FourH0/0/0/2'],
               'hub576':['trex.eth4', 'rp1.FourH0/0/0/2'] 
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

