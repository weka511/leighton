# leighton

## Description

Replication of [Leighton and Murray's Behavior of Carbon Dioside and Other Volatiles on Mars](http://www.mars.asu.edu/christensen/classdocs/Leighton_BehavioCO2_science_66.pdf). The two driver programs are _cores.py_, which executes the model across all available cores, and _gui.py_, which is used to visualize data.

## Contents

| File | Purpose |
| ------------------------- | ------------------------------------------------------------|
|cores.py|Process model via leighton.py, but run across all available cores |
|cores.dat|Default parameter file for _cores.py_ |
|driver.bat|Used to run leighton.py for a range of latitudes|
|gui.py|User Interface for viewer.py |
|kepler|Submodule with models for planetary motion and Solar irradiance | 
|leighton.py|Parse command line parameters and execute model. May be executed stand alone for testing (without _cores.py_)|
|planet.py| Repository for basic data about planets |
|solar_tests.py|Test code to exercise solar model from kepler |
|thermalmodel.py|Slices of Mars' interior, together with model for heat flow |
|utilities.py|Utility functions for log files, zipping lists, choosing colours for plots |
|viewer.py|Used to plot data files produced by _leighton.py_ and _cores.py_ |
|physics.py|Repository for physical laws and constants |

The code has been tested with Python 3.5.1 |Anaconda 2.4.1 (64-bit).

## Coding conventions

All calculations should use SI units, except in modules which communicate with the user, where customary units may be used (e.g. angles in degrees, days, months, etc.)



