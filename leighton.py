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

'''Driver program for Leighton & Murray simulation'''
import thermalmodel, planet, solar, utilities, sys,getopt, string, physics, math

def help():
      '''Generate help text for user'''
      print (
            ('python leighton.py -o <outputfile> -f <hour from> '
             '-t <hour to> -l <latitude> -s <steps per hour> '
             '-m <initial temperature> -c -p <spec for layers>')
      )

def display_and_record(message,history):
      '''Display a message and log it'''
      print (message)
      history.write(message)


def get_output_file_name(from_date,to_date,latitude,temperature,co2):
      '''if output file not specified, choose name
      based on command line paremeters'''
      (ns,lat)=utilities.format_latitude(latitude)
      co2s = 'co2' if co2 else 'noco2'
      return '{0:d}-{1:d}-{2:d}-{3:s}-{4:.0f}{5:s}.txt'.format(
            from_date,to_date,int(temperature),co2s,lat,ns).strip()      

def main(argv):
      '''Execute the model'''
      outputfile  = ''
      from_date   = 0
      to_date     = 720
      latitude    = 0
      step        = 10
      temperature = -1
      co2         = True
      spec        = [(9,0.015),(10,0.3)]
      
      if len(argv)>0:
            try:
                  opts, args = getopt.getopt( \
                        argv,\
                        'ho:f:t:l:s:m:p:c',\
                        ['ofile=','from','to','latitude','step','temperature','co2','spec'])
            except getopt.GetoptError:
                  help()
                  sys.exit(2)
            for opt, arg in opts:
                  if opt == '-h':
                        help()
                        sys.exit()
                  elif opt in ('-o', '--ofile'):
                        outputfile = arg
                  elif opt in ('-f', '--from'):
                        from_date=int(arg)
                  elif opt in ('-t', '--to'):
                        to_date=int(arg)
                  elif opt in ('-l','--latitude'):
                        latitude=float(arg)
                  elif opt in ('-s','--step'):
                        step=int(arg)                  
                  elif opt in ('-m','--temperature'):
                        temperature=int(arg)
                  elif opt in ('-c','co2'):
                        co2=False
                  elif opt in ('-p','spec'):
                        spec=[]
                        for run in arg.strip('[]').split(';'):
                              try:
                                    couple=run.strip('()').split(',')
                                    spec.append((int(couple[0]),float(couple[1])))
                              except ValueError:
                                    print ('Could not parse {0}'.format(run))
                                    sys.exit(2)

      mars = planet.create('Mars')

      solar_model = solar.Solar(mars)     
      
      # If user doesn't specify starting temperature, use stable value
      stableTemperatureSpecified = temperature<0
      if stableTemperatureSpecified:
            temperature=thermalmodel.ThermalModel.stable_temperature(solar_model,mars)
           
      if outputfile=='': 
            outputfile=get_output_file_name(from_date,to_date,latitude,temperature,co2)

      print('Outputting to {0}'.format(outputfile))
      
      with open(outputfile, 'w') as f:
            history = utilities.ExternalTemperatureLog(f)
            display_and_record('Semimajor axes       = {0:10.7f} AU'.format(mars.a),history)
            display_and_record('Eccentricty          = {0:10.7f}'.format(mars.e),history)
            display_and_record('Obliquity            = {0:6.3f}'.format(mars.obliquity),history)
            display_and_record('Hours in Day         = {0:10.7f}'.format(mars.hours_in_day),history)
            display_and_record('Absorption Fraction  = {0:6.3f}'.format(mars.F),history)
            display_and_record('Emissivity           = {0:6.3f}'.format(mars.E),history)            
            display_and_record('Soil Conductivity    = {0:7.3f} W/M/K'.format(mars.K),history)
            display_and_record('Specific Heat        = {0:7.3f} J/Kg/K'.format(mars.C),history)
            display_and_record('Density              = {0:6.3f} Kg/M3'.format(mars.rho),history)         
            display_and_record('Latitude             = {0:6.1f}'.format(latitude),history)
            display_and_record('Step                 = {0:6.1f}'.format(step),history)
            
            if stableTemperatureSpecified:
                  display_and_record('Starting Temperature = {0:6.1f} K (stable temperature)'.format(temperature),history)
            else:
                  display_and_record('Starting Temperature = {0:6.1f} K'.format(temperature),history)
                  
            if co2:
                  display_and_record('Subliming and freezing CO2',history)
            else:
                  display_and_record('No CO2',history)
                  
            display_and_record('Layering (from top down)',history)
            for n,thickness in spec:
                  display_and_record('{0:d} layers, thickness {1:6.3f} metres each.'.format(n,thickness),history)
                  
            display_and_record('Albedo of snowcap    = {0:5.2f}'.format(physics.CO2.albedo),history)
           
            thermal=thermalmodel.ThermalModel(math.radians(latitude),
                                              spec,
                                              solar_model,
                                              mars,
                                              history,
                                              temperature,
                                              co2)
            thermal.runModel(from_date,to_date,step)
            
            history.close()
            
if __name__ == '__main__':
      main(sys.argv[1:])