# Traffic Utilities

For a realistic portrayal of networking features, IP traffic through the routers on the network is essential. Traffic generators are used to inject traffic into lab networks. The python functions to utilize the software traffic generator, TREX, in the simulated networks is available in this python file - [TrafficGenerator.py](./TrafficGenerator.py).

## Steps to incorporate the TREX traffic generator in a network notebook:

1. The following functions are available in the TrafficGenerator.py python file
- generate_bidir_traffic: This function sends a burst of bidirectional traffic for 1 sec across the simulated network.
- generate_hipriority_traffic: This function sends unidirectional high priority traffic across the simulated network.
- generate_3traffic_streams: This function sends 3 streams of unidirectional traffic across the simulated network.
Depending on your requirement, choose the appropriate traffic generator function.

2. Include the below 2 lines at the top of your notebook or within the python file used in your notebook. Use the function that you have decided in step 1.

```
sys.path.append("..")
from trafficUtils.TrafficGenerator import generate_3traffic_streams
```

3. Include the server for the traffic generator in the **cfg** variable of your notebook like below:

```
         'trex': {'platform':'linux',
                  'xr_port_redir': [21, 22, 23, 50, 53, 80],
                  'vcpu': 8,
                  'memory': '5GB',
                  'data_ports': ['eth1', 'eth2'],
                  'image': '/opt/cisco/images/linux/centos7_serial.qcow2'
                 }
        },
```
      
4. After bringing up the VXR network and obtaining the ssh ip address and port of the server, invoke the traffic generator function as shown below to start the traffic:

```
!pip install paramiko
!pip install paramiko-expect
client1, client2, interact1, interact2 = generate_traffic_streams(serveripaddress, serverport)
```
