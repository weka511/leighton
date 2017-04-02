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

'''Repository for basic data about planets'''

import math, physics, kepler.kepler as k


    
class Planet: 
    '''Store information about a planet
    
    Attributes:
                name
                a                    Semimajor axis in AU
                e                    eccentricity
                obliquity            obliquity
                hours_in_day         Length of planetary day in Earth hours
                F                    absorption
                E                    emissivity
                K                    conductivity
                C                    specific heat
                rho                  Density
                average_temperature  Average Temperature Kelvin
                longitude_of_perihelion
    '''    
    def __init__(self,name,a=1,e=0,obliquity=-999,longitude_of_perihelion=-999):
        '''
        Create planet and initialize
        Parameters:
             name    Name of planet
        '''
        self.name = name

        self.a                       = a
        self.e                       = e
        self.obliquity               = math.radians(obliquity)  
        self.longitude_of_perihelion = math.radians(longitude_of_perihelion)
    def __str__(self):
        '''Convert planet to string'''
        return ('{0}\n'
                'Semimajor axis          = {1:9.7f} AU\n'
                'eccentricity            = {2:8.6f}\n' 
                'longitude_of_perihelion = {3:6.3f}\n'
                'obliquity               = {4:6.3f}\n' 
                'hours in day            = {5:6.4f}\n' 
                'absorption              = {6:4.2f}\n'
                'emissivity              = {7:4.2f}\n' 
                'conductivity            = {8:5.2g}\n'
                'specific heat           = {9:6.1f}\n'
                'rho                     = {10:6.1f}\n' 
                'average temperature     = {11:5.1f}'
                ).format(
                    self.name,
                    self.a,
                    self.e,
                    self.longitude_of_perihelion,
                    math.degrees(self.obliquity),
                    self.hours_in_day,
                    self.F,
                    self.E,
                    self.K,
                    self.C,
                    self.rho,
                    self.average_temperature
        )
  
    def instantaneous_distance(self,true_longitude):
        '''
        Instantaneaous Distance from Sun in AU
        Appelbaum & Flood equations (2) & (3)
        Parameters:
             true_longitude
        '''
        f = k.true_anomaly_from_true_longitude(true_longitude,PERH=self.longitude_of_perihelion)
        return k.get_distance_from_focus(f,self.a,e=self.e)

    def sin_declination(self,true_longitude):
        '''
        Sine of declination
        Appelbaum & Flood equation (7)
        Parameters:
             true_longitude        
        '''
        return math.sin(self.obliquity) * math.sin(true_longitude)
     
    def cos_zenith_angle(self,true_longitude,latitude,T):
        '''
        Cosine of zenith angle
        Appelbaum & Flood equation (6)
        See also Derivation of the solar geometric 
        relationships using vector analysis by Alistair Sproul

        Renewable Energy 32 (2007) 1187-1205
        '''
        sin_declination=self.sin_declination(true_longitude)
        cos_declination=math.sqrt(1-sin_declination*sin_declination)
        return math.sin(latitude)*sin_declination +            \
            math.cos(latitude)*cos_declination *  math.cos(self.hour_angle(T))

    def hour_angle(self,T):
        '''
        Hour angle
        Appelbaum & Flood equation (8)
        Parameters:
             T     Time in Planetary hours
        '''
        return math.radians(15*T-180)

    def get_earth_days_in_year(self):
        '''
        Number of Earth days in year Planetary Year
        Use Kepler's 2nd law
        '''
        return Earth.get().earth.get_days_in_year()*math.sqrt(self.a*self.a*self.a)

    def get_my_days_in_year(self):
        '''
        Number of Planetary days in Planetary Year
        Use Kepler's 2nd law
        ''' 
        earth_days=self.get_earth_days_in_year()
        return earth_days*Earth.get().hours_in_day/self.hours_in_day
    
class Mercury(Planet):
    '''Data for the planet Mercury'''
    def __init__(self):
        '''Create data for planet'''
        Planet.__init__(self,
                        'Mercury',
                        a=0.387098,  # Wikipedia Mercury page
                        e=0.205630,  # Wikipedia Mercury page
                        obliquity=0,  # Wikipedia Axial Tilt page
                        longitude_of_perihelion=77.45645) # Murray & Dermott
        
