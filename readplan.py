import sys, os
from datetime import datetime,timedelta
from energymanagement import generators,consumers,freshwater,emutils,db
import simpy
import csv
import pandas as pd



pathname = os.path.dirname(sys.argv[0])
DATA_DIR = f"{os.path.abspath(pathname)}/data"

conn = db.create_connection(f"{DATA_DIR}/energymanagement.db")
configuration = db.resultset_to_dict(db.select(conn,"select_configuration", []))

print(configuration)

RANDOM_SEED = 42
start_time = 0

schedule = []
forecast = []
energy = []

def es(env, energy, start_time):
    while True:
        reporting_cycle = 60
        yield env.timeout(reporting_cycle)
        energy.append({"date": start_time + timedelta(minutes=env.now), "batterylevel": battery.level, "freshwaterlevel": freshwater_tank.level, "solarenergy": solar.level, 
           "energylevel": ((battery.level/configuration['BATTERY_CAPACITY_KWH'])*9 + (freshwater_tank.level/configuration['FRESHWATER_CAPACITY_L']) *1)  * 100/10 })        
        #print('\t Battery level at %d kWh at %d' %  (battery.level,env.now ))
        slevel = solar.level
        if slevel != 0:
            solar.get(slevel)

with open('plan.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        if line_count == 1:
            start_time = datetime.fromisoformat(row["datetime"]);
            print(f'\tstart time {start_time}')
        #print(f'\tRow {line_count} at date {row["datetime"]}: {row["activity"]} at/to {row["destination_city"]},{row["destination_country"]}.')
        row_time = datetime.fromisoformat(row["datetime"])
        schedule_row = {"minutes":(row_time - start_time).total_seconds()/60,"compliment":row["compliment"],"activity":row["activity"],"destination_city":row["destination_city"],"destination_country":row["destination_country"]}
        print(schedule_row)
        schedule.append(schedule_row)
        line_count += 1
    print(f'Processed {line_count} lines.')
 
with open('forecast.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    format_str = '%m/%d/%Y %H:%M:%S' # the Date Time format
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        row_time = datetime.strptime(row["Date time"], format_str)
        #print((row_time - start_time).total_seconds()/60)
        forecast_row = {"minutes":(row_time - start_time).total_seconds()/60,"location":row["Name"],"wind_direction":row["Wind Direction"],"solar_energy":row["Solar Energy"],"cloud_cover":row["Cloud Cover"],"wind_speed":row["Wind Speed"]}
        print(forecast_row)
        forecast.append(forecast_row)
        line_count += 1
    print(f'Processed {line_count} lines.')
        
       

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


