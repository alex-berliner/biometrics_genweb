from collections import OrderedDict
import plotly.graph_objs as go
from plotly.offline import plot
import pytz
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import csv
from grapher import *


"""
time,rating
1532451612,20.0
1532466747,0.0
1532468258,0.0
1532470355,0.0
"""

class HeadacheDay():
    def __init__(self, date, rate):
        self.date = date
        self.rate = rate
    def __str__(self):
        return "%s %s" % (str(self.date), (self.rate))

def consolidate_events(events):
    if not any(events):
        return

    maxnight = datetime.combine(events[0].date, datetime.max.time())
    events += [HeadacheDay(maxnight, -1)]
    conditions = []
    for i in range(len(day_accu)-1):
        day = day_accu[i]
        next_day = day_accu[i+1]
        conditions += [((next_day.date - day.date).seconds, day.rate)]
        # print((next_day.date - day.date).seconds, day.rate)

    total_time = sum([x[0] for x in conditions])
    final_rate = 0
    for condition in conditions:
        final_rate += condition[0]/total_time * condition[1]

    midnight = datetime.combine(events[0].date, datetime.min.time())
    return HeadacheDay(midnight, final_rate)

headache_filename = "../biometrics/data/headache.csv"
med_event_filename = "../biometrics/data/med_events.csv"
def get_headache_days():
    global day_accu

    rows = []
    with open(headache_filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            rows.append(row)

    headache_events = []
    for row in rows[1:]:
        date = datetime.fromtimestamp(int(row[0]))
        rate = float(row[1])/100
        day = HeadacheDay(date, rate)
        headache_events += [day]

    headache_days = []
    current_day = -1
    day_accu = []
    for event in headache_events:
        # flush day_accu, consolidate into single day
        if current_day != event.date.day:
            ret = consolidate_events(day_accu)
            if ret is not None:
                headache_days += [ret]
            day_accu = []
            current_day = event.date.day
        day_accu += [event]
    return headache_days

def get_med_events():
    df = pd.read_csv(med_event_filename)
    # convert to timestamps
    df['date'] = pd.to_datetime(df['time'], unit="s")
    df = df.drop("time", axis="columns")
    # localize to pacific
    df['date'] = pd.DatetimeIndex(df['date']).tz_localize('UTC').tz_convert('US/Pacific')

    ts1 = datetime(2020, 10, 1, tzinfo=pytz.timezone("US/Pacific"))
    ts2 = ts1+relativedelta(months=1)

    mask = (df['date'] >= ts1) & (df['date'] < ts2)
    subframe = df.loc[mask]

    return df

headache_days = get_headache_days()
med_events = get_med_events()

days = OrderedDict()

for day_iter in headache_days:
    days[day_iter.date.date()] = [day_iter]

# combine headache and med events into |days|
for i in range(len(med_events)):
    date = datetime.fromtimestamp(int(med_events["date"][i].timestamp())).date()
    if date in days:
      days[date] += [med_events["med_events"][i]]
    else:
      days[date] = [med_events["med_events"][i]]

# create GraphData's out of |days|
runner = datetime(2017, 11, 1).date()
delta  = relativedelta(months=1)
graphs2 = []
while runner < datetime.now().date():
    keys = sorted([x for x in days if x >= runner and x < (runner + delta)])
    if len(keys) < 1:
        runner += delta
        continue
    graphs2 += [GraphData("Headache Intensity")]
    for date in keys:
        day = days[date]
        annotations = []
        for event in day:
            if isinstance(event, HeadacheDay):
                graphs2[-1].graph_dates    += [event.date]
                graphs2[-1].graph_percents += [event.rate]
        for event in day:
            if isinstance(event, str):
                annotations += [event.replace(" mg", "mg").replace(" ", "<br>") + "<br>==="]
        if any(annotations):
            graphs2[-1].annotation_dates += [date]
            graphs2[-1].annotation_text  += ["<br>".join(annotations).rstrip("===")]
        # print("\n".join(annotations).strip())
        # print(annotations)

    runner += delta

# current_month = -1
# graphs = []
# for day_iter in headache_days:
#     # create new month field
#     if current_month != day_iter.date.month:
#         current_month = day_iter.date.month
#         # TODO populate name better
#         graphs += [GraphData("Headache Intensity")]
#     # add day data to month
#     graphs[-1].graph_dates    += [day_iter.date]
#     graphs[-1].graph_percents += [day_iter.rate]

# # add "last month"
# month_ago = datetime.now() - relativedelta(months=1)
# graphs += [GraphData("Headache Intensity 0-1 scale")]
# for day_iter in reversed(headache_days):
#     graphs[-1].graph_dates    += [day_iter.date]
#     graphs[-1].graph_percents += [day_iter.rate]
#     if month_ago > day_iter.date:
#         break

# graphs[-1].graph_dates.reverse()
# graphs[-1].graph_percents.reverse()

html = HeadacheHtmlBuilder(graphs2)
html.gen_page()
