import pytest
import subprocess
import sys

#initialize the starting variables.
child_procs = []
cmds = [["python3", "fake_sas.py"],["pytest"]]

# Start fake_sas so the test cases can interact with it.
subprocess.Popen()
proc = subprocess.Popen(cmds[0],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
child_procs.append(proc)

# Ensure that fake_sas is running correctly.
success_output = "Will start server at localhost:9000, use <Ctrl-C> to stop."

try:
    output = child_procs[0].proc.stdout.readline()
    if output == success_output:
        # Start the test cases.
        proc = subprocess.Popen(cmds[1],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        child_procs.append(proc)

    else:
        print("Fake_sas did not successfully start exiting...")
        sys.exit(1)

except TimeoutExpired:
    child_procs[0].kill()
    output, errors = proc.communicate()




