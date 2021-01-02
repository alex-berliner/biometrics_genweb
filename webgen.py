import csv
import os
import pandas as pd
import plotly.graph_objs as go
import pytz
from collections import OrderedDict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from grapher import *
from plotly.offline import plot

headache_filename  = os.environ["BIOMETRICS_ROOT"] + "/biometrics/data/headache.csv"
med_event_filename = os.environ["BIOMETRICS_ROOT"] + "/biometrics/data/med_events.csv"

class HeadacheDay():
    def __init__(self, date, rate, htype):
        self.date = date
        self.rate = rate
        self.htype = htype
    def __str__(self):
        return "%s %s" % (str(self.date), (self.rate))

class AimovigLevel():
    def __init__(self, date, rate):
        self.date = date
        self.rate = rate
    def __str__(self):
        return "%s %s" % (str(self.date), (self.rate))

# height of the current bar graph text
height_counter = None
def gen_graph(graphs, days):
    global height_counter
    if height_counter is None:
        height_counter = 0
    keys = sorted([x for x in days])
    graphs += [GraphData("Headache Intensity")]
    for date in keys:
        day = days[date]
        annotations = []
        # print(day)
        for event in day:
            if isinstance(event, HeadacheDay) and event.htype == "headache":
                graphs[-1].graph_dates    += [event.date]
                graphs[-1].graph_percents += [event.rate]
            elif isinstance(event, HeadacheDay) and event.htype == "headache_min":
                graphs[-1].min_graph_dates    += [event.date]
                graphs[-1].min_graph_percents += [event.rate]
        for event in day:
            if isinstance(event, str):
                annotations += [event.replace(" mg", "mg").replace(" ", "<br>") + "<br><br>"]
        for event in day:
            if isinstance(event, AimovigLevel):
                graphs[-1].aimovig_level_dates    += [event.date]
                graphs[-1].aimovig_level_percents += [event.rate]
        if len(annotations) > 0:
            graphs[-1].annotation_dates += [date]
            graphs[-1].annotation_text  += ["<br>".join(annotations).rstrip("<br>") + "<br> "*height_counter]
            height_counter = (height_counter + 3)%15


