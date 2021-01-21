#!/usr/bin/env python3

import sys, os
from datetime import datetime,timedelta
from energymanagement import generators,consumers,freshwater,emutils,db
from fileimport import forecast,schedule
import simpy
import csv
import json
import pandas as pd

pathname = os.path.dirname(sys.argv[0])
DATA_DIR = f"{os.path.abspath(pathname)}/data"

conn = db.create_connection(f"{DATA_DIR}/energymanagement.db")
configuration = db.resultset_to_dict(db.select(conn,"select_configuration", []))

print (json.dumps(configuration, indent=2))

RANDOM_SEED = 42
energy = []

def es(env, energy, start_time):
    while True:
        reporting_cycle = 60
        yield env.timeout(reporting_cycle)
        energy.append({"date": start_time + timedelta(minutes=env.now), "batterylevel": battery.level, 
	   "freshwaterlevel": freshwater_tank.level, "solarenergy": solar.level, 
           "energylevel": ((battery.level/configuration['BATTERY_CAPACITY_KWH'])*9 
	       + (freshwater_tank.level/configuration['FRESHWATER_CAPACITY_L']) *1)  * 100/10 })        
        #print('\t Battery level at %d kWh at %d' %  (battery.level,env.now ))
        slevel = solar.level
        if slevel != 0:
            solar.get(slevel)

start_time, schedule = schedule.process('plan.csv')
forecast = forecast.process('forecast.csv', start_time)

env = simpy.Environment()

solar = simpy.Container(env, 100000000, init=0)
battery = simpy.Container(env, configuration['BATTERY_CAPACITY_KWH'], init=configuration['BATTERY_START_KWH'])
freshwater_tank = simpy.Container(env, configuration['FRESHWATER_CAPACITY_L'], init=configuration['FRESHWATER_START_L'])

fwg = simpy.Resource(env, capacity=1)

#consumers
env.process(es(env, energy, start_time))
env.process(consumers.laundry_scheduler(env, schedule, battery))
env.process(consumers.undefined_load(env, schedule, battery))

#generators
env.process(generators.solar_egeneration(env, schedule, start_time, forecast, battery, configuration['BATTERY_CAPACITY_KWH'], solar))
env.process(generators.drag_egeneration(env, schedule, battery, configuration['BATTERY_CAPACITY_KWH']))

#freshwater
env.process(freshwater.use_freshwater(env, schedule, start_time, freshwater_tank))
env.process(freshwater.generate_freshwater(env, freshwater_tank, battery))

env.run(until=configuration['SIM_TIME'])
df = pd.DataFrame(energy)
df.to_csv("energy.csv")


