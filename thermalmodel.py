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

'''
This module carries out heat flow calculation for Mars.
The thermal model consists of a series of Layers,
the top one being the Surface
'''
import math, planet, kepler.solar as s, utilities, physics, kepler.kepler as k



class Layer:
    '''
    One Layer from Planet.
    
    Layer is an abstact class, which is implemented by Surface, Medial,
    and Bottom.
    
    Attributes:
        name              'Surface', 'Medial', or 'Bottom' - used for logging
        latitude          Latitude at which we are calculating
        thickness         Thickness of layer
        temperature       Temperature at start of step
        new_temperature   Used to hold temperature that we ar calculating, to
                          ensure that entire step takes place at one
                          temperature
        planet            Planet we are modelling
        heat_gain         Gain during one step
    '''
    def __init__(self,name,latitude,thickness,planet,temperature):
        '''Create a layer'''
        self.name = name
        self.latitude = latitude
        self.thickness = thickness
        self.temperature = temperature
        self.new_temperature = temperature
        self.planet = planet
        self.heat_gain = 0
        
    def propagate_temperature(self,above,below,true_longitude,T,dT,record,model):
        raise NotImplementedError('propagate_temperature')
    
    def temperature_gradient(self,neighbour):
        '''
        Calculate temperature gradient between neighbour and this layer.
        Gradient will be +ve (heat will flow to me) if neighbour is hotter
        '''
        temperature_difference = neighbour.temperature - self.temperature
        distance = 0.5*(self.thickness + neighbour.thickness)
        return (temperature_difference / distance)
        
    def heat_flow(self,neighbour):
        '''
        heat flow to me from neighbour
        parameters:
            neighbour
        '''
        return(self.planet.K * self.temperature_gradient(neighbour))


    def update_temperature(self,heat_gain_per_second,dT):
        '''
        Calculate new temperature given heat flow
        Don't change temperatures until every Layer has been processed
        otherwise energy won't be conserved, which would be a Very Bad Thing;
        just cache result
        
        Parameters:
           heat_gain_per_second  Rate at which heat flows in
           dT                    Number of seconds
           planet                Planet we are modelling
        '''
        self.calculate_heat_gain(heat_gain_per_second,dT)
        delta_temperature= self.heat_gain / (self.planet.C * self.planet.rho * self.thickness)
        self.new_temperature += delta_temperature

    def calculate_heat_gain(self,heat_gain_per_second,dT):
        '''
        Heat gained during step
        
        Parameters:
            heat_gain_per_second   Rate at which heat flows in
            dT                     Number of seconds
        '''
        self.heat_gain = heat_gain_per_second*dT
        
    def __str__(self):
        '''Convert to text for display'''
        return ( 
            '{0}: Latitude={1:6.1f},'  
            'Thickness={2:6.3f}, '  
            'Temperature = {3:6.1f},{4:6.1f}'
            ).format(self.name,
                     self.latitude,
                     self.thickness,
                     self.temperature,
                     self.new_temperature)

