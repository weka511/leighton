# Copyright (C) 2015-2017 Greenweaves Software Pty Ltd

# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>
'''This module keeps track of useful fragments of physics'''

class Conversion:
    '''Used to convert between CGS and SI'''
    cm_per_metre = 100
    gm_per_Kg = 1000
    cm3_per_meter3 = cm_per_metre*cm_per_metre*cm_per_metre
    metres_per_au=149597870700.0 #http://neo.jpl.nasa.gov/glossary/au.html
    seconds_per_day=24*60*60
     
    @staticmethod
    def au2meters(au):
        '''
        Convert a distance from Astronomical Units to Metres
         
        Arguments
        au -- distance in Astronomical Units
        '''
        return Conversion.metres_per_au*au
     
    @staticmethod 
    def meters2au(meters):
        '''
        Convert a distance from Metres to Astronomical Units
        
        Arguments
        meters -- distance in Astronomical Units
        '''        
        return meters/Conversion.metres_per_au    
class CO2:
    
    '''Properties of carbon dioxide'''
    condensation_temperature = 145
    latent_heat = 574               # http://www.engineeringtoolbox.com/fluids-evaporation-latent-heat-d_147.html    
    albedo = 0.6
    
class Radiation:
    '''Stefan Bolzmann law'''
    stefan_bolzmann = 5.670374e-8
    
    @staticmethod
    def bolzmann(t):
        '''Use Stefan Bolzmann to calculate radiation from temperature'''
        t2=t*t    # we call this function often, so don't use exponentiation
        return Radiation.stefan_bolzmann*t2*t2 
    
    @staticmethod
    def reverse_bolzmann(radiation):
        '''Use Stefan Bolzmann to calculate  temperature from radiation'''
        return (radiation/Radiation.stefan_bolzmann)**0.25
    
if __name__=='__main__':
    print (Radiation.reverse_bolzmann(1350*(1-0.3)/4))