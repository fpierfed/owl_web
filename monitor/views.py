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

# Create your views here.
from urllib import quote

from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

import pydot
import grapher

from owl import blackboard
from owl import condorutils


# import ctypes
# import ctypes.util
# try:
#     libgvc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('gvc'))
#     libgraph = ctypes.cdll.LoadLibrary(ctypes.util.find_library('graph'))
# except:
#     libgvc = ctypes.cdll.LoadLibrary('/usr/local/lib/libgvc.dylib')
#     libgraph = ctypes.cdll.LoadLibrary('/usr/local/lib/libgraph.dylib')





def generic_index(request, **kwds):
    """
    Generic interface to the various index views allowing us to specify optional
    constraints to blackboard entry selection.

    Valid constraints are dataset=... and owner=... (apart from no constraint).
    """
    valid_keys = set(('dataset', 'owner'))
    keys = set(kwds.keys())
    assert(keys.issubset(valid_keys))

    # Load the template.
    t = loader.get_template('monitor/index.html')

    # Get the bb entries.
    entries = blackboard.listEntries(**kwds)

    # Decorate them with extra attributes.
    for e in entries:
        submit_host = e.GlobalJobId[:e.GlobalJobId.find('#')]
        e.RequestId = '%s@%s' % (quote(str(e.DAGManJobId)), submit_host)

    # Render the template and exit.
    c = Context({'entries': entries, })
    return(HttpResponse(t.render(c)))


def index(request):
    """
    Main entry point for the monitor web app. Display a list of 'OSF` blackboard
    entries:
        dataset | user | datetime | Stage1 Status | Stage2 Status | ...
        ...
    """
    return(generic_index(request))


def owner_index(request, owner_name):
    """
    List all entries associated with `owner`.
    """
    return(generic_index(request, owner=owner_name))


def dataset_index(request, dataset):
    """
    List all entries associated with `dataset`.
    """
    return(generic_index(request, dataset=dataset))


def entry_index(request, entry_id):
    """
    Detail page on a specific blackboard entry.
    """
    # Load the template.
    t = loader.get_template('monitor/detail.html')

    # Get the bb entries.
    entry = blackboard.getEntry(entry_id)

    # Render the template and exit.
    c = Context({'entry': entry, })
    return(HttpResponse(t.render(c)))


def hold_job(request, job_id):
    """
    Send the gven job_id a condor_hold. Then redirect to the main index page.
    """
    # Call condor_hold job_id
    err = condorutils.condor_hold(job_id)

    # Redirect to the main index.
    return(HttpResponseRedirect(reverse('monitor.views.index')))


def release_job(request, job_id):
    """
    Send the gven job_id a condor_release. Then redirect to the main index page.
    """
    # Call condor_release job_id
    err = condorutils.condor_release(job_id)

    # Redirect to the main index.
    return(HttpResponseRedirect(reverse('monitor.views.index')))



