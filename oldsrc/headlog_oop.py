import plotly.graph_objs as go
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from headlog_helpers import yearmonth
from plotly.offline import plot

WAKING_HRS_PER_WEEK = 16*7

class HeadacheGraph():
    def __init__(self, graph_dates=[], graph_percents=[], html_notes = []):
        self.html_notes       = []
        self.annotation_dates = []
        self.annotation_text  = []
        self.graph_dates      = graph_dates
        self.graph_percents   = graph_percents
        # self.maxalts_taken    = maxalts_taken

    def gen_graph(self):
        headache_trace = go.Scatter(
            name = "Headache Intensity",
            x=self.graph_dates,
            y=self.graph_percents,
            text=[str(dates) for dates in self.graph_dates],
            mode='lines+markers',
            # hoverinfo='y',
            line=dict(shape='hv')
        )

        border_size = (self.graph_dates[-1] - self.graph_dates[0]).total_seconds()/20

        annotations = []
        for i in range(len(self.annotation_text)):
            annotations += \
                [{
                    "x": self.annotation_dates[i],
                    "y": 0.10,
                    "arrowcolor": "rgba(63, 81, 181, 0.2)",
                    "arrowsize": 0.3,
                    "ax": 0,
                    "ay": 30,
                    "text": self.annotation_text[i],
                    "xref": "x",
                    "yanchor": "bottom",
                    "yref": "y"
                }]

        data = [headache_trace]
        layout = dict(
            annotations= annotations,
            dragmode= "zoom",
            legend=dict(
                # y=0.5,
                # x=0.5,
                traceorder='reversed',
                font=dict(
                    size=16
                ),
                # hoverinfo= "name+x+text",
            ),
            xaxis=dict(
                type= "date",
                range= [self.graph_dates[0]-timedelta(seconds=border_size),self.graph_dates[-1]+timedelta(seconds=border_size)],
                rangeslider = dict(
                    autorange = True,
                    range     = [self.graph_dates[0]-timedelta(seconds=border_size),self.graph_dates[-1]+timedelta(seconds=border_size)]
                )
            ),
            yaxis=dict(
                range=[-0.05, 1.05]
            )
        )

        start = self.graph_dates[0].replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        end   = self.graph_dates[-1].replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        if end.month is start.month:
            end += relativedelta(months=1)

        name = "%s --- %s"%(yearmonth(start),
                            yearmonth(end))

        return name, dict(data=data, layout=layout)


