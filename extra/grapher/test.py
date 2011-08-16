#!/usr/bin/env python
import grapher

dot = open('bcw.dot').read()
print(grapher.create(dot, "dot", "svg"))