class Venus(Planet):
    '''Data for the planet Venus'''
    def __init__(self):
        '''Create data for planet'''
        Planet.__init__(self,
                        'Venus',
                        a=0.723327,  # Wikipedia Venus page
                        e=0.0067,  # Wikipedia Venus page
                        obliquity=177.36, # Wikipedia Axial Tilt pagee
                        longitude_of_perihelion=131.53298)
        
class Earth(Planet):
    '''Data for the planet Earth'''
    earth = None
    @classmethod
    def get(cls):
        if Earth.earth==None:
            Earth.earth=Earth()
        return Earth.earth
    def __init__(self):
        '''Create data for planet'''
        Planet.__init__(self,
                        'Earth',
                        a=1.0, # the  semimajor axis in AU,
                        e=0.017, #  eccentricity
                        obliquity=23.4,   # Wikipedia Axial Tilt page
                        longitude_of_perihelion=102.94719)
        self.hours_in_day = 24
        self.average_temperature = 300        
    def get_days_in_year(self):
        return 365.256363004
    
class Mars(Planet):
    '''Data for the planet Mars'''
    def __init__(self):
        '''Create data for planet'''
        Planet.__init__(self,
                        'Mars',
                        a=1.523679,  # Wikipedia Mars page
                        e=0.093377,  # Appelbaum & Flood
                        obliquity=24.936, # Appelbaum & Flood
                        longitude_of_perihelion=336.04084)
        
        self.hours_in_day = 24.6597 #  http://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html
        self.F = 0.85 # absorption fraction - Leighton & Murray
        self.E = 0.85 # Emissivity - Leighton & Murray
        self.K = 6e-5 * physics.Conversion.cm_per_metre # soil conductivity - Leighton & Murray
        self.C = 3.3 * physics.Conversion.gm_per_Kg # specific heat
        self.rho = 1.6 * physics.Conversion.cm3_per_meter3 / physics.Conversion.gm_per_Kg # density
        self.average_temperature = 210 #http://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html
        
class Jupiter(Planet):
    '''Data for the planet Jupiter'''
    def __init__(self):
        '''Create data for planet'''
        Planet.__init__(self,
                        'Jupiter',
                        a=5.204267,  # Wikipedia Jupiter page
                        e=0.048775,  # Wikipedia Jupiter page
                        obliquity=3.13, # Wikipedia Axial Tilt page
                        longitude_of_perihelion=14.75385)

class Saturn(Planet):
    '''Data for the planet Saturn'''
    def __init__(self):
        '''Create data for planet'''
        Planet.__init__(self,
                        'Saturn',
                        a=9.5820172,   # Wikipedia Saturn page
                        e=0.055723219,  # Wikipedia Saturn page
                        obliquity=26.73, # Wikipedia Axial Tilt page
                        longitude_of_perihelion=92.43194)
        
class Uranus(Planet):
    '''Data for the planet Uranus'''
    def __init__(self):
        '''Create data for planet'''
        Planet.__init__(self,
                        'Uranus',
                        a=19.189253,   # Wikipedia Jupiter page
                        e=0.047220087,  # Wikipedia Uranus page
                        obliquity=97.77, # Wikipedia Axial Tilt page
                        longitude_of_perihelion=170.96424)
        
class Neptune(Planet):
    '''Data for the planet Neptune'''
    def __init__(self):
        '''Create data for planet'''
        Planet.__init__(self,
                        'Neptune',
                        a=30.070900,  # Wikipedia Jupiter page
                        e=0.00867797,  # Wikipedia Neptune page
                        obliquity=28.32,   # Wikipedia Axial Tilt page
                        longitude_of_perihelion=44.97135)

def create(name):
    '''Create a named Planet'''
    planets=[Mercury(),
             Venus(),
             Earth(),
             Mars(),
             Jupiter(),
             Saturn(),
             Uranus(),
             Neptune()
    ]
    for planet in planets:
        if planet.name.upper()==name.upper(): return planet
    return None

if __name__=='__main__':
    import unittest
    
    class TestMarsMethods(unittest.TestCase):
        def setUp(self):
            self.mars = create('mars')
            print(self.mars)
        def test_get_days_in_year(self):
            self.assertAlmostEqual(687,self.mars.get_earth_days_in_year(),places=1)
            self.assertAlmostEqual(668.6,self.mars.get_my_days_in_year(),places=1)
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True: # raised by sys.exit(True) when tests failed
            raise