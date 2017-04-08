# leighton

Replication of [Leighton and Murray's Behavior of Carbon Dioside and Other Volatiles on Mars](http://www.mars.asu.edu/christensen/classdocs/Leighton_BehavioCO2_science_66.pdf)


| File | Purpose |
| ------------------------- | ------------------------------------------------------------|
| cores.py | Process model via leighton.py, but run across all available cores |
| cores.dat | Default paramter file for cores.py |
| gui.py | GUI for viewer.py |
| kepler | Submodule with models for planetary motion and Solar irradiance | 
| leighton.py | Driver for executing model |
| planet.py |  Repository for basic data about planets |
| solar_tests.py | Test code to exercise solar model from kepler |
| thermalmodel.py | Slices of Mars' interior, together with model for heat flow |
| utilities.py | Utility functions for log files, zipping lists, choosing colours for plots |
| viewer.py | Used to plot data files from leighton.py |
| physics.py | Repository for physical laws and constants |


