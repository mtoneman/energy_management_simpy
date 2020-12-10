from datetime import datetime,timedelta
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

def row_at_time(time, table):
    timelist = [li["minutes"] for li in table]
    timelist.append(1000000000)
  
    # using enumerate() + next() to find index of 
    # first element just greater than time  
    res = next(x for x, val in enumerate(timelist) if val > time) - 1 

    return max(0,res);

def time_at_minute(minutes, starttime):
    return starttime + timedelta(minutes=minutes)

def generate_freshwater(env, freshwater_tank):
    yield env.timeout(21) #small offset for prettier graph
    while True:
        yield env.timeout(30)
        if freshwater_tank.level < 2000:
            #print('starting a freshwater generation cycle at %.2f.' % (env.now))
            while freshwater_tank.level < 9000:
                freshwater_tank.put(1000) # 5Wh per liter
                battery.get(5)
                yield env.timeout(30)

def laundry(env, battery, cycle_time):
    #print('starting a laundry cycle of %d minutes at %.2f.' % (cycle_time, env.now))
    yield env.timeout(cycle_time/2)
    battery.get(4) # washing cycle uses 4kWh 
    yield env.timeout(cycle_time/2)
    battery.get(5) # drying cycle uses 5kWh 
    #print('finished the laundry cycle at %.2f.' % (env.now))

def use_freshwater(env, freshwater_tank):
    """Simulate water use"""
    freshwater_use_lph = {"crew_only" : 200, "crew_and_owner": 350, "full_charter": 1000}
    while True:
        compliment = schedule[row_at_time(env.now, schedule)]["compliment"]
 
        # daylight hours only
        time_now = time_at_minute(env.now, start_time) 
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

def solar_egeneration(env, battery):
    """Simulate solar e-generation"""
    yield env.timeout(9) #small offset for prettier graph
    power_generated_ph = 12 # average for 12 daylight hours
    while True:
        yield env.timeout(60)
        power_gen = power_generated_ph 

        # sailing reduces the effective power to 60%
        activity = schedule[row_at_time(env.now, schedule)]["activity"]
        if(activity == "sailing"):
            power_gen = power_gen * 0.6

        # factor in the forecast solar energy
        solar_energy = float(forecast[row_at_time(env.now, forecast)]["solar_energy"])
        power_gen = power_gen * (min(solar_energy,5.0) / 5.0)

        # daylight hours only
        time_now = time_at_minute(env.now, start_time) 
        if(time_now.hour < 7 or time_now.hour > 19):
            power_gen = 0

	# daylight cycle
        power_gen = power_gen * (3 - (abs(13 - time_now.hour)* abs(13 - time_now.hour)) / 12)

        if(power_gen > 0):
            solar.put(power_gen)

        if power_gen > 0 and battery.level < (BATTERY_CAPACITY_KWH - power_gen):
            #print('solar panels generated %f at %s' % (power_gen, time_now))
            battery.put(power_gen)


def drag_egeneration(env, battery):
    """Simulate drag e-generation"""
    yield env.timeout(7) #small offset for prettier graph
    power_generated_ph = 100
    while True:
        yield env.timeout(60)
        activity = schedule[row_at_time(env.now, schedule)]["activity"]
        if activity == 'sailing' and battery.level < (BATTERY_CAPACITY_KWH - power_generated_ph):
            battery.put(power_generated_ph)


def laundry_scheduler(env, battery):
    yield env.timeout(17) #small offset for prettier graph
    """Schedule laundry cycles"""
    cycle_time = 180
    cycle_schedule_hours = {"crew_only" : 48, "crew_and_owner": 24, "full_charter": 12}
    while True:
        compliment = schedule[row_at_time(env.now, schedule)]["compliment"]
        next_cycle = 60 * cycle_schedule_hours[compliment] - cycle_time
        #print('schedule next laundry cycle for %s in %d minutes' % (compliment,next_cycle))
        env.process(laundry(env, battery, cycle_time))
        yield env.timeout(next_cycle)

def undefined_load(env, battery):
    """Placeholder Electrical Load Simulator"""
    undefined_load_kWh = {"crew_only" : 30, "crew_and_owner": 40, "full_charter": 70}
    while True:
        compliment = schedule[row_at_time(env.now, schedule)]["compliment"]
        battery.get(undefined_load_kWh[compliment]/4)
        yield env.timeout(15)


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
env.process(laundry_scheduler(env, battery))
env.process(use_freshwater(env, freshwater_tank))
env.process(generate_freshwater(env, freshwater_tank))
env.process(undefined_load(env, battery))

#generators
env.process(solar_egeneration(env, battery))
env.process(drag_egeneration(env, battery))

env.run(until=SIM_TIME)
df = pd.DataFrame(energy)
df.to_csv("energy.csv")


