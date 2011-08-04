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
from django.template import Context, loader
from django.http import HttpResponse

from eunomia import condorutils






def index(request):
    """
    Main entry point for the inventory web app.
    """
    # Load the template.
    t = loader.get_template('inventory/index.html')
    
    # Call condor_status and get a full list of machines and their ClassAds.
    machines = condorutils.condor_status()
    
    # Render the template and exit.
    c = Context({'machines': machines})
    return(HttpResponse(t.render(c)))


def detail(request, machine_name):
    """
    Display the machine details.
    """
    # Load the template.
    t = loader.get_template('inventory/detail.html')
    
    # Call condor_status and get a info of machine_name.
    machines = condorutils.condor_status(machine_name)
    
    # Render the template and exit.
    c = Context({'machine': machines[0]})
    return(HttpResponse(t.render(c)))






















































