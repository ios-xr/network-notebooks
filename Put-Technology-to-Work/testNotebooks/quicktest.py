# DESCRIPTION: This is a python script that executes the cells of the notebook, quicktestNB.ipynb
# AUTHOR: Sarah Samuel (sasamuel@cisco.com)
# DATE: 15 July 2021

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors import CellExecutionError

with open('quicktestNB.ipynb') as f:
    nb = nbformat.read(f, as_version=4)

ep = ExecutePreprocessor(timeout=-1, kernel_name='python3')
print ("Executing Quick Test Notebook - Takes 7-8 minutes to complete\n")
try:
    ep.preprocess(nb, {'metadata': {'.': 'notebooks/'}})    
except CellExecutionError:
    out = None
    msg = 'Error executing the notebook "%s".\n' % 'quicktestNB.ipynb'
    msg += 'See notebook "%s" for the traceback.\n' % 'quicktestNB.ipynb'
    print(msg)
finally:
    with open('quicktestNB.ipynb', mode='w', encoding='utf-8') as f:
        nbformat.write(nb, f)

print ("\nAll cells of Quick Test Notebook executed successfully. Check quicktestNB.ipynb for logs\n")
