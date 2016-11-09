# pymidas

## About
A python library that aims to provide a subset of the MIDAS API for use in python.  And, a tool that helps set up and work with MIDAS experiments.

## Getting Started
Install the utility and midas python library with a few deft strokes of the keyboard

```bash
python setup.py install
```

Note: you may need to sudo that command.

### pymidas
Classes that wrap the MIDAS object that they describe.

```python
import midas

exptab = midas.Exptab()
print exptab.expt_names
```

### mhelper
A command line utility that helps implement MIDAS experiments in a certain style.  The general usage idiom is as follows:

```bash
mhelper cmd [arg1 ...]
```

**Commands**
* init [expt-name expt-dir data-dir] 
  * starts a new experiment
  * arguments can be provided or entered interactively
  * the data-dir is symlink to <expt-dir>/resources/data
* link [resource-dir]
  * symlinks an item in the resources directory to the current directory
  
  

