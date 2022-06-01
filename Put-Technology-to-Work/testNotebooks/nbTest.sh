#!/bin/bash
PYVXR_OVXR_FILE_PATH=/opt/cisco/pyvxr/pyvxr-ovxr.tar.gz
NOTEBOOKS_DIR=/opt/cisco/notebooks/notebooks
CONDA_DIR="${HOME}/miniconda3"
miniCondaInstallLink="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
testCommand="wget -q --timeout 10 --spider ${miniCondaInstallLink} -O /dev/null"

echo "Checking internet connectivity..."
if  ${testCommand};
then
   echo "Connected to anaconda"
   mkdir -p ${CONDA_DIR}
   wget ${miniCondaInstallLink}  -O ${CONDA_DIR}/miniconda.sh
   bash ${CONDA_DIR}/miniconda.sh -b -u -p ${CONDA_DIR}
   rm -rf ~/miniconda3/miniconda.sh
   echo "######################################init"
   ~/miniconda3/bin/conda init bash
   . ~/.bashrc
   . ~/miniconda3/etc/profile.d/conda.sh
   echo "######################################disable activating base Env by default"
   conda config --set auto_activate_base false
   echo "######################################create pyvxr env"
   conda create -n pyvxr python=3.8 -y
   echo "######################################deactivate base Env"
   conda deactivate
   if [ ! -f ~/.ssh/id_rsa ]
   then
      ssh-keygen -t rsa -f ~/.ssh/id_rsa -q -N ""
      cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
   fi
   echo "######################################activate pyvxr"
   conda activate pyvxr
   echo "######################################install Jupyter"
   conda install -c conda-forge jupyterlab -y
   echo "######################################install pyvxr-ovxr"
   pip3 install $PYVXR_OVXR_FILE_PATH
   echo "######################################copy notebooks to user dir"
   cp -r $NOTEBOOKS_DIR ~/
   echo "######################################Run notebook quick test"
   cd ~/notebooks/Put-Technology-to-Work/testNotebooks/
   ipython -c "%run quicktestNB.ipynb"
else                                                                                                                                   
    echo "                                                                                                                                 
    Not able to connect to anaconda. If you are behind a firewall, please set proper proxy settings and run again. Exiting...   
    To test the connection to anaconda please run the command below:"                                                                      
    echo "if ${testCommand}; then echo 'Connected';else echo 'Not connected';fi"
fi                                                        
