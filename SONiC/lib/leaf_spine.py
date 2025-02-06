# Python library for 2 Leaf 2 Spine 3-Stage Clos topology with Cisco 8000 variants 8102-64H and 8101-32H
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
import time
print(sys.version)
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
from lib.image_version import *
#from genie import testbed
from pyats.topology import loader
from paramiko_expect import SSHClientInteraction
import paramiko
from traffic.TrafficGenerator import generate_bidir_traffic
    
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
