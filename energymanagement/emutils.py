from datetime import timedelta

def row_at_time(time, table):
    timelist = [li["minutes"] for li in table]
    timelist.append(1000000000)

    # using enumerate() + next() to find index of
    # first element just greater than time
    res = next(x for x, val in enumerate(timelist) if val > time) - 1

    return max(0,res);


def time_at_minute(minutes, starttime):
    return starttime + timedelta(minutes=minutes)