def get_headache_days():
    # consolidate events in one day into single event
    def consolidate_headache_events(day_accu):
        if len(day_accu) < 1:
            return

        maxnight = datetime.combine(day_accu[0].date, datetime.max.time())
        # maxnight = pytz.timezone("US/Pacific").localize(maxnight)
        day_accu += [HeadacheDay(maxnight, -1, "headache")]
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

        midnight = datetime.combine(day_accu[0].date, datetime.min.time())
        return HeadacheDay(midnight, final_rate, "headache")
    rows = []
    with open(headache_filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            rows.append(row)

    headache_events = []
    for row in rows[1:]:
        date = datetime.fromtimestamp(int(row[0]))
        rate = float(row[1])/100
        day = HeadacheDay(date, rate, "headache")
        headache_events += [day]
    headache_days = []
    current_day = -1
    day_accu = []

    runner = datetime(2017, 1, 1)
    d = relativedelta(days=1)
    while runner < datetime.now():
        t1 = runner
        t2 = runner + d
        selection = [x for x in headache_events if t1 <= x.date and x.date < t2]
        runner += d
        if len(selection) > 0:
            ret = consolidate_headache_events(selection)
            headache_days += [ret]

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

# look for AimovigLevel container in list
# made because storing AimovigLevel class in list with multiple data types
def find_aimovig_level(the_list):
    return [x for x in the_list if isinstance(x, AimovigLevel)][-1]

# perform 20 day running average on headache data
def create_running_average_headache_days(headache_function, htype):
    # split rate values out of headache events, average them, then insert back into headache events
    headache_days = headache_function()
    day_average = 20.0
    avgq=[]
    hen = []
    # make array of rates from events, then make averages
    dayvals = [x.rate for x in headache_days]
    for e in dayvals:
        avgq.append(e)
        if len(avgq) > day_average:
            avgq = avgq[1:]
        hen += [float(sum(avgq)/day_average)]

    # replace average data with raw data for last 120 days
    raw_count = 120
    last_x = dayvals[-raw_count:]
    hen[-raw_count:] = last_x
    # splice back into events
    for i in range(len(hen)):
        headache_days[i].rate = hen[i]

    return headache_days

def get_headache_min_days():
    # consolidate events in one day into single event
    def minimize_headache_events(day_accu):
        if len(day_accu) < 1:
            return

        maxnight = datetime.combine(day_accu[0].date, datetime.max.time())
        # maxnight = pytz.timezone("US/Pacific").localize(maxnight)
        day_accu += [HeadacheDay(maxnight, -1, "headache_min")]
        conditions = []
        for i in range(len(day_accu)-1):
            day = day_accu[i]
            next_day = day_accu[i+1]
            conditions += [((next_day.date - day.date).seconds, day.rate)]
            # print((next_day.date - day.date).seconds, day.rate)

        total_time = sum([x[0] for x in conditions])
        final_rate = min([x[1] for x in conditions])

        midnight = datetime.combine(day_accu[0].date, datetime.min.time())
        return HeadacheDay(midnight, final_rate, "headache_min")

    rows = []
    with open(headache_filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            rows.append(row)

    headache_events = []
    for row in rows[1:]:
        date = datetime.fromtimestamp(int(row[0]))
        rate = float(row[1])/100
        day = HeadacheDay(date, rate, "headache_min")
        headache_events += [day]
    headache_days = []
    current_day = -1
    day_accu = []

    runner = datetime(2017, 1, 1)
    d = relativedelta(days=1)
    while runner < datetime.now():
        t1 = runner
        t2 = runner + d
        selection = [x for x in headache_events if t1 <= x.date and x.date < t2]
        runner += d
        if len(selection) > 0:
            ret = minimize_headache_events(selection)
            headache_days += [ret]

    return headache_days

def main():
    headache_days = create_running_average_headache_days(get_headache_days, "headache")
    min_headache_days = create_running_average_headache_days(get_headache_min_days, "headache_min")
    med_events = get_med_events()

    days = OrderedDict()
    for day_iter in headache_days:
        days[day_iter.date.date()] = [day_iter]

    for day_iter in min_headache_days:
        days[day_iter.date.date()] += [day_iter]
        # print(days[day_iter.date.date()])

    # combine headache and med events into |days|
    for i in range(len(med_events)):
        date = datetime.fromtimestamp(int(med_events["date"][i].timestamp())).date()
        if date in days:
            days[date] += [med_events["med_events"][i]]
        else:
            days[date] = [med_events["med_events"][i]]

    # beginning of time
    daterange = pd.date_range(datetime(2018,9,5), datetime.now().date()+relativedelta(months=2))
    mglevel = 0
    hl = 28.0
    days_since_update = 0.0

    for d in daterange:
        d = d.date()
        # print(d)
        aimovig_count = None
        aimstr=""
        days_since_update += 1
        if d not in days:
            aimovig_level = round(mglevel * (0.5 ** (days_since_update/hl)))
            days[d] = [AimovigLevel(d, aimovig_level)]
            continue

        for e in days[d]:
            if isinstance(e, str) and  "aimovig" in e:
                aimovig_count = 70 if ("fail" in e or "70" in e) else 140
                aimstr = e
                break
        if aimovig_count:
            mglevel = aimovig_count + mglevel * (0.5 ** (days_since_update/hl))
            days_since_update = 0
        aimovig_level = round(mglevel * (0.5 ** (days_since_update/hl)))
        days[d] += [AimovigLevel(d, aimovig_level)]

    latest = []

    graphs_accu = []
    # used for text only
    gen_graph(graphs_accu, days)

    # used for graph and text
    gen_graph(latest, days)
    if len(latest) > 1:
        print("Too many in latest")
        exit()
    else:
        latest[-1].is_latest = True
        graphs_accu += latest

    html = HeadacheHtmlBuilder(graphs_accu)
    html.gen_page()


if __name__ == "__main__":
    main()