class Surface(Layer):
    '''
    Top Layer: gains and loses heat through radiation, 
    and exchanges heat with Layer below
    
    Attributes:
        solar         Solar model
        co2           Indicates whether we should include CO2 (sublimation
                         and condensation)
        total_co2     Amount of CO2 frozen    
    '''
    def __init__(self,latitude,thickness,solar,planet,temperature,co2):
        '''
        Initialize
        
        Parameters:
            latitude     The latitude for which we are performing calculations
            solar        Solar model
            planet       The planet for which we are performing calculations
            temperature  Starting temperature
            co2          Indicates whether we should include CO2 (sublimation
                         and condensation)
        '''
        Layer.__init__(self,'Surface',latitude,thickness,planet,temperature)
        self.solar     = solar
        self.co2       = co2
        self.total_co2 = 0
    
    def update_temperature_adjust_for_co2(self,total_inflow_before_latent_heat,dT):
        if self.temperature>physics.CO2.condensation_temperature:
            if self.total_co2>0 and total_inflow_before_latent_heat>0:
                total_inflow_before_latent_heat=self.sublimate_co2(total_inflow_before_latent_heat)
            self.update_temperature(total_inflow_before_latent_heat,dT)
        else:
            if self.co2_is_available() and total_inflow_before_latent_heat<0:
                total_inflow_before_latent_heat=self.freeze_co2(total_inflow_before_latent_heat)           
            self.update_temperature(total_inflow_before_latent_heat,dT) 
            
    def propagate_temperature(self,above,below,true_longitude,T,dT,record,model):
        irradiance=self.absorption()*self.solar.surface_irradience(true_longitude,self.latitude,T)
        
        #Use formula from Leighton & Murray for surface temperature
        temperature_2 = model.temperature(1)
        temperature_3 = model.temperature(2)
        temperature = 3*temperature_2/2 - temperature_3/2

        radiation_loss=self.bolzmann(temperature)
 
        #Use formula from Leighton & Murray for surface heat flow
        temperature_difference = temperature_2 - temperature
        distance = below.thickness#0.5* 
        
        temperature_gradient= (temperature_difference / distance)        
        internal_inflow=self.planet.K * temperature_gradient

        total_inflow_before_latent_heat = irradiance - radiation_loss + internal_inflow
        if self.co2:
            self.update_temperature_adjust_for_co2(total_inflow_before_latent_heat,dT)
        else:
            self.update_temperature(total_inflow_before_latent_heat,dT)
        record.add(self.temperature)
        return internal_inflow
    
    def bolzmann(self,t):
        '''Loss of energy through radiation'''
        return self.emissivity()*physics.Radiation.bolzmann(t)
 
    def absorption(self):
        '''Calculate absorbed energy, assuming frozen CO2 affects albedo'''
        if self.total_co2>0:
            return 1-physics.CO2.albedo
        else:        
            return self.planet.F  
    
    def emissivity(self):
        '''Emissivity of surface'''
        return self.planet.E   # TODO co2
    
    def sublimate_co2(self,total_inflow_before_latent_heat):
        '''
        Sublimate CO2
        
        Parameters:
            total_inflow_before_latent_heat
            
        Returns:
            temperature inflow (subtract latent heat)
        '''
        if self.total_co2>0:
            self.total_co2-=abs(total_inflow_before_latent_heat)/physics.CO2.latent_heat
            if self.total_co2>0:
                return 0
            else:
                balance=abs(self.total_co2)*physics.CO2.latent_heat
                self.total_co2=0
                return balance
        else:
            return total_inflow_before_latent_heat

    def co2_is_available(self):
        '''Indicates whther there is CO2 available to freeze (currently unlimited)'''
        return True
    
    def freeze_co2(self,total_inflow_before_latent_heat):
        '''
        Freeze CO2
        
        Parameters:
            total_inflow_before_latent_heat
        '''
        self.total_co2+=abs(total_inflow_before_latent_heat)/physics.CO2.latent_heat
        return 0
    

class MedialLayer(Layer):
    '''Ordinary layers - exchanges heat with Layers above and below'''
    def __init__(self,latitude,thickness,planet,temperature):
        Layer.__init__(self,'Medial',latitude,thickness,planet,temperature)
        
    def propagate_temperature(self,above,below,true_longitude,T,dT,record,model):
        internal_inflow = self.heat_flow(above) + self.heat_flow(below)
        self.update_temperature(internal_inflow,dT)
        record.add(self.temperature)
        return internal_inflow
    
    
class Bottom(Layer):
    '''Bottom layer - exchanges heat with layer above only '''
    def __init__(self,layer):
        Layer.__init__(self,'Bottom',layer.latitude,layer.thickness,layer.planet,layer.temperature)
        
    def propagate_temperature(self,above,below,true_longitude,T,dT,record,model):
        internal_inflow = self.heat_flow(above)
        self.update_temperature(internal_inflow,dT)
        record.add(self.temperature)
        return internal_inflow