class HeadacheEventList():
    def __init__(self):
        self.scale_change_date = None
        self.headache_events   = []

    def month_period_index(self, d1, d2):
        retstr = "%s%s"%(d1.strftime("%b%Y"), d2.strftime("%b%Y"))
        return retstr

    def find_scale_switch(self):
        self.headache_events = sorted(self.headache_events)
        for elem in self.headache_events:
            for note in elem.notes:
                if "head ache" in note:
                    self.scale_change_date = elem.start
                    return

    def scale_switch(self):
        if self.scale_change_date is None:
            self.find_scale_switch()

        for elem in self.headache_events:
            elem.scale_switch(self.scale_change_date)

    def fill_end_times(self):
        self.headache_events = sorted(self.headache_events)
        for i in range(len(self.headache_events)-1):
            self.headache_events[i].end = self.headache_events[i+1].start
        self.headache_events[-1].end = self.headache_events[-1].start + timedelta(hours=2)

    def fill_durations(self):
        self.headache_events = sorted(self.headache_events)
        days = []
        for i in range(len(self.headache_events)):
            elem = self.headache_events[i]
            dayrunner = elem.start
            while dayrunner < elem.end:
                dayend = dayrunner.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

                # move back end if on the last day
                if dayend > elem.end:
                    dayend = elem.end

                # move start to after 8 if necessary on the first day
                if dayrunner.hour < 8:
                    dayrunner = dayrunner.replace(hour=8, minute=0, second=0, microsecond=0)

                # discard entries existing entirely been midnight and 8
                if dayend < dayrunner.replace(hour=8, minute=0, second=0, microsecond=0):
                    continue

                duration = dayend - dayrunner
                elem.duration += duration

                dayrunner = dayrunner.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)

            # some entries from the beginning have large values from spotty activity, pare them down
            if elem.duration > timedelta(hours=(24-8)*2):
                elem.duration = timedelta(hours=(24-8)*2)

    def get_range(self, start_request=None, end_request=None):
        self.headache_events = sorted(self.headache_events)
        start_i = 0
        end_i   = len(self.headache_events)-1

        # if no start is specified
        if start_request is None:
            start_request = self.headache_events[0].start

        # if no end is specified
        if end_request is None:
            end_request = self.headache_events[-1].start

        # if dates are crossed, reject
        if start_request > end_request:
            return -1, -1

        found_start = False
        found_end = False
        for i in range(len(self.headache_events)):
            if (not found_start) and (self.headache_events[i].start >= start_request):
                found_start = True
                start_i = i

            if (not found_end) and (self.headache_events[i].end >= end_request):
                found_end = True
                end_i = i

            if found_start and found_end:
                break
        if start_i > end_i:
            return -1, -1
        return start_i, end_i

    # produce "started/took drug" annotations
    def get_annotations(self, start_date, end_date):
        start_i, end_i = self.get_range(start_date, end_date)
        if start_i == -1:
            return -1

        date_range_elems = self.headache_events[start_i:end_i+1]

        annotations = []
        dates       = []

        for elem in date_range_elems:
            starteds = list((filter(lambda e: "started" in e.lower(), elem.notes)))
            started_anno = None
            if len(starteds) > 0:
                annotations += [" ".join(starteds).replace(" ", "<br />")]
                dates       += [elem.start]
                started_anno = True

            # Enable to display maxalts
            # maxalts = list((filter(lambda e:  e.lower(), elem.meds)))
            # if len(maxalts) > 0:
            #     if started_anno:
            #         annotations[-1] += "M"
            #     else:
            #         annotations += ["M<br />"]
            #         dates       += [elem.start]

        return annotations, dates

    def get_head_percent(self, start_date, end_date):
        start_i, end_i = self.get_range(start_date, end_date)
        if start_i == -1:
            return -1

        bucket_date_range = self.headache_events[start_i:end_i+1]
        if len(bucket_date_range) < 1:
            return -1
        total_duration = 0
        total_qol      = 0
        for elem in bucket_date_range:
            intensity_head = float(elem.intensity_head) if elem.intensity_head is not None else 100
            intensity_neck = float(elem.intensity_neck) if elem.intensity_neck is not None else 100

            if intensity_head is 100 and intensity_neck is 100:
                continue

            intensity = min(intensity_head, intensity_neck)

            qol = 10 - float(intensity)*2
            if qol >= 9:
                qol = 10
            if qol <= 4:
                qol = 0

            total_qol      += float(qol)/10.0 * elem.duration.total_seconds()
            total_duration += elem.duration.total_seconds()
        if total_duration < .0001:
            return 0
        return total_qol/float(total_duration)

    def find_num_occurrence_in_range(self, find_str, start_request=None, end_request=None):
        start_i = 0
        end_i   = len(self.headache_events)-1

        # if no start is specified
        if start_request is None:
            start_request = self.headache_events[0].start

        # if no end is specified
        if end_request is None:
            end_request = self.headache_events[-1].start

        # if dates are crossed, reject
        if start_request > end_request:
            return 0

        beg, end = self.get_range(start_request, end_request)
        event_range = self.headache_events[beg:end+1]
        num_result = 0
        for event in event_range:
            if find_str in "".join(event.notes):
                num_result+=1
        return num_result

    def find_occurrence_in_range(self, find_str, start_request=None, end_request=None):
        start_i = 0
        end_i   = len(self.headache_events)-1

        # if no start is specified
        if start_request is None:
            start_request = self.headache_events[0].start

        # if no end is specified
        if end_request is None:
            end_request = self.headache_events[-1].start

        # if dates are crossed, reject
        if start_request > end_request:
            return 0

        beg, end = self.get_range(start_request, end_request)
        event_range = self.headache_events[beg:end+1]
        ret_notes = []
        for event in event_range:
            for note in event.notes:
                if find_str in note.lower():
                    # num_result+=1
                    ret_notes += [note]
        return ret_notes


    def sanitize(self):
        self.scale_switch()
        self.fill_end_times()
        self.fill_durations()

    # normalize events to having one per day
    def range_normalize(self, beg_date=None, end_date=None, slide_avg_days=1):
        # if no start is specified
        if beg_date is None:
            beg_date = self.headache_events[0].start

        # if no end is specified
        if end_date is None:
            end_date = self.headache_events[-1].end

        # def sliding_average(hel):
        # start = hel.headache_events[0].start.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        start  = beg_date.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        # end    = hel.headache_events[-1].end
        end    = end_date
        runner = start
        offset = relativedelta(days=1)

        time_normalized_percents = []
        iterated_days = []

        while runner < end:
            day_percent = self.get_head_percent(runner, runner+offset)
            time_normalized_percents += [day_percent]
            iterated_days += [runner]
            runner += offset

        # slide averaging
        averaged_vals = []
        accu = []
        for val in time_normalized_percents:
            accu = accu + [val]
            if len(accu)>slide_avg_days:
                del accu[0]
            avg = 0
            for avg_accu in accu:
                avg += avg_accu
            averaged_vals += [avg/len(accu)]

        return iterated_days, averaged_vals

    def get_headache_plot(self, beg_date=None, end_date=None):
        beg_i, end_i = self.get_range(beg_date, end_date)
        date_range = hel.headache_events[beg_i:end_i+1]
        event_filter = list((filter(lambda e: e.intensity_head is not None, date_range)))

        x     = [e.start for e in event_filter]
        y     = [e.intensity_head for e in event_filter]
        # notes = [e.notes for e in event_filter]
        return x, y

