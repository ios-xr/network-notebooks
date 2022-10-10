# DESCRIPTION: This is a small library that contains imports functions that can be reused across the IOS XR notebooks in the DevNet Sandbox
# PLATFORM: Emulator for CISCO 8000
# Sarah Samuel (sasamuel@cisco.com)
# DATE: 21 September 2022

from pathlib import Path

import sys
import os
import logging
import shutil
import getpass
import string
import random
print(sys.version)
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
from pyats.topology import loader
from paramiko_expect import SSHClientInteraction
import paramiko
from traffic.TrafficGenerator import generate_bidir_traffic
from traffic.TrafficGenerator import generate_hipriority_traffic
    
pe1_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh
!
hostname PE1
!
interface Loopback0
 ipv4 address 10.100.100.101 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_TREX_eth1
 mtu 9216
 ipv4 address 10.0.0.2 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/1
 description Connected_to_P1
 mtu 9216
 ipv4 address 10.120.2.1 255.255.255.0
 ipv4 unreachables disable
 load-interval 30
 damp
 !
 carrier-delay up 150000 down 0
 load-interval 30
 no shutdown
!
router ospf 10
 router-id 10.100.100.101
 area 0
  interface FourHundredGigE0/0/0/0
  interface FourHundredGigE0/0/0/1
  interface Loopback0
  !
 !
!
mpls ldp
 router-id 10.100.100.101
 interface FourHundredGigE0/0/0/0
 interface FourHundredGigE0/0/0/1
 !
!
 """

p1_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh
!
hostname P1
!
interface Loopback0
 ipv4 address 10.200.200.201 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_PE1
 mtu 9216
 ipv4 address 10.120.2.2 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/1
 description Connected_to_P2
 mtu 9216
 ipv4 address 10.120.3.1 255.255.255.0
 ipv4 unreachables disable
 load-interval 30
 damp
 !
 carrier-delay up 150000 down 0
 load-interval 30
 no shutdown
!
router ospf 10
 router-id 10.200.200.201
 area 0
  interface FourHundredGigE0/0/0/0
  interface FourHundredGigE0/0/0/1
  interface Loopback0
  !
 !
!
mpls ldp
 router-id 10.200.200.201
 interface FourHundredGigE0/0/0/0
 interface FourHundredGigE0/0/0/1
 !
!
 """

p2_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh
!
hostname P2
!
interface Loopback0
 ipv4 address 10.200.200.202 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_P1
 mtu 9216
 ipv4 address 10.120.3.2 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/1
 description Connected_to_PE2
 mtu 9216
 ipv4 address 10.120.4.1 255.255.255.0
 ipv4 unreachables disable
 load-interval 30
 damp
 !
 carrier-delay up 150000 down 0
 load-interval 30
 no shutdown
!
router ospf 10
 router-id 10.200.200.202
 area 0
  interface FourHundredGigE0/0/0/0
  interface FourHundredGigE0/0/0/1
  interface Loopback0
  !
 !
!
mpls ldp
 router-id 10.200.200.202
 interface FourHundredGigE0/0/0/0
 interface FourHundredGigE0/0/0/1
 !
!
 """

pe2_config_str = """
ssh server v2
ssh server netconf
netconf-yang agent ssh
!
hostname PE2
!
interface Loopback0
 ipv4 address 10.100.100.102 255.255.255.255
!
interface FourHundredGigE0/0/0/0
 description Connected_to_P2
 mtu 9216
 ipv4 address 10.120.4.2 255.255.255.0
 no shutdown
!
interface FourHundredGigE0/0/0/1
 description Connected_to_TREX_eth2
 mtu 9216
 ipv4 address 10.1.1.2 255.255.255.0
 ipv4 unreachables disable
 load-interval 30
 dampening
 !
 carrier-delay up 150000 down 0
 load-interval 30
 no shutdown
!
router ospf 10
 router-id 10.100.100.102
 area 0
  interface FourHundredGigE0/0/0/0
  interface FourHundredGigE0/0/0/1
  interface Loopback0
  !
 !
!
mpls ldp
 router-id 10.100.100.102
 interface FourHundredGigE0/0/0/0
 interface FourHundredGigE0/0/0/1
 !
!
"""

# To remove base configs, use the below string
unconfig_str = """
no interface Loopback0
!
no interface FourHundredGigE0/0/0/0
!
no interface FourHundredGigE0/0/0/1
!
no router ospf 10
!
no mpls ldp
!
 """
    
def access_device_consoles(yaml_file, nodes):
    import yaml
    
    tb = loader.load(yaml_file)
    print("\n*** Logging into the devices ***")
    for n in nodes:
       console = tb.devices[n]
       out = console.connect(learn_os=True, learn_hostname=True, prompt_recovery=True)
       nodes[n] = console
    return tb


def copy_file_to_rtr(rtr_ip, rtr_port, src_file, dst_on_rtr):
    client = paramiko.SSHClient()
    # Set SSH key parameters to auto accept unknown hosts
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rtr_ip, port=rtr_port, username='cisco', password='cisco123', allow_agent=False, look_for_keys=False)
    transfer = client.open_sftp()
    transfer.put(src_file, dst_on_rtr)
    transfer.close()
    client.close()
    return

def save_cfg_locally(rtr_ip, rtr_port, loc):
    client = paramiko.SSHClient()
    # Set SSH key parameters to auto accept unknown hosts
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rtr_ip, port=rtr_port, username='cisco', password='cisco123', allow_agent=False, look_for_keys=False)
    transfer = client.open_sftp()
    transfer.get("/etc/sonic/config_db.json", loc)
    transfer.close()
    client.close()
    print ("File copied:", loc)
    return
