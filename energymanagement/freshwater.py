from energymanagement import emutils

def use_freshwater(env, schedule, start_time, freshwater_tank):
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


def generate_freshwater(env, freshwater_tank, battery):
    yield env.timeout(21) #small offset for prettier graph
    while True:
        yield env.timeout(30)
        if freshwater_tank.level < 2000:
            #print('starting a freshwater generation cycle at %.2f.' % (env.now))
            while freshwater_tank.level < 9000:
                freshwater_tank.put(1000) # 5Wh per liter
                battery.get(5)
                yield env.timeout(30)

