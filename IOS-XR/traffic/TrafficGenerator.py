# DESCRIPTION: This is a small library that contains functions that can be reused for a traffic generator
# PLATFORM: Emulator for CISCO 8000
# Sarah Samuel (sasamuel@cisco.com)
# DATE: 08 September 2020

import paramiko
from paramiko_expect import SSHClientInteraction
PROMPT = '.*root.*'
TREX_PROMPT = '.*trex.*'

# The below function sends bidirectional traffic. 
# TREX is in stateful mode.
def generate_bidir_traffic(trexipaddress, trexport):
    import paramiko
    from paramiko_expect import SSHClientInteraction
    PROMPT = '.*root.*'
    TREX_PROMPT = '.*trex.*'
    client = paramiko.SSHClient()
    # Set SSH key parameters to auto accept unknown hosts
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=trexipaddress, port=trexport, username='root', password='cisco123')

    # SFTP for file transfer
    transfer = client.open_sftp()
    transfer.put("./traffic/test-new.yaml", "/opt/cisco/trex/latest/cap2/test-new.yaml")
    transfer.close() 

    # Interact mode to perform the configurations for the traffic
    interact = SSHClientInteraction(client, timeout=30, display=True)
    interact.expect(PROMPT)

    interact.send('ifconfig eth1 up; ifconfig eth2 up')
    interact.expect(PROMPT)

    interact.send('cd /opt/cisco/trex/latest/cap2/; ls -lart test-new.yaml; cd /opt/cisco/trex/latest/')
    interact.expect(PROMPT)

    # Start traffic for 1 second. Change the -d value to send traffic for longer.
    interact.send('./t-rex-64 -f cap2/test-new.yaml -m 1795 -d 1')
    interact.expect('.*')
  
    interact.send('exit')
    interact.expect()

    interact.close()
    client.close()
    return

# The below function sends unidirectional high-priority traffic. 
# TREX is in stateless mode
def generate_hipriority_traffic (trexipaddress, trexport):
    import paramiko
    from paramiko_expect import SSHClientInteraction
    PROMPT = '.*root.*'
    TREX_PROMPT = '.*trex.*'
    # Connecting to the first SSH console to start the TREX server
    client1 = paramiko.SSHClient()
    # Set SSH key parameters to auto accept unknown hosts
    client1.load_system_host_keys()
    client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client1.connect(hostname=trexipaddress, port=trexport, username='root', password='cisco123')
    
    # SFTP for file transfer
    transfer = client1.open_sftp()
    transfer.put("./traffic/trex_cfg.yaml", "/etc/trex_cfg.yaml")
    transfer.put("./traffic/dscp_traffic1.py", "/opt/cisco/trex/latest/stl/dscp_traffic1.py")
    transfer.close() 
    
    # Interact mode to perform the configurations for the traffic
    interact1 = SSHClientInteraction(client1, timeout=30, display=True)
    interact1.expect(PROMPT)
    
#    interact1.send('yum -y install net-tools')
#    interact1.expect(PROMPT, timeout=500)
    
#    interact1.send('yum -y install pciutils')
#    interact1.expect(PROMPT, timeout=500)
    
    interact1.send('ifconfig eth1 10.0.0.1 netmask 255.255.255.0 up; ifconfig eth2 10.1.1.1 netmask 255.255.255.0 up')
    interact1.expect(PROMPT)

    interact1.send('cd /opt/cisco/trex/latest/')
    interact1.expect(PROMPT)
    
    interact1.send('./t-rex-64 -i')
    interact1.expect('.*wait 1 sec.*', timeout=120)
    
    # Connecting to the first SSH console to send traffic
    client2 = paramiko.SSHClient()
    # Set SSH key parameters to auto accept unknown hosts
    client2.load_system_host_keys()
    client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client2.connect(hostname=trexipaddress, port=trexport, username='root', password='cisco123')
                    
    # Interact mode to perform the configurations for the traffic
    interact2 = SSHClientInteraction(client2, timeout=100, display=True)
    interact2.expect(PROMPT)

    interact2.send('cd /opt/cisco/trex/latest/')
    interact2.expect(PROMPT)
                    
    interact2.send('./trex-console')
    interact2.expect('.*trex.*', timeout=120)
    
    interact2.send('start -f stl/dscp_traffic1.py -d 1h -m 100pps -p 0')
    interact2.expect('.*trex.*', timeout=120)
    
    return client1, client2, interact1, interact2

