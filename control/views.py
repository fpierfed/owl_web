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

from django.template import Context, loader
from django.http import HttpResponse

from eunomia.utils import which





# Constants
# TODO: We should be getting these from, say a DB.
REPO_ROOT = '/data2/jwst/repository/raw'
EXE = which('process_dataset.py')

dataset001 = {'name': 'dataset_001', 
              'exposures': ('raw-000001', 'raw-000002', 'raw-000003', 'raw-000004')}
dataset002 = {'name': 'dataset_002', 
              'exposures': ('raw-000001', 'raw-000002')}
INSTRUMENTS = ({'name': 'instrument1/modeA', 
                'link_name': 'Regular BCW',
                'datasets': (dataset001, dataset002)}, 
               {'name': 'instrument1/modeD', 
                'link_name': 'iRODS BCW',
                'datasets': (dataset001, dataset002)}, )




def index(request):
    """
    Main entry point for the control web app.
    """
    # Load the template.
    t = loader.get_template('control/index.html')
    
    # Render the template and exit.
    c = Context({'instruments': INSTRUMENTS})
    return(HttpResponse(t.render(c)))


def dataset_index(request, instrument, mode):
    """
    Display available dataset exposures for the given instrument and mode.
    """
    # Load the template.
    t = loader.get_template('control/dataset.html')
    
    name = str(instrument) + '/' + str(mode)
    
    # Find the instrument.
    instr_dict = {'name': '%s not found' % (name),
                  'datasets': ()}
    for i in INSTRUMENTS:
        if(i['name'] == name):
            instr_dict = i
            break
    
    # Render the template and exit.
    c = Context({'instrument': instr_dict})
    return(HttpResponse(t.render(c)))


def process_index(request, instrument, mode, dataset, exposure, 
                  repo_root=REPO_ROOT, exe=EXE):
    """
    Display available dataset exposures for the given instrument and mode.
    """
    # Load the template.
    t = loader.get_template('control/process.html')
    
    # Special handling for modeD which uses iRODS. This is a hack :-(
    if(str(mode) == 'modeD'):
        repo_root = repo_root.replace('/jwdmsdevvm1/data1/', '', 1)
        exe = which('process_idataset.py')
    
    name = str(instrument) + '/' + str(mode)
    
    # Find the instrument.
    instr_dict = {'name': '%s not found' % (name),
                  'datasets': ()}
    for i in INSTRUMENTS:
        if(i['name'] == name):
            instr_dict = i
            break
    
    # Get the repository path.
    repo_path = os.path.join(repo_root, dataset)
    
    # Compose the command.
    args = (exe, '-r', repo_path, '-i', instrument, '-m', mode, exposure)
    proc = subprocess.Popen(args, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            shell=False)
    err = proc.wait()
    
    # Render the template and exit.
    cmd_str = ' '.join(args)
    c = Context({'command': cmd_str,
                 'exit_code': err,
                 'instrument': instr_dict,
                 'dataset': dataset,
                 'exposure': exposure})
    return(HttpResponse(t.render(c)))




















