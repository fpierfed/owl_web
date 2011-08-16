from distutils.core import setup, Extension

setup(
    name = 'grapher',
    description = "Enhancements to PyDOT", 
    author = "Francesco Pierfederici", 
    author_email = "fpierfed@stsci.edu",
    version='0.1',
    
    ext_modules = [
        Extension("_grapher", 
                  sources=["grapher.c", "grapher.i"],
                  include_dirs=['/usr/include/graphviz'],
                  libraries=['gvc', 'graph'])],
    py_modules=['grapher'],
)
