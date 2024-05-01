def minutes_till_midnight():
    from datetime import datetime
    import pytz

    berlin_tz = pytz.timezone('Europe/Berlin')
    now = datetime.now(berlin_tz)
    end_of_day = berlin_tz.localize(datetime(now.year, now.month, now.day, 23, 59, 59))
    remaining_time = end_of_day - now
    return remaining_time.seconds // 60