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
"""
Wrapper around pydot to enable in-memory rendering of graphs instead of going
to disk and using a system call to graphviz executables.

Limitations: one cannot use shape files.
"""
import ctypes
import ctypes.util

import pydot
from pydot import Error, InvocationException, Node, Edge, Graph, Subgraph, Cluster



try:
    graphlib = ctypes.cdll.LoadLibrary(ctypes.util.find_library('gvc'))
except:
    graphlib = ctypes.cdll.LoadLibrary('/usr/local/lib/libgvc.dylib')



class Dot(pydot.Dot):
    def create(self, layout='dot', format='svg'):
        """Creates and returns a (Postscript by default) representation of the 
        graph.

        create will write the graph in memory according to the layout specified
        ('twopi' by default), reading the Postscript output and returning it as
        a string is the operation is successful.
        On failure None is returned.
        
        Possible layouts are
            'dot'
            'neato'
            'fdp'
            'sfdp'
            'twopi'
            'circo'
        
        Possible formats are
            'ps'
            'svg'
            'svgz'
            'fig'
            'mif'
            'hpgl'
            'pcl'
            'png'
            'gif'
            'dia'
            'imap'
            'cmapx'
        
        and possibly more, depending on your graphviz installation.
        """
        # Init some C vars.
        cLength = ctypes.c_int(0)
        cResult = ctypes.pointer(ctypes.create_string_buffer(1))
        
        # Turn the current graph into a string.
        dot = ctypes.c_char_p(self.to_string())
        
        # Init the Graphviz context and layout from layout/self.prog and dot.
        format = 'svg'
        layout = 'dot'
        
        gvc = graphlib.gvContext()
        g = graphlib.agmemread(dot)
        
        graphlib.gvLayout(gvc, g, layout)
        graphlib.gvRenderData(gvc, g, format, ctypes.byref(cSvg), ctypes.byref(cLength))
        
        graphlib.gvFreeLayout(gvc, g)
        graphlib.agclose(g)
        graphlib.gvFreeContext(gvc)
        return(ctypes.string_at(cSvg))
        return(dot)
