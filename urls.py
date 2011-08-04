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
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^eunomia_web/', include('eunomia_web.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    
    # Main entry point.
    (r'^$', 'main.views.index'),
    
    # Monitor web app.
    (r'^monitor/$', 'monitor.views.index'),
    (r'^monitor/user/(?P<owner_name>\S+)/$', 'monitor.views.owner_index'),
    (r'^monitor/dataset/(?P<dataset>\S+)/$', 'monitor.views.dataset_index'),
    (r'^monitor/entry/(?P<entry_id>\S+)/$', 'monitor.views.entry_index'),
    (r'^monitor/request/(?P<request_id>\d+)/$', 'monitor.views.request_index'),
    (r'^monitor/hold/(?P<job_id>[0-9\.]+)/$', 'monitor.views.hold_job'),
    (r'^monitor/release/(?P<job_id>[0-9\.]+)/$', 'monitor.views.release_job'),
    
    # Control web app.
    (r'^control/$', 'control.views.index'),
    (r'^control/(?P<instrument>[a-zA-Z0-9]+)/(?P<mode>[a-zA-Z0-9]+)/(?P<dataset>[a-zA-Z0-9_-]+)/(?P<exposure>[a-zA-Z0-9-]+)/$', 'control.views.process_index'),
    (r'^control/(?P<instrument>[a-zA-Z0-9]+)/(?P<mode>[a-zA-Z0-9]+)/$', 'control.views.dataset_index'),
    
    # Inventory web app.
    (r'^inventory/$', 'inventory.views.index'),
    (r'^inventory/(?P<machine_name>[a-zA-Z0-9@-_\.]+)/$', 'inventory.views.detail'),
)












