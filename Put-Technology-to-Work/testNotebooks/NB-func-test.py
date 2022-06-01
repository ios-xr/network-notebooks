# DESCRIPTION: This is a small test to bring up a 5 router network topology with OSPF and MPLS and 
# traffic generators connected to either of the PE routers.
# PLATFORM: Emulator for CISCO 8000
# TOPOLOGY: TGN-------------PE1-------------P1--------------PE2--------------TGN
#                                OSPF+MPLS       OSPF+MPLS        
# AUTHOR: Sarah Samuel (sasamuel@cisco.com)
# DATE: 14 July 2021

from ncclient import manager
from ncclient.xml_ import to_ele
from lxml import etree
import time
import sys
sys.path.append("..")
from QoS.SP_tgn import *


def connect(host, port, user, password, source):
      conn = manager.connect(host=host,
                             port=port,
                             username=user,
                             password = password,
                             device_params={'name': 'iosxr'},
                             hostkey_verify=False,
                             allow_agent=False,
                             look_for_keys=False
                            )

      rpc_reply = conn.edit_config(config=telemetry)
      conn.commit()
      print(rpc_reply)


TestResult = True
sim = Vxr()
sim.no_image_copy=True
sim.clean()
print("Sim clean: Done")
print("Simulation starting. Please wait for the Sim status message. This may take 3-10 minutes.")

try:
    sim.start(cfg)
    status = sim.status()
    print("Sim status: ", status)
except Exception as err:
    print("Sim launch failed (%s)" % str(err))
    TestResult = False

print('Consoles can be reached by:')
print('P1: ', get_telnet_cmd(sim, 'rp1'), '\nPE1: ', get_telnet_cmd(sim, 'rpe1'), '\nPE2: ', get_telnet_cmd(sim, 'rpe2'), '\nCE1: ', get_telnet_cmd(sim, 'rce1'), '\nCE2: ', get_telnet_cmd(sim, 'rce2'), '\nTGN: ', get_telnet_cmd(sim, 'trex'))
print('or better:')
print('P1: ', get_ssh_cmd(sim, 'rp1'), '\nPE1: ', get_ssh_cmd(sim, 'rpe1'), '\nPE2: ', get_ssh_cmd(sim, 'rpe2'), '\nCE1: ', get_ssh_cmd(sim, 'rce1'), '\nCE2: ', get_ssh_cmd(sim, 'rce2'), '\nTGN: ', get_ssh_cmd(sim, 'trex', 'True'))
print('The password is cisco123')

ports = sim.ports()
loginpe1 = telnetlib.Telnet(str(ports['rpe1']['HostAgent']) , str(ports['rpe1']['serial0']))
loginp1 = telnetlib.Telnet(str(ports['rp1']['HostAgent']) , str(ports['rp1']['serial0']))
loginpe2 = telnetlib.Telnet(str(ports['rpe2']['HostAgent']) , str(ports['rpe2']['serial0']))
logince1 = telnetlib.Telnet(str(ports['rce1']['HostAgent']) , str(ports['rce1']['serial0']))
logince2 = telnetlib.Telnet(str(ports['rce2']['HostAgent']) , str(ports['rce2']['serial0']))
trexipaddress = str(ports['trex']['HostAgent'])
trexport = str(ports['trex']['xr_redir22'])
p1_ipaddress = str(ports['rp1']['HostAgent'])
p1_sshport = str(ports['rp1']['xr_redir22'])

print("\n*********Waiting for 40s for protocol convergence*********")
time.sleep(40)

loginp1.write(('''
show ip ospf nei
show mpls ldp interface
show mpls ldp bindings brief
show run mpls ldp
show mpls ldp neigh br
show ip route
''').encode('ascii'))
line = loginp1.read_until(b'/r/n',4)
print(line.decode())

try:
    client1, client2, interact1, interact2 = generate_hipriority_traffic (trexipaddress, trexport)
except:
    print("TREX ERROR")
    TestResult = False
else:
    print("TREX Traffic Transmission successful")

print("\n*********Waiting for 40s for traffic flow*********")
time.sleep(40)

loginpe1.write(('''
show interface FourHundredGigE0/0/0/2 acc
show interface FourHundredGigE0/0/0/1 acc
''').encode('ascii'))
line = loginpe1.read_until(b'/r/n',4)
print("***** LIVE OUTPUT FROM TELNET CONSOLE OF PE1 *****")
print(line.decode())

telemetry = '''
<config>
<telemetry-model-driven xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-telemetry-model-driven-cfg">
   <destination-groups>
    <destination-group>
     <destination-id>D1</destination-id>
     <ipv4-destinations>
      <ipv4-destination>
       <ipv4-address>10.168.122.119</ipv4-address>
       <destination-port>20030</destination-port>
       <encoding>gpb</encoding>
       <protocol>
        <protocol>grpc</protocol>
        <no-tls/>
       </protocol>
      </ipv4-destination>
     </ipv4-destinations>
    </destination-group>
   </destination-groups>
   <sensor-groups>
    <sensor-group>
     <sensor-group-identifier>SGroup1</sensor-group-identifier>
     <sensor-paths>
      <sensor-path>
       <telemetry-sensor-path>Cisco-IOS-XR-wdsysmon-fd-oper:system-monitoring/cpu-utilization</telemetry-sensor-path>
      </sensor-path>
     </sensor-paths>
    </sensor-group>
   </sensor-groups>
   <enable></enable>
   <subscriptions>
    <subscription>
     <subscription-identifier>Sub1</subscription-identifier>
     <sensor-profiles>
      <sensor-profile>
       <sensorgroupid>SGroup1</sensorgroupid>
       <sample-interval>3000</sample-interval>
      </sensor-profile>
     </sensor-profiles>
     <destination-profiles>
      <destination-profile>
       <destination-id>D1</destination-id>
      </destination-profile>
     </destination-profiles>
    </subscription>
   </subscriptions>
  </telemetry-model-driven>
 </config>
 '''
try:
    connect(p1_ipaddress, p1_sshport, 'cisco', 'cisco123', 'candidate')
except:
    print("NCCLIENT ERROR - Yang model cfg failed")
    TestResult = False
else:
    print("Yang model cfg successful")

# Show the telemetry configuration applied on the router.
loginp1.write(('''
show running-config telemetry model-driven
''').encode('ascii'))
line = loginp1.read_until(b'/r/n',2)
print("***** VIEW FROM TELNET CONSOLE OF P1 *****")
print(line.decode())

loginpe1.close()
loginpe2.close()
logince1.close()
logince2.close()
loginp1.close()
client1.close()
client2.close()

sim.stop()
sim.clean()
# Clean up sim scratch space
shutil.rmtree(sim_dir)

if (TestResult):
    print("********* NOTEBOOK TEST IS SUCCESSFUL *********")
else:
    print("********* NOTEBOOK TEST FAILED *********")
        


      

      


