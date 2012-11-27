from datetime import datetime
from math import ceil, trunc

def friendly_display(date):
    delta = date - datetime.now()

    minutes = trunc(ceil(delta.seconds/60.0))
    hours = trunc(round(minutes / 60.0))

    if delta.days < 0:
        return "now"
    elif delta.days > 1:
        days = delta.days
        
        if hours > 12:
            days += 1

        return "in %s days" % days
    elif delta.days == 0:
        if hours > 12:
            return "tomorrow"

        if minutes >= 60 and hours == 1:
            return "in an hour"
        elif hours > 1:
            return "in %s hours" % hours

        return "in %s minutes" % trunc(ceil(delta.seconds/60.0))