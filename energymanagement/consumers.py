from energymanagement import emutils


def undefined_load(env, schedule, battery):
    """Placeholder Electrical Load Simulator"""
    undefined_load_kWh = {"crew_only" : 30, "crew_and_owner": 40, "full_charter": 70}
    while True:
        compliment = schedule[emutils.row_at_time(env.now, schedule)]["compliment"]
        battery.get(undefined_load_kWh[compliment]/4)
        yield env.timeout(15)

def laundry_cycle(env, battery, cycle_time):
    #print('starting a laundry cycle of %d minutes at %.2f.' % (cycle_time, env.now))
    yield env.timeout(cycle_time/2)
    battery.get(4) # washing cycle uses 4kWh
    yield env.timeout(cycle_time/2)
    battery.get(5) # drying cycle uses 5kWh
    #print('finished the laundry cycle at %.2f.' % (env.now))



def laundry_scheduler(env, schedule, battery):
    yield env.timeout(17) #small offset for prettier graph
    """Schedule laundry cycles"""
    cycle_time = 180
    cycle_schedule_hours = {"crew_only" : 48, "crew_and_owner": 24, "full_charter": 12}
    while True:
        compliment = schedule[emutils.row_at_time(env.now, schedule)]["compliment"]
        next_cycle = 60 * cycle_schedule_hours[compliment] - cycle_time
        #print('schedule next laundry cycle for %s in %d minutes' % (compliment,next_cycle))
        env.process(laundry_cycle(env, battery, cycle_time))
        yield env.timeout(next_cycle)