class ThermalModel:
    '''
    Model heat losses and gains by a Planet
    
    Attributes:
        layers         The Thermal Model is a collection of Layers
        planet         The planet that we are modelling
        history        Used to log evolution of temperatures 
        record         Used to log evolution of temperatures
        zipper_layers  A colection of triplets of layers so we can calculate
                       heat flows between one layer and its neighbours
    '''
    @staticmethod 
    def stable_temperature(solar,planet,proportion=0.25):
        '''
        Used at start of iterations to estimate stable temperature,
        unless user specifies a start
        
        Parameters:
            solar
            planet
            proportion
        '''
        beam_irradience=proportion * solar.beam_irradience(planet.a)
        return physics.Radiation.reverse_bolzmann(beam_irradience)    
    
    def __init__(self,latitude,spec,solar,planet,history,temperature,co2):
        '''
        Initialize model
        
        Parameters:
            latitude     The latitude for which we are performing calculations
            spec         Specification for layers. A list of the form
                         [(n1,thickness1),(n2,thickness2)...]
                         where n1 is the number of layers of thisckness 1, etc.
                         The list starts at the topmost layer
            solar        Solar model
            planet       The planet for which we are performing calculations
            history      Used to log evolution of temperatures 
            temperature  Starting temperature
            co2          Indicates whether we should include CO2 (sublimation
                         and condensation)
        '''
        self.layers=[]
        self.planet=planet
        (n,dz)=spec[0]
        self.layers.append(Surface(latitude,dz,solar,planet,temperature,co2))
        for (n,dz)in spec:
            for i in range(n):
                self.layers.append(MedialLayer(latitude,dz,planet,temperature))
        bottom=self.layers.pop()
        self.layers.append(Bottom(bottom))
        self.history=history
        self.record=None
        self.zipper_layers = list(utilities.slip_zip(self.layers))
 
    def temperature(self,index):
        return self.layers[index].temperature
    
    # Calculate heat transfer during one time step
    # Don't change temperatures until every Layer has been processed
    # otherwise energy won't be conserved, which would be a Very Bad Thing
    def propagate_temperature(self,true_longitude,T,dT):
        total__internal_inflow=0
        for above,layer,below in self.zipper_layers:
            total__internal_inflow+=layer.propagate_temperature(above,below,true_longitude,T,dT,self.record,self)
        #if abs(total__internal_inflow)>1.0e-6: print ('Total Internal Inflow {0}'.format(total__internal_inflow))
 
        for layer in self.layers:
            layer.temperature=layer.new_temperature
     
    # Calculate heat transfer during all time steps      
    # parameters:
    #    start_day
    #    number_of_days
    #    number_of_steps_in_hour
    def runModel(self,start_day,number_of_days,number_of_steps_in_hour):
        hours_in_day=24
        step_size = 3600/float(number_of_steps_in_hour) 
        for day,hour,_,step,_,_,_,_,_,true_longitude in steps(0,number_of_days,10,self.planet):
            self.record = utilities.TemperatureRecord(day,hour,hours_in_day,true_longitude)
            self.propagate_temperature(true_longitude,hour,step_size)
            if step==0:
                self.history.add(self.record)

def steps(start_day,number_of_days,number_of_steps_in_hour,planet):
    '''
    Generator for iterating over time steps
    
    for day,hour,hour_with_step,step,time,M,E,nu,r,true_longitude in steps(...):
    
    '''
    days_in_year=planet.get_my_days_in_year()
    hours_in_day=24
    step_size = 3600/float(number_of_steps_in_hour)        
    for day in range(start_day,start_day+number_of_days):
        for hour in range(24):
            for step in range(number_of_steps_in_hour):
                hour_with_step=hour+step/number_of_steps_in_hour
                day_with_hour_and_step = day + hour_with_step/24
                time=day_with_hour_and_step*360/days_in_year
                M = k.get_mean_anomaly(1,math.radians(time))
                E = k.get_eccentric_anomaly(M,planet.e)
                nu = k.get_true_anomaly(E,planet.e)
                r = k.get_distance_from_focus(nu,planet.a,planet.e)
                true_longitude= k.true_longitude_from_true_anomaly(nu,PERH=planet.longitude_of_perihelion)              
                yield (day,hour,hour_with_step,step,time,M,E,nu,r,true_longitude)
                
if __name__=='__main__':
        
    import matplotlib.pyplot as plt
    
    mars = planet.create('Mars')
    solar = s.Solar(mars)
        
    history = utilities.InternalTemperatureLog()    
    thermal=ThermalModel(10,[(9,0.015),(10,0.3)],solar,mars,history,225.9,False)
    
    thermal.runModel(0,1440,10)

    (days,surface_temp) = history.extract(0)
    print (days,surface_temp)
    (_,t1) = history.extract(1)
    (_,t2) = history.extract(2)
    (_,t3) = history.extract(3)
    (_,t4) = history.extract(4)
    (_,t5) = history.extract(5)
    (_,t6) = history.extract(10)
    (_,t7) = history.extract(19)
    plt.plot(days,surface_temp,'r-',days,t1,'g-',days,t2,'b-',days,t3,'c-',days,t4,'m-',days,t5,'y-',days,t6,'b-',days,t7,'b-')
    plt.show()
