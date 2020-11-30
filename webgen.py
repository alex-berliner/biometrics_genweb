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
    def __init__(self, date, rate):
        self.date = date
        self.rate = rate
    def __str__(self):
        return "%s %s" % (str(self.date), (self.rate))

def gen_graph(graphs, start, delta, days):
    # create GraphData's out of |days|
    runner = start
    while runner < datetime.now().date():
        keys = sorted([x for x in days if x >= runner and x <= (runner + delta)])
        if len(keys) < 1:
            runner += delta
            continue
        graphs += [GraphData("Headache Intensity")]
        for date in keys:
            day = days[date]
            annotations = []
            for event in day:
                if isinstance(event, HeadacheDay):
                    graphs[-1].graph_dates    += [event.date]
                    graphs[-1].graph_percents += [event.rate]
            for event in day:
                if isinstance(event, str):
                    annotations += [event.replace(" mg", "mg").replace(" ", "<br>") + "<br><br>"]
            if len(annotations) > 0:
                graphs[-1].annotation_dates += [date]
                graphs[-1].annotation_text  += ["<br>".join(annotations).rstrip("<br>") + "<br> "*15]

        runner += delta

def consolidate_events(day_accu):
    if len(day_accu) < 1:
        return

    maxnight = datetime.combine(day_accu[0].date, datetime.max.time())
    # maxnight = pytz.timezone("US/Pacific").localize(maxnight)
    day_accu += [HeadacheDay(maxnight, -1)]
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
    return HeadacheDay(midnight, final_rate)

def get_headache_days():
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

    runner = datetime(2017, 1, 1)
    d = relativedelta(days=1)
    while runner < datetime.now():
        t1 = runner
        t2 = runner + d
        selection = [x for x in headache_events if t1 <= x.date and x.date < t2]
        runner += d
        if len(selection) > 0:
            ret = consolidate_events(selection)
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

def main():
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

    graphs_accu = []

    d = relativedelta(months=1)
    gen_graph(graphs_accu, datetime(2017, 11, 1).date(), d, days)

    latest = []
    d = relativedelta(months=2)
    gen_graph(latest, (datetime.now()-d).date(), d, days)
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
