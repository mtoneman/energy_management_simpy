from datetime import datetime,timedelta
from energymanagement import generators,consumers,emutils
import simpy
import csv
import pandas as pd

RANDOM_SEED = 42

BATTERY_CAPACITY_KWH = 5000
BATTERY_START_KWH = 3000

FRESHWATER_CAPACITY_L = 10000
FRESHWATER_START_L = 6000

SIM_TIME = 60*24*15 # Simulation time in minutes, 15 days

start_time = 0

#compliment {"crew_only","crew_and_owner", "full_charter"}
#current_passengers = "full_charter"

schedule = []
forecast = []
energy = []


def use_freshwater(env, freshwater_tank):
    """Simulate water use"""
    freshwater_use_lph = {"crew_only" : 200, "crew_and_owner": 350, "full_charter": 1000}
    while True:
        compliment = schedule[emutils.row_at_time(env.now, schedule)]["compliment"]
 
        # daylight hours only
        time_now = emutils.time_at_minute(env.now, start_time) 
        factor = 1
        if(time_now.hour < 6):
            factor = 0.2
        elif(time_now.hour < 9):
            factor = 1
        elif(time_now.hour < 17):
            factor = 0.6
        elif(time_now.hour < 22):
            factor = 1
        else:
            factor = 0.2

        freshwater_tank.get(freshwater_use_lph[compliment] * factor)
        #print('fresh water at %d' % (freshwater_tank.level))
        yield env.timeout(60)

def es(env, energy, start_time):
    while True:
        reporting_cycle = 60
        yield env.timeout(reporting_cycle)
        energy.append({"date": start_time + timedelta(minutes=env.now), "batterylevel": battery.level, "freshwaterlevel": freshwater_tank.level, "solarenergy": solar.level, 
           "energylevel": ((battery.level/BATTERY_CAPACITY_KWH)*9 + (freshwater_tank.level/FRESHWATER_CAPACITY_L) *1)  * 100/10 })        
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
battery = simpy.Container(env, BATTERY_CAPACITY_KWH, init=BATTERY_START_KWH)
freshwater_tank = simpy.Container(env, FRESHWATER_CAPACITY_L, init=FRESHWATER_START_L)

fwg = simpy.Resource(env, capacity=1)

#consumers
env.process(es(env, energy, start_time))
env.process(consumers.laundry_scheduler(env, schedule, battery))
env.process(use_freshwater(env, freshwater_tank))
env.process(consumers.generate_freshwater(env, freshwater_tank, battery))
env.process(consumers.undefined_load(env, schedule, battery))

#generators
env.process(generators.solar_egeneration(env, schedule, start_time, forecast, battery, BATTERY_CAPACITY_KWH, solar))
env.process(generators.drag_egeneration(env, schedule, battery, BATTERY_CAPACITY_KWH))

env.run(until=SIM_TIME)
df = pd.DataFrame(energy)
df.to_csv("energy.csv")