def request_index(request, request_id):
    """
    Detail page on a specific request (i.e. DAGManJobId@<submit host>) by
    creating an SVG representation of the executing DAG.
    """
    # Load the template.
    t = loader.get_template('monitor/request_svg.html')

    # Get the bb entries.
    dagManJobId, host = request_id.split('@', 1)
    (dataset, user, requestId, stages) = blackboard.getOSFEntry(dagManJobId)

    # Filter out all the spurious ones.
    # FIXME: Maybe do this a bit better, huh?
    hh = host + '#'
    stages = [s for s in stages if s.GlobalJobId.startswith(hh)]

    # Create the DOT graph.
    dot = pydot.Dot(type='digraph')

    # Keep track of node names vs node ids.
    nodes = {}                          # {node name: [node id1, node id2, ...]}
    for stage in stages:
        nodeId = '%d.%d' % (stage.ClusterId, stage.ProcId)

        # Remember that if a condor job is on hold, it will have an ExitCode =
        # None and a JobState = Exited.
        if(stage.JobState != 'Exited'):
            nodeLabel = '%s - %s' % (stage.DAGNodeName,
                                     stage.JobState)
        elif(stage.ExitCode == None):
            # The corresponding condor job was put on hold.
            nodeLabel = '%s - %s' % (stage.DAGNodeName,
                                     'On Hold')
        else:
            nodeLabel = '%s - %s (%d)' % (stage.DAGNodeName,
                                          stage.JobState,
                                          stage.ExitCode)
        if(stage.JobState == 'Exited' and stage.ExitCode != 0):
            dot.add_node(pydot.Node(nodeId, shape='ellipse', label=nodeLabel,
                                    style="filled", fillcolor="red"))
        else:
            dot.add_node(pydot.Node(nodeId, shape='ellipse', label=nodeLabel))

        if(nodes.has_key(stage.DAGNodeName)):
            nodes[stage.DAGNodeName].append(nodeId)
        else:
            nodes[stage.DAGNodeName] = [nodeId, ]

    # Now add the edges of the graph.
    for stage in stages:
        if(stage.DAGParentNodeNames):
            nodeId = '%d.%d' % (stage.ClusterId, stage.ProcId)

            parentNames = stage.DAGParentNodeNames.split(',')
            for parentName in parentNames:
                if(not nodes.has_key(parentName)):
                    continue

                # We have three cases:
                #   1. node.Instances == parent.Instances: 1 to 1
                #   2. node.Instances > parent.Instances:  scatter
                #   3. node.Instances < parent.Instances:  gather
                # We can treat 2. and 3. the same way. !. is different.
                if(len(nodes[stage.DAGNodeName]) == len(nodes[parentName])):
                    # Case 1.
#
# FIXME: here we assume that ProcIds are the same for parent and child.
#
                    pClusterId = int(nodes[parentName][0].split('.')[0])
                    pId = '%d.%d' % (pClusterId, stage.ProcId)
                    dot.add_edge(pydot.Edge(pId, nodeId))
                else:
                    # Cases 2. and 3.
                    for parentId in nodes[parentName]:
                        dot.add_edge(pydot.Edge(parentId, nodeId))

    # Create the SVG graph.
# This does a system call, which I would rather avoid.
#     rawSvg = dot.create(format='svg')

# This works standalone but not in the web environment... dunno why :-(
#     cLength = ctypes.c_int(1)
#     cSvg = ctypes.pointer(ctypes.create_string_buffer(1))
#     dotString = dot.to_string()
#
#     gvc = libgvc.gvContext()
#     g = libgraph.agmemread(dotString)
#
#     libgvc.gvLayout(gvc, g, "dot")
#     libgvc.gvRenderData(gvc, g, "svg",
#                           ctypes.byref(cSvg), ctypes.byref(cLength))
#
#     libgvc.gvFreeLayout(gvc, g)
#     libgraph.agclose(g)
#     libgvc.gvFreeContext(gvc)
#
#     rawSvg = ctypes.string_at(cSvg)

    # This works, as long as I convert the unicode to string.
    dotString = dot.to_string()
    rawSvg = grapher.create(str(dotString), 'dot', 'svg')

    # Remove the header.
    svg = rawSvg.split('\n')[6:]

    # Render the template and exit.
    c = Context({'dataset': dataset,
                 'user': user,
                 'requestId': requestId,
                 'svg': '\n'.join(svg)})
    return(HttpResponse(t.render(c), mimetype='application/xhtml+xml'))


def request_index_old(request, request_id):
    """
    Detail page on a specific request (i.e. DAGManJobId) in a way that resembles
    the OPUS/NHPPS OSF blackboard:
        Dataset, Owner, DAGManJobId, [Nodei JobState, Nodei ExitCode, ]
    """
    # Load the template.
    t = loader.get_template('monitor/request.html')

    # Get the bb entries.
    (dataset, user, requestId, stages) = blackboard.getOSFEntry(request_id)

    # Render the template and exit.
    c = Context({'dataset': dataset,
                 'user': user,
                 'requestId': requestId,
                 'stages': stages})
    return(HttpResponse(t.render(c)))
