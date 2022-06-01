# This is a small library that can be reused to bring up a 4 router Service-Provider network topology with OSPF and MPLS.
# TOPOLOGY: PE1-------------P1--------------P3--------------PE3
#               OSPF+MPLS       OSPF+MPLS        OSPF+MPLS   
# AUTHOR: Annapoorani
# DATE: 5 November 2019

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
key chain ISIS-KEY
 key 1
  accept-lifetime 00:00:00 january 01 2018 infinite
  key-string password 121A0C041104
  send-lifetime 00:00:00 january 01 2018 infinite
  cryptographic-algorithm HMAC-MD5
 !
!
interface Loopback0
 ipv4 address 209.165.200.225 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_P3
 mtu 9216
 ipv4 address 198.51.100.1 255.255.255.0
 ipv4 unreachables disable
 load-interval 30
 damp
 !
 carrier-delay up 150000 down 0
 load-interval 30
 no shutdown
!
interface FourHundredGigE0/0/0/1
 !
 carrier-delay up 150000 down 0
 load-interval 30
 no shutdown
 !
 router isis CORE
 net 49.0001.0100.0000.0005.00
 nsr
 nsf cisco
 log adjacency changes
 lsp-gen-interval maximum-wait 5000 initial-wait 50 secondary-wait 200
 lsp-refresh-interval 65000
 max-lsp-lifetime 65535
 lsp-password keychain ISIS-KEY
 lsp-password keychain ISIS-KEY level 2
 address-family ipv4 unicast
  metric-style wide
  spf-interval maximum-wait 5000 initial-wait 50 secondary-wait 200
  spf prefix-priority critical tag 5000
  spf prefix-priority high tag 1000
 !
!
mpls oam
!
mpls ldp
 router-id 209.165.200.225
 interface FourHundredGigE0/0/0/0
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
key chain ISIS-KEY
 key 1
  accept-lifetime 00:00:00 january 01 2018 infinite
  key-string password 110A1016141D
  send-lifetime 00:00:00 january 01 2018 infinite
  cryptographic-algorithm HMAC-MD5
 !
!
interface FourHundredGigE0/0/0/0
 description Connected_to_P1
 mtu 9216
 ipv4 address 198.51.100.2 255.255.255.0
 ipv4 unreachables disable
 load-interval 30
 dampening
 !
 carrier-delay up 150000 down 0
 load-interval 30
 no shutdown
!
interface FourHundredGigE0/0/0/1
ipv4 address 198.51.100.3 255.255.255.0
!
router isis CORE
 is-type level-2-only
 net 49.0001.0100.0000.0007.00
 nsr
 nsf cisco
 log adjacency changes
 lsp-gen-interval maximum-wait 5000 initial-wait 50 secondary-wait 200
 lsp-refresh-interval 65000
 max-lsp-lifetime 65535
 lsp-password keychain ISIS-KEY
 lsp-password keychain ISIS-KEY level 2
 address-family ipv4 unicast
  metric-style wide
  spf-interval maximum-wait 5000 initial-wait 50 secondary-wait 200
  spf prefix-priority critical tag 5000
  spf prefix-priority high tag 1000
 !
!
mpls oam
!
mpls ldp
 router-id 209.165.200.225
 interface FourHundredGigE0/0/0/0
 !
!
multicast-routing
 address-family ipv4
  interface all enable
 !
!
"""
        
cfg = { 'simulation':
         {'skip_auto_bringup': False, 
          'sim_dir': sim_dir,
          'sim_host': 'localhost',
          'sim_rel': '/opt/cisco/vxr2/latest',
          'pyvxr_flags': {'port_file_timeout': 1200}
         },
        'devices':
         {'r1': {'platform':'spitfire_f-baked',
                 'xr_port_redir': [22, 23, 830],
                 'linecard_types': ['8201-sys'],
                 'data_ports': ['FourH0/0/0/0', 'FourH0/0/0/1', 'FourH0/0/0/2'],
                 'xr_username': 'cisco',
                 'xr_password': 'cisco123',
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
          'r2': {'platform':'spitfire_f-baked',
                 'xr_port_redir': [22, 23, 830],
                 'linecard_types': ['8201-sys'],
                 'data_ports': ['FourH0/0/0/0', 'FourH0/0/0/1', 'FourH0/0/0/2', 'FourH0/0/0/3'],
                 'xr_username': 'cisco',
                 'xr_password': 'cisco123',
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
                } 
          },
         'connections':
          {'hubs':
           {'hub570':['r1.FourH0/0/0/0', 'r2.FourH0/0/0/0']}
          }
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
