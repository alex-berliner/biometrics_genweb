import re
import os
import plotly.graph_objs as go
from plotly.offline import plot
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from plotly.subplots import make_subplots

def yearmonth(time):
    return time.strftime("%b %Y")

WAKING_HRS_PER_WEEK = 16*7

def gen_html(graph):
    # TODO: use real HTML generator
    graph_name, fig = graph.gen_graph_data()

    link_file = graph_name.replace(" ", "")
    link_name = graph_name.split("/")[-1]
    if graph.is_latest:
        link_file = "last_two_months"
        link_name = "Everything"
        fig.write_html(os.environ["BIOMETRICS_ROOT"] + "/web_biometrics/index.html")

    # head_pct = sum(graph.graph_percents_run_avg)/len(graph.graph_percents_run_avg)
    # head_pct_strs = []
    # html_junk = "<br>"
    # head_pct_str = "%2.2f" % (100.0*head_pct)
    # head_pct_strs += ["%s: %s%%"%(graph_name, head_pct_str)]
    # pct_str  = ""
    # pct_str += "%s<br>" % link_file
    # pct_str += "&emsp;<b>%s&#37;</b> QOL<br>" % head_pct_str
    # pct_str += "&emsp;<b>%d/%d</b> usable waking hours weekly<br>" % (head_pct*WAKING_HRS_PER_WEEK, WAKING_HRS_PER_WEEK)
    # takens = [x for x in re.split("  +", " ".join(graph.annotation_text).replace("<br>", " ")) if len(x) > 0]
    # if graph.is_latest:
    #     takens = []

    # for note in graph.html_notes:
    #     pct_str += "&emsp;%s" % note

    # pct_str += "<br>"

    # html_junk += pct_str
    # html_junk=html_junk.rstrip("<br>")
    # takens_str = "<br>&emsp;" + "<br>&emsp;".join(takens).lstrip("<br>") + "<br><br>"
    # html_junk += takens_str

    # with open(os.environ["BIOMETRICS_ROOT"] + "/web_biometrics/index.html", "a") as myfile:
    #     myfile.write(html_junk)

class GraphData():
    def __init__(self, name):
        self.name                     = name
        self.html_notes               = []
        self.annotation_dates         = []
        self.annotation_text          = []
        self.graph_dates_raw          = []
        self.graph_percents_raw       = []
        self.graph_dates_run_avg      = []
        self.graph_percents_run_avg   = []
        self.min_graph_percents       = []
        self.min_graph_dates          = []
        self.aimovig_level_dates      = []
        self.aimovig_level_mg         = []
        self.range                    = [0, 1.05]
        self.is_latest                = False

    def gen_graph_data(self):
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # main graph traces
        traces = []
        traces += [go.Scatter(
            name = "Feeling bad",
            x=[self.graph_dates_run_avg[0], self.graph_dates_run_avg[-1] + relativedelta(months=3)],
            y=[0.80, 0.80],
            marker_color='rgba(239, 85, 59, 0.7)',
        )]
        traces += [go.Scatter(
            name = "Feeling good",
            x=[self.graph_dates_run_avg[0], self.graph_dates_run_avg[-1] + relativedelta(months=3)],
            y=[0.88, 0.88],
            marker_color='rgba(0, 172, 86, 0.7)'
        )]
        traces += [go.Scatter(
            name = "Headache Attack",
            x=[self.graph_dates_run_avg[0], self.graph_dates_run_avg[-1] + relativedelta(months=3)],
            y=[0.75, 0.75],
            marker_color='rgba(239, 85, 59, 0.7)',
            visible = "legendonly",
        )]
        traces += [go.Scatter(
            name = "Headache Raw Intensity",
            x=self.graph_dates_raw,
            y=[round(x, 2) for x in self.graph_percents_raw],
            text=[str(dates) for dates in self.graph_dates_raw],
            mode='lines+markers',
            hoverinfo='y+x',
            line_shape='linear',
            line=dict(shape='hv', width=3),
            marker_color='rgba(174, 142, 240, 1)',
            visible = "legendonly",
        )]
        traces += [go.Scatter(
            name = "Headache Avg Intensity",
            x=self.graph_dates_run_avg,
            y=[round(x, 2) for x in self.graph_percents_run_avg],
            text=[str(dates) for dates in self.graph_dates_run_avg],
            mode='lines+markers',
            hoverinfo='y+x',
            line_shape='linear',
            line=dict(shape='hv', width=3),
            marker_color='rgba(99, 110, 250, 1)',
        )]
        traces += [go.Scatter(
            name = "Headache Max Intensity",
            x=self.min_graph_dates,
            y=[round(x, 2) for x in self.min_graph_percents],
            text=[str(dates) for dates in self.min_graph_dates],
            mode='lines+markers',
            hoverinfo='y+x',
            line_shape='linear',
            line=dict(shape='hv', width=3),
            marker_color='rgba(250, 20, 20, 1)',
            visible = "legendonly",
        )]
        for i in range(len(self.annotation_dates)):
            date = self.annotation_dates[i]
            text = self.annotation_text[i]
            traces += [ go.Bar( x = [date],
                                y = [1],
                                name=text,
                                showlegend=False,
                                hoverinfo="none",
                                width=100000000*2.05, #bar width
                                opacity=0.3
                                ) ]
        aib = go.Scatter(
            name = "Aimovig in Blood",
            x=self.aimovig_level_dates,
            y=[x for x in self.aimovig_level_mg],
            text=[self.aimovig_level_mg],
            mode='lines+markers',
            hoverinfo='y+x',
            line_shape='linear',
            line=dict(shape='hv', width=3),
            marker_color='rgba(165, 165, 49, .7)',
            visible = "legendonly",
        )
        ald = go.Scatter(
            name = "Aimovig Level Danger",
            x=[self.graph_dates_run_avg[0], self.graph_dates_run_avg[-1] + relativedelta(months=3)],
            y=[157.57, 157.57],
            marker_color='rgba(239, 85, 59, 0.7)',
            visible = "legendonly",
        )
        for t in traces:
            fig.add_trace(t, secondary_y=False)

        # add aimovig graph as secondary axis
        traces += [ald]
        traces += [aib]
        fig.add_trace(aib, secondary_y=True)
        fig.add_trace(ald, secondary_y=True)

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

        border_size = 86400/3
        fig.update_layout(
            annotations= annotations,
            dragmode= "zoom",
            legend=dict(
                font=dict( size=16 ),
                y=0.01,
                x=0.01,
                bgcolor='rgba(255,255,255,1)',
            ),
            xaxis=dict(
                type= "date",
                # length of the whole graph
                range = [self.graph_dates_run_avg[-1]-relativedelta(months=3),
                         self.graph_dates_run_avg[-1]+timedelta(seconds=border_size)],
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m",  step="month", stepmode="backward"),
                        dict(count=2, label="2m",  step="month", stepmode="backward"),
                        dict(count=3, label="3m",  step="month", stepmode="backward"),
                        dict(count=6, label="6m",  step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year",  stepmode="todate"),
                        dict(count=1, label="1y",  step="year",  stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True,
                ),
            ),
            yaxis=dict(
                range=self.range
            )
        )
        start = self.graph_dates_run_avg[0]
        end   = self.graph_dates_run_avg[-1]
        name = "%s --- %s"%(yearmonth(start), yearmonth(end))

        return name, fig
