This folder contains scripts to test the functionalities of the Emulator used in Cisco 8000 Emulator Notebooks. 

Before you begin the tests in this folder, ensure that the [image_version.py](./../../image_version.py) file is updated with the latest Emulator image-path and S1 parameters. 

Follow these steps to quickly test all the functionalities of notebooks in a docker container or AWS instance:
1) Configure proxy settings, if applicable.
2) Run this command to install and test notebooks:
  ```. /opt/cisco/notebooks/notebooks/Put-Technology-to-Work/testNotebooks/nbTest.sh```
  
  The [nbTest.sh](./nbTest.sh) script installs the necessary components and executes the [quicktest notebook](./quicktestNB.ipynb). 
  The following functionalities in Notebooks are tested, using this script:
 
    - Sim-up with 5 routers + linux server
    - Basic router configurations and routing protocols
    - TREX
    - Traffic
    - Yang models for configuring routers

  
  
