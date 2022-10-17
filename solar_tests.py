#!/usr/bin/env python

# Copyright (C) 2015-2022 Greenweaves Software Pty Ltd

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

'''
Model for solar irradiation, based on Solar Radiation on Mars,
 Joseph Appelbaum & Dennis Flood, Lewis Research Center, NASA
'''
from kepler.solar      import Solar
from kepler.kepler     import get_eccentric_anomaly, get_true_anomaly, true_longitude_from_true_anomaly
from matplotlib.cm     import jet
from matplotlib.pyplot import figure, show
from math              import asin, degrees, pi, radians
from numpy             import linspace, meshgrid, vectorize
from planet            import Planet
from scipy.integrate   import quad
from unittest          import main, TestCase
from utilities         import extremum

if __name__=='__main__':

    def true_longitude(day):
        M            = 2*pi*(day-2)/687 #perihelion Jan 3
        E            = get_eccentric_anomaly(M,mars.e)
        true_anomaly = get_true_anomaly(E,mars.e)
        return true_longitude_from_true_anomaly(true_anomaly)

    class TestMarsMethods(TestCase):
        def setUp(self):
            self.mars = Planet.Mars()
            self.solar = Solar(self.mars)

    #   This test is based on figure 3 of Appelbaum & Flood, with two adjustments.
    #   Appelbaum & Flood have the perihelion and aphelion at LS = 249 degress and
    #   68 degress respectively (Figure 3). But in the section preceding equation (3)
    #   the perihelion is stated to be at 248 degrees. The aphelion is 180 degrees
    #   before or after the perihelion, so this has also been shifted.

        def test_beam_irradience_as_function_true_longitude(self):
            d0=-1
            d1=-1
            for i in range(360):
                d2=self.mars.instantaneous_distance(i)
                if d0>-1 and d1>-1:
                    if d0>d1 and d1<d2:
                        x=extremum(i-2,i-2,i,d0,d1,d2)
                        d=self.mars.instantaneous_distance(x)
                        irr=self.solar.beam_irradience(d)
                        self.assertAlmostEqual(248,x)
                        self.assertAlmostEqual(718,irr,delta=1)
                    if d0<d1 and d1>d2:
                        x=extremum(i-2,i-2,i,d0,d1,d2)
                        d=self.mars.instantaneous_distance(x)
                        irr=self.solar.beam_irradience(d)
                        self.assertAlmostEqual(68,x)
                        self.assertAlmostEqual(493,irr,delta=1)
                d0=d1
                d1=d2

        def test_beam_irradience(self):
            self.assertAlmostEqual(1371/(1.5236915**2),
                                   self.solar.beam_irradience(self.mars.a),
                                   places=1)

        # The next few tests are based on Table II i Appelbaum & Flood

        def test_top_atmosphere(self):
            integral,error=quad(integrand,12,13,args=(self.solar,69))
            self.assertAlmostEqual(488,integral,delta=1.5)

        def test_top_atmosphere2(self):
            integral,error=quad(integrand,13,14,args=(self.solar,69))
            self.assertAlmostEqual(460,integral,delta=1)


        def test_top_atmosphere3(self):
            integral,error=quad(integrand,14,15,args=(self.solar,249))
            self.assertAlmostEqual(376,integral,delta=1)

        def test_top_atmosphere7(self):
            integral,error=quad(integrand,18,19,args=(self.solar,69))
            self.assertAlmostEqual(25,integral,delta=1)


    def integrand(x, solar,ls):
        return solar.surface_irradience(ls,22.3,x)

    try:
        main()
    except SystemExit as inst:
        pass


    def generate_irradiance(planet,true_longitude,latitude):
        x=[]
        y=[]
        for TT in range(120,200):
            T=TT/10
            irradiance=solar.surface_irradience(true_longitude,latitude,T)
            x.append(T)
            y.append(irradiance)
        return (x,y)

    def add_text(y0,xs,ys,ax=None):
        i0=ys.index(y0)
        ax.text (xs[i0],y0,'{0:.0f}'.format(y0))

    # Plot irradiance at latitude of Viking Lander
    def plot_irradiance(true_longitude=299,colour='r',ax=None):
        (x,y)=generate_irradiance(mars,true_longitude,22.3)
        ax.plot(x,y,colour,label=r'${0}^\circ$'.format(true_longitude))

    mars                = Planet.create('Mars')
    solar               = Solar(mars)
    beam_irradience_top = solar.beam_irradience(mars.a) # Mean beam irradience at top of atmosphere
    print ('Mean beam irradience at top of atmosphere = {0:6.2f} W/m2'.\
          format(beam_irradience_top))


    # Instananeous beam irradience at top of atmosphere
    xs=[]
    ys=[]
    d0=-1
    d1=-1

    for i in range(687):
        tl=true_longitude(i)
        xs.append(degrees(tl))
        d2=mars.instantaneous_distance(tl)
        ys.append(solar.beam_irradience(d2))
        if d0>-1 and d1>-1:
            if d0>d1 and d1<d2:
                x=extremum(i-2,i-2,i,d0,d1,d2)
                d=mars.instantaneous_distance(x)
                irr=solar.beam_irradience(d)
                print ('Perihelion day={0:.3f}, distance={1:.3f}, irradiance={2:.2f}'.format(x,d,irr))
            if d0<d1 and d1>d2:
                x=extremum(i-2,i-2,i,d0,d1,d2)
                d=mars.instantaneous_distance(x)
                irr=solar.beam_irradience(d)
                print ('Aphelion day={0:.3f}, distance={1:.3f}, irradiance={2:.2f}'.format(x,d,irr))
        d0=d1
        d1=d2
    fig = figure(figsize=(12,12))
    ax = fig.add_subplot(2,2,1)

    ax.axis([0, 360, 450, 750])
    ax.set_title('Beam irradience at top of Mars atmosphere')
    ax.set_xlabel('Areocentric longitude - degrees')
    ax.set_ylabel('Beam irradience at top of Mars atmosphere - W/m2')
    add_text(min(ys),xs,ys,ax=ax)
    add_text(max(ys),xs,ys,ax=ax)
    ax.grid(True)
    ax.plot(xs,ys)

    # Variation of solar declination angle

    x=[]
    y=[]
    for day in range(687):
        tl=true_longitude(day)
        x.append(degrees(tl))
        y.append(degrees(asin(mars.sin_declination(tl))))

    ax = fig.add_subplot(2,2,2)
    ax.set_title('Variation of solar declination angle')
    ax.axis([0, 360, -25, 25])
    ax.set_xlabel('True longitude - degrees')
    ax.set_ylabel('Solar Declination Angle - degrees')
    ax.grid(True)
    ax.plot(x,y)

    # Diurnal Variation of Beam Irradience on a horizontal surface

    ax = fig.add_subplot(2,2,3)
    ax.set_title('Diurnal Variation of Beam Irradience on a horizontal surface')
    ax.set_xlabel('Solar Time - Hours')
    ax.set_ylabel('Beam Irradiance - W/m2')
    plot_irradiance(69,'r',ax=ax)
    plot_irradiance(120,'g',ax=ax)
    plot_irradiance(153,'b',ax=ax)
    plot_irradiance(249,'c',ax=ax)
    plot_irradiance(299,'m',ax=ax)
    ax.axis([12, 20, 0, 600])
    ax.legend(loc='upper right',title=r'$L_S$')
    ax.grid(True)

    def surface_irradience(day,latitude):
        return solar.surface_irradience_daily(true_longitude(day),radians(latitude),total=False)

    ax4=fig.add_subplot(2,2,4)

    x    = linspace(0,687)
    y    = linspace(-90,90)
    X, Y = meshgrid(x, y)
    Z    = (vectorize(surface_irradience))(X,Y)
    cax  = ax.pcolormesh(X, Y, Z, cmap = jet)
    cbar = fig.colorbar(cax)

    #ax4.set_xticks([i for i in lengths_of_months()])
    #ax4.set_xticklabels(['JFMAMJJASOND'[i] for i in range(0,12)])
    #ax4.set_yticks([i for i in range(-90,91,30)])
    #ax4.set_yticklabels([lat(i) for i in range(-90,91,30)])
    fig.suptitle('Surface Irradiance')


    fig.savefig('solar')
    show()
