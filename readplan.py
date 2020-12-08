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
#SIM_TIME = 60 # Simulation time in minutes, ten days

start_time = 0
battery_level = BATTERY_START_KWH

#compliment {"crew_only","crew_and_owner", "full_charter"}
#current_passengers = "full_charter"
schedule = []
energy = []

def row_at_time(time, table):
    timelist = [li[0] for li in table]
    timelist.append(1000000000)
  
    # using enumerate() + next() to find index of 
    # first element just greater than time  
    res = next(x for x, val in enumerate(timelist) if val > time) - 1 

    return max(0,res);

def generate_freshwater(env, freshwater_tank):
    while True:
        yield env.timeout(30)
        if freshwater_tank.level < 2000:
            print('starting a freshwater generation cycle at %.2f.' % (env.now))
            while freshwater_tank.level < 9000:
                freshwater_tank.put(1000) # 5Wh per liter
                battery.get(5)
                yield env.timeout(30)

def laundry(env, battery, cycle_time):
    print('starting a laundry cycle of %d minutes at %.2f.' % (cycle_time, env.now))
    yield env.timeout(cycle_time/2)
    battery.get(4) # washing cycle uses 4kWh 
    yield env.timeout(cycle_time/2)
    battery.get(5) # drying cycle uses 5kWh 
    print('finished the laundry cycle at %.2f.' % (env.now))

def use_freshwater(env, freshwater_tank):
    """Simulate water use"""
    freshwater_use_lph = {"crew_only" : 200, "crew_and_owner": 350, "full_charter": 1000}
    while True:
        compliment = schedule[row_at_time(env.now, schedule)][1]
        freshwater_tank.get(freshwater_use_lph[compliment])
        print('fresh water at %d' % (freshwater_tank.level))
        yield env.timeout(60)

def drag_egeneration(env, battery):
    """Simulate drag e-generation"""
    power_generated_ph = 90
    while True:
        yield env.timeout(60)
        compliment = schedule[row_at_time(env.now, schedule)][2]
        #if compliment == 'sailing' and 100 * (battery.level / BATTERY_CAPACITY_KWH) < 80 and  battery.level < (BATTERY_CAPACITY_KWH - power_generated_ph):
        if compliment == 'sailing' and battery.level < (BATTERY_CAPACITY_KWH - power_generated_ph):
            battery.put(power_generated_ph)


def laundry_scheduler(env, battery):
    """Schedule laundry cycles"""
    cycle_time = 180
    cycle_schedule_hours = {"crew_only" : 48, "crew_and_owner": 24, "full_charter": 12}
    while True:
        compliment = schedule[row_at_time(env.now, schedule)][1]
        next_cycle = 60 * cycle_schedule_hours[compliment] - cycle_time
        print('schedule next laundry cycle for %s in %d minutes' % (compliment,next_cycle))
        env.process(laundry(env, battery, cycle_time))
        yield env.timeout(next_cycle)

def undefined_load(env, battery):
    """Placeholder Electrical Load Simulator"""
    undefined_load_kWh = {"crew_only" : 30, "crew_and_owner": 40, "full_charter": 80}
    while True:
        compliment = schedule[row_at_time(env.now, schedule)][1]
        battery.get(undefined_load_kWh[compliment]/4)
        yield env.timeout(15)


def es(env, energy, start_time):
    while True:
        reporting_cycle = 60
        yield env.timeout(reporting_cycle)
        energy.append({"date": start_time + timedelta(minutes=env.now), "batterylevel": battery.level, "freshwaterlevel": freshwater_tank.level, 
           "energylevel": ((battery.level/BATTERY_CAPACITY_KWH)*9 + (freshwater_tank.level/FRESHWATER_CAPACITY_L) *1)  * 100/10 })        
        print('\t Battery level at %d kWh at %d' %  (battery.level,env.now ))

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
        print(f'\tRow {line_count} at date {row["datetime"]}: {row["activity"]} at/to {row["destination_city"]},{row["destination_country"]}.')
        row_time = datetime.fromisoformat(row["datetime"])
        #print((row_time - start_time).total_seconds()/60)
        schedule.append([(row_time - start_time).total_seconds()/60,row["compliment"],row["activity"],row["destination_city"],row["destination_country"]])
        line_count += 1
    print(f'Processed {line_count} lines.')
        

env = simpy.Environment()

battery = simpy.Container(env, BATTERY_CAPACITY_KWH, init=BATTERY_START_KWH)
freshwater_tank = simpy.Container(env, FRESHWATER_CAPACITY_L, init=FRESHWATER_START_L)

fwg = simpy.Resource(env, capacity=1)

env.process(es(env, energy, start_time))
env.process(laundry_scheduler(env, battery))
env.process(use_freshwater(env, freshwater_tank))
env.process(generate_freshwater(env, freshwater_tank))
env.process(undefined_load(env, battery))

env.process(drag_egeneration(env, battery))

env.run(until=SIM_TIME)
df = pd.DataFrame(energy)
df.to_csv("energy.csv")


