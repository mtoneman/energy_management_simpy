from energymanagement import emutils


def drag_egeneration(env, schedule, start_time, battery, BATTERY_CAPACITY_KWH):
    """Simulate drag e-generation"""
    yield env.timeout(7) #small offset for prettier graph
    power_generated_ph = 150
    while True:
        yield env.timeout(60)
        power_gen = power_generated_ph

        activity = schedule[emutils.row_at_time(env.now, schedule)]["activity"]
        if activity == 'sailing' and battery.level < (BATTERY_CAPACITY_KWH - power_generated_ph):
            # daylight hours only
            time_now = emutils.time_at_minute(env.now, start_time)
            if(time_now.hour < 7 or time_now.hour > 19):
                power_gen = 0

            if(power_gen > 0):
                battery.put(power_gen)


def solar_egeneration(env, schedule, start_time, forecast, battery, BATTERY_CAPACITY_KWH, solar):
    """Simulate solar e-generation"""
    yield env.timeout(9) #small offset for prettier graph
    power_generated_ph = 12 # average for 12 daylight hours
    while True:
        yield env.timeout(60)
        power_gen = power_generated_ph

        # sailing reduces the effective power to 60%
        activity = schedule[emutils.row_at_time(env.now, schedule)]["activity"]
        if(activity == "sailing"):
            power_gen = power_gen * 0.6

        # factor in the forecast solar energy
        solar_energy = float(forecast[emutils.row_at_time(env.now, forecast)]["solar_energy"])
        power_gen = power_gen * (min(solar_energy,5.0) / 5.0)

        # daylight hours only
        time_now = emutils.time_at_minute(env.now, start_time)
        if(time_now.hour < 7 or time_now.hour > 19):
            power_gen = 0

        # daylight cycle
        power_gen = power_gen * (3 - (abs(13 - time_now.hour)* abs(13 - time_now.hour)) / 12)

        if(power_gen > 0):
            solar.put(power_gen)

        if power_gen > 0 and battery.level < (BATTERY_CAPACITY_KWH - power_gen):
            battery.put(power_gen)
            #print('solar panels generated %f at %s' % (power_gen, time_now))
 
def windkite_egeneration(env, schedule, start_time, forecast, battery, BATTERY_CAPACITY_KWH, windkite):
    """Simulate wind kite e-generation"""
    yield env.timeout(2) #small offset for prettier graph

    power_generated_ph = 200
    while True:
        yield env.timeout(60)
        power_gen = power_generated_ph

        activity = schedule[emutils.row_at_time(env.now, schedule)]["activity"]
        if activity == 'anchoring' and battery.level < (BATTERY_CAPACITY_KWH - power_generated_ph):
            # only for a few hours per day hours only
            time_now = emutils.time_at_minute(env.now, start_time)
            if(time_now.hour < 10 or time_now.hour > 16):
                power_gen = 0

            # factor in the forecast solar energy
            wind_speed = float(forecast[emutils.row_at_time(env.now, forecast)]["wind_speed"])
            # max / min wind speed for the kite
            #print('wind speed for kite: %f' % (wind_speed))
            if(wind_speed > 50 or  wind_speed < 8):
                power_gen = 0

            # wind power is wind speed cubed
            power_gen = power_gen * (wind_speed*wind_speed)/(50.0*50)

            if(power_gen > 0):
                windkite.put(power_gen)

            if power_gen > 0 and battery.level < (BATTERY_CAPACITY_KWH - power_gen):
                battery.put(power_gen)

