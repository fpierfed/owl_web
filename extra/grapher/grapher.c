#include <gvc.h>
#include "grapher.h"



char* create(char* data, char* layout, char* format) { 
    GVC_t*          gvc;
    graph_t*        g;
    char*           result = 0;
    unsigned int    resultSize = 0;
    int             err = 0;
    
    
    // Simple sanity check.
    if(!layout)
        layout = "dot";
    if(!format)
        format = "svg";    
    
    // Malloc result to by a small size.
    result = (char*)malloc(sizeof(char) * 4096);
    
    if(data) {
        // Draw the graph.
        gvc = gvContext();
        
        g = agmemread(data);
        
        gvLayout(gvc, g, layout);
        gvRenderData(gvc, g, format, &result, &resultSize);
        
        gvFreeLayout(gvc, g);
        agclose(g);
        err = gvFreeContext(gvc);
    }
    return(result);
}