class HeadacheEvent():
    def __init__(self, start=None, intensity_head=None, intensity_neck=None):
        self.start          = start
        self.end            = None
        self.duration       = timedelta(0)
        self.intensity_head = intensity_head
        self.intensity_neck = intensity_neck
        self.notes          = ""
        self.meds           = []
        self.scale_switched = False

    def __eq__(self, other):
        return self.start == other.start

    def __lt__(self, other):
        return self.start < other.start

    def __str__(self):
        retstr = ""

        if self.end is None:
            self.end = self.start

        if self.intensity_head:
            retstr += "Head Intensity: " + str(self.intensity_head) + "\n"

        if self.intensity_neck:
            retstr += "Neck Intensity: " + str(self.intensity_neck) + "\n"

        if self.start:
            retstr += "Start: " + str(self.start) + "\n"

        if self.end:
            retstr += "End:   " + str(self.end) + "\n"

        if len(self.meds) > 0:
            retstr += "Meds:" + "\n"
            for med in self.meds:
                retstr += "\t" + med + "\n"

        return retstr.rstrip("\n")

    def scale_switch(self, switch_date):
        def scale(intensity):
            scale = [ [5,5], [3,4], [2,3], [1,2], [0,1], [-1,0] ]
            for s in scale:
                if intensity > s[0]:
                    return s[1]

        if self.scale_switched is True or switch_date is None:
            return

        self.scale_switched = True

        if (self.start - switch_date).total_seconds() > 0:
            return

        if self.intensity_head is not None:
            self.intensity_head = scale(float(self.intensity_head.replace("<1","0.5")))

        if self.intensity_neck is not None:
            self.intensity_neck = scale(float(self.intensity_neck.replace("<1","0.5")))