# The below function sends 3 streams of unidirectional traffic. 
# TREX is in stateless mode
def generate_3traffic_streams (trexipaddress, trexport):
    import paramiko
    from paramiko_expect import SSHClientInteraction
    PROMPT = '.*root.*'
    TREX_PROMPT = '.*trex.*'
    # Connecting to the first SSH console to start the TREX server
    client1 = paramiko.SSHClient()
    # Set SSH key parameters to auto accept unknown hosts
    client1.load_system_host_keys()
    client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client1.connect(hostname=trexipaddress, port=trexport, username='root', password='cisco123')
    
    # SFTP for file transfer
    transfer = client1.open_sftp()
    transfer.put("./traffic/trex_cfg.yaml", "/etc/trex_cfg.yaml")
    transfer.put("./traffic/traffic_3st.py", "/opt/cisco/trex/latest/stl/traffic_3st.py")
    transfer.close() 
    
    # Interact mode to perform the configurations for the traffic
    interact1 = SSHClientInteraction(client1, timeout=30, display=True)
    interact1.expect(PROMPT)
    
    #interact1.send('sudo yum install net-tools')
    #interact1.expect(PROMPT)
    
    #interact1.send('sudo yum install pciutils')
    #interact1.expect(PROMPT)

    interact1.send('ifconfig eth1 10.0.0.1 netmask 255.255.255.0 up; ifconfig eth2 10.1.1.1 netmask 255.255.255.0 up')
    interact1.expect(PROMPT)

    interact1.send('cd /opt/cisco/trex/latest/')
    interact1.expect(PROMPT)
    
    interact1.send('./t-rex-64 -i')
    interact1.expect('.*wait 1 sec.*', timeout=120)
    
    # Connecting to the first SSH console to send traffic
    client2 = paramiko.SSHClient()
    # Set SSH key parameters to auto accept unknown hosts
    client2.load_system_host_keys()
    client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client2.connect(hostname=trexipaddress, port=trexport, username='root', password='cisco123')
                    
    # Interact mode to perform the configurations for the traffic
    interact2 = SSHClientInteraction(client2, timeout=30, display=True)
    interact2.expect(PROMPT)

    interact2.send('cd /opt/cisco/trex/latest/')
    interact2.expect(PROMPT)
                    
    interact2.send('./trex-console')
    interact2.expect('.*trex.*', timeout=60)
    
    interact2.send('start -f stl/traffic_3st.py -d 1h -m 100pps -p 0')
    interact2.expect('.*trex.*', timeout=60)
    
    return client1, client2, interact1, interact2

# The below function stops the traffic and ends the sessions. 
# TREX is in stateless mode
def stop_traffic (client1, client2, interact1, interact2):
    interact2.send('stop -a')
    interact2.expect('.*trex.*', timeout=10)
    
    interact1.send('cd /opt/cisco/trex/latest/')
    interact1.expect(PROMPT)
    
    interact1.send('sudo ./dpdk_nic_bind.py --force -u 00:04.0')
    interact1.expect(PROMPT)
    
    interact1.send('sudo ./dpdk_nic_bind.py --force -u 00:05.0')
    interact1.expect(PROMPT)
    
    interact1.send('sudo ./dpdk_nic_bind.py --bind=virtio-pci 00:04.0')
    interact1.expect(PROMPT)
    
    interact1.send('sudo ./dpdk_nic_bind.py --bind=virtio-pci 00:05.0')
    interact1.expect(PROMPT)
    
    interact1.close()
    interact2.close()
    client1.close()
    client2.close()



    
    
    
    
                   
    

    
