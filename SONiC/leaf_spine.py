# This is a small library that can be reused to bring up 2 Leaf 2 Spine network topology with Cisco 8000
# AUTHOR: Sarah Samuel (sasamuel@cisco.com)
# DATE: 10 November 2021

from pathlib import Path

import sys
import os
import telnetlib
import logging
import shutil
import getpass
import string
import random
import genie
print(sys.version)
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
from image_version import *
#from genie import testbed
from pyats.topology import loader
from paramiko_expect import SSHClientInteraction
import paramiko
from traffic.TrafficGenerator import generate_bidir_traffic

# Setting up scratch space for the simulation
sim_dir = '/nobackup/' + getpass.getuser() + '/pyvxr/' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))


        
cfg = { 'simulation':
         {'skip_auto_bringup': False,
          'no_image_copy': True,
          'sim_dir': sim_dir,
          'sim_host': 'localhost',
          'sim_rel': '/opt/cisco/vxr2/latest',
          'pyvxr_flags': {'port_file_timeout': 1200}
         },
        'devices':
         {'S0': {'platform':'spitfire_f',
                 'xr_port_redir': [22, 23],
                 'linecard_types': ['8102-64H'],
                 'os_type': 'sonic',
                 'linux_username': 'cisco',
                 'linux_password': 'cisco123',
                 'image': '/opt/cisco/images/8000/sonic/onie-recovery-x86_64-cisco_8000-r0.iso',
                 'onie-install': '/opt/cisco/images/8000/sonic/sonic-cisco-8000.bin',
                 'vxr_sim_config': {
                  'shelf': {
                    'ConfigOvxr': 'true',
                    'ConfigS1SdkVer': ConfigS1SdkVer_sonic,
                    'ConfigS1NpsuiteVer': ConfigS1NpsuiteVer_sonic
                  }
                 }
                },
          'S1': {'platform':'spitfire_f',
                 'xr_port_redir': [22, 23],
                 'linecard_types': ['8102-64H'],
                 'os_type': 'sonic',
                 'linux_username': 'cisco',
                 'linux_password': 'cisco123',
                 'image': '/opt/cisco/images/8000/sonic/onie-recovery-x86_64-cisco_8000-r0.iso',
                 'onie-install': '/opt/cisco/images/8000/sonic/sonic-cisco-8000.bin',
                 'vxr_sim_config': {
                  'shelf': {
                   'ConfigOvxr': 'true',
                   'ConfigS1SdkVer': ConfigS1SdkVer_sonic,
                   'ConfigS1NpsuiteVer': ConfigS1NpsuiteVer_sonic
                  }
                 }
                },
          'L0': {'platform':'spitfire_f',
                 'xr_port_redir': [22, 23],
                 'linecard_types': ['8101-32H'],
                 'os_type': 'sonic',
                 'linux_username': 'cisco',
                 'linux_password': 'cisco123',
                 'image': '/opt/cisco/images/8000/sonic/onie-recovery-x86_64-cisco_8000-r0.iso',
                 'onie-install': '/opt/cisco/images/8000/sonic/sonic-cisco-8000.bin',
                 'vxr_sim_config': {
                  'shelf': {
                   'ConfigOvxr': 'true',
                   'ConfigS1SdkVer': ConfigS1SdkVer_sonic,
                   'ConfigS1NpsuiteVer': ConfigS1NpsuiteVer_sonic
                  }
                 }
                },
          'L1': {'platform':'spitfire_f',
                 'xr_port_redir': [22, 23],
                 'linecard_types': ['8101-32H'],
                 'os_type': 'sonic',
                 'linux_username': 'cisco',
                 'linux_password': 'cisco123',
                 'image': '/opt/cisco/images/8000/sonic/onie-recovery-x86_64-cisco_8000-r0.iso',
                 'onie-install': '/opt/cisco/images/8000/sonic/sonic-cisco-8000.bin',
                 'vxr_sim_config': {
                  'shelf': {
                   'ConfigOvxr': 'true',
                   'ConfigS1SdkVer': ConfigS1SdkVer_sonic,
                   'ConfigS1NpsuiteVer': ConfigS1NpsuiteVer_sonic
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
           {'S0_L0_conn1':['S0.Ethernet0', 'L0.Ethernet0'],
            'S0_L0_conn2':['S0.Ethernet2', 'L0.Ethernet3'],
            'S0_L1_conn1':['S0.Ethernet1', 'L1.Ethernet0'],
            'S0_L1_conn2':['S0.Ethernet3', 'L1.Ethernet3'],
            'S1_L0_conn1':['S1.Ethernet0', 'L0.Ethernet1'],
            'S1_L0_conn2':['S1.Ethernet2', 'L0.Ethernet4'],
            'S1_L1_conn1':['S1.Ethernet1', 'L1.Ethernet1'],
            'S1_L1_conn2':['S1.Ethernet3', 'L1.Ethernet4'],
            'L0_trex':['L0.Ethernet2', 'trex.eth1'],
            'L1_trex':['L1.Ethernet2', 'trex.eth2']
           }
          }
       }


#Function definitions

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
