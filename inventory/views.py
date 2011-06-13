# Copyright (C) 2010 Association of Universities for Research in Astronomy(AURA)
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#     1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
# 
#     2. Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
# 
#     3. The name of AURA and its representatives may not be used to
#       endorse or promote products derived from this software without
#       specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY AURA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL AURA BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
import os
import subprocess
import tempfile
import time

from django.template import Context, loader
from django.http import HttpResponse

from eunomia import job





# Constants
# TODO: We should be using condor_quill or similar system.
EXE = '/usr/bin/condor_status'
# Timeout in seconds for the call to EXE.
TIMEOUT = 5.



def parse(stdout):
    """
    Parse a machine ClassAd list and return an object per machine. We re-use the
    Job class from eunomia since it is general enough (for now).
    """
    machines = []
    
    # ClassAds end with a '\n\n' and start with 'MyType = "Machine"'.
    ad = ''
    for line in stdout:
        if(line.strip() == 'MyType = "Machine"' and ad):
            # New ClassAd: parse the last one and start a new one.
            machines.append(job.Job.newFromClassAd(ad))
            ad = ''
        ad += line
    # The file ended and hence we must have a last ClassAd: parse it and quit.
    machines.append(job.Job.newFromClassAd(ad))
    return(machines)


def _run_and_get_stdout(args, timeout):
    """
    Simple wrapper around subprocess.Popen() with support for timeouts. Return
    the path of the file with the STDOUT content. In case the process had to be 
    killed or returned an error, the file is removed and None returned.
    """
    # Open the file for writing.
    (fid, file_name) = tempfile.mkstemp()
    os.close(fid)
    f = open(file_name, 'w')
    
    # Execute the external process and redirect STDOUT to f.
    proc = subprocess.Popen(args, 
                            stdout=f, 
                            shell=False)
    
    # Since proc.wait() can deadlock, it is prudent to jut poll...
    start_time = time.time()
    while(time.time() - start_time < timeout):
        exit_code = proc.poll()
        if(exit_code is None):
            # The process is still running.
            time.sleep(.1)
            continue
        
        # If we are here, the process finished.
        if(exit_code != 0):
            f.close()
            return(None)
        
        f.close()
        return(file_name)
    # If the process is still tunning at this point, kill it.
    proc.kill()
    f.close()
    return(None)





def index(request):
    """
    Main entry point for the inventory web app.
    """
    machines = ({'Name': 
                 'Error communicating with condor please try again later.'}, )
    
    # Load the template.
    t = loader.get_template('inventory/index.html')
    
    # Call condor_status and get a full list of machines and their ClassAds.
    file_name = _run_and_get_stdout((EXE, '-long'), TIMEOUT)
    
    if(file_name is not None):
        f = open(file_name, 'r')
        machines = parse(f)
        f.close()
    
    # Cleanup.
    os.remove(file_name)
    
    # Render the template and exit.
    c = Context({'machines': machines})
    return(HttpResponse(t.render(c)))


def detail(request, machine_name):
    """
    Display the machine details.
    """
    machines = ({'Name': 
                 'Error communicating with condor please try again later.'}, )
    
    # Load the template.
    t = loader.get_template('inventory/detail.html')
    
    # Call condor_status and get a full list of machines and their ClassAds.
    file_name = _run_and_get_stdout((EXE, '-long', machine_name), TIMEOUT)
    if(file_name is not None):
        f = open(file_name, 'r')
        machines = parse(f)
        f.close()
    
    # Cleanup.
    os.remove(file_name)
    
    # Render the template and exit.
    c = Context({'machine': machines[0]})
    return(HttpResponse(t.render(c)))






















































