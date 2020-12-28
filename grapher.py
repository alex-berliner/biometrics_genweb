import re
import os
import plotly.graph_objs as go
from plotly.offline import plot
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def yearmonth(time):
    return time.strftime("%b %Y")

WAKING_HRS_PER_WEEK = 16*7

class HeadacheHtmlBuilder():
    def __init__(self, graphs):
        self.graphs = graphs

    def gen_page(self):
        # TODO: use real HTML generator
        report = ""
        head_pct_strs = []
        html_junk = "<br>"
        # wfile = open(os.environ["BIOMETRICS_ROOT"] + "/web_biometrics/index.html", "w")
        bottom = ""
        for graph in reversed(self.graphs):
            graph_name, graph_dict = graph.gen_graph()

            head_pct = sum(graph.graph_percents)/len(graph.graph_percents)

            link_file = graph_name.replace(" ", "")
            link_name = graph_name.split("/")[-1]
            if graph.is_latest:
                link_file = "last_two_months"
                link_name = "Everything"
                plot(graph_dict, filename=os.environ["BIOMETRICS_ROOT"] + "/web_biometrics/index.html", auto_open=False)
            # filename = "files/%s.html" % link_file

            head_pct_str = "%2.2f" % (100.0*head_pct)
            head_pct_strs += ["%s: %s%%"%(graph_name, head_pct_str)]
            pct_str  = ""
            pct_str += "%s<br>" % link_file
            pct_str += "&emsp;<b>%s&#37;</b> QOL<br>" % head_pct_str
            pct_str += "&emsp;<b>%d/%d</b> usable waking hours weekly<br>" % (head_pct*WAKING_HRS_PER_WEEK, WAKING_HRS_PER_WEEK)
            takens = [x for x in re.split("  +", " ".join(graph.annotation_text).replace("<br>", " ")) if len(x) > 0]
            if graph.is_latest:
                takens = []

            for note in graph.html_notes:
                pct_str += "&emsp;%s" % note

            pct_str += "<br>"

            html_junk += pct_str
            html_junk=html_junk.rstrip("<br>")
            takens_str = "<br>&emsp;" + "<br>&emsp;".join(takens).lstrip("<br>") + "<br><br>"
            html_junk += takens_str

        with open(os.environ["BIOMETRICS_ROOT"] + "/web_biometrics/index.html", "a") as myfile:
            myfile.write(html_junk)

class GraphData():
    def __init__(self, name):
        self.name                     = name
        self.html_notes               = []
        self.annotation_dates         = []
        self.annotation_text          = []
        self.graph_dates              = []
        self.graph_percents           = []
        self.min_graph_percents       = []
        self.min_graph_dates          = []
        self.aimovig_level_dates      = []
        self.aimovig_level_percents   = []
        self.range                    = [-0.05, 1.05]
        self.is_latest                = False

    def gen_graph(self):
        traces = []
        # main graph
        traces += [go.Scatter(
            name = "Feeling bad",
            x=[self.graph_dates[0], self.graph_dates[-1]],
            y=[0.80, 0.80],
            marker_color='rgba(239, 85, 59, 0.7)',
        )]
        traces += [go.Scatter(
            name = "Feeling good",
            x=[self.graph_dates[0], self.graph_dates[-1]],
            y=[0.88, 0.88],
            marker_color='rgba(0, 172, 86, 0.7)'
        )]
        traces += [go.Scatter(
            name = "Headache Attack",
            x=[self.graph_dates[0], self.graph_dates[-1]],
            y=[0.75, 0.75],
            marker_color='rgba(239, 85, 59, 0.7)',
        )]
        traces += [go.Scatter(
            name = "Headache Avg Intensity",
            x=self.graph_dates,
            y=[round(x, 2) for x in self.graph_percents],
            text=[str(dates) for dates in self.graph_dates],
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
            traces += [
                go.Bar(x = [date],
                y = [1],
                name=text,
                showlegend=False,
                hoverinfo="none",
                #    marker_color=event_color,
                   width=100000000*2.05, #bar width
                #    customdata=df['description'],
                #    hovertemplate='date: %{x}<br>event: %{customdata}',
                opacity=0.3
                )]
        traces += [go.Scatter(
            name = "Aimovig in Blood",
            x=self.aimovig_level_dates,
            y=[x/280 for x in self.aimovig_level_percents],
            text=[self.aimovig_level_percents],
            mode='lines+markers',
            hoverinfo='y+x',
            line_shape='linear',
            line=dict(shape='hv', width=3),
            marker_color='rgba(165, 165, 49, .7)',
            visible = "legendonly",
        )]
        traces += [go.Scatter(
            name = "Aimovig Level Danger",
            x=[self.graph_dates[0], self.graph_dates[-1]],
            y=[0.56, 0.56],
            marker_color='rgba(239, 85, 59, 0.7)',
            visible = "legendonly",
        )]

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

        border_size = 86400/3#(self.graph_dates[-1] - self.graph_dates[0]).total_seconds()/20
        layout = dict(
            annotations= annotations,
            dragmode= "zoom",
            legend=dict(
                # y=0.5,
                # x=0.5,
                # traceorder='reversed',
                font=dict(
                    size=16
                ),
                # hoverinfo= "name+x+text",
                # yanchor="bottom",
                y=0.01,
                # xanchor="left",
                x=0.01,
                bgcolor='rgba(255,255,255,1)',
            ),
            xaxis=dict(
                type= "date",
                range = [self.graph_dates[-1]-relativedelta(months=2), self.graph_dates[-1]+timedelta(seconds=border_size)],
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                                label="1m",
                                step="month",
                                stepmode="backward"),
                        dict(count=2,
                                label="2m",
                                step="month",
                                stepmode="backward"),
                        dict(count=3,
                                label="3m",
                                step="month",
                                stepmode="backward"),
                        dict(count=6,
                                label="6m",
                                step="month",
                                stepmode="backward"),
                        dict(count=1,
                                label="YTD",
                                step="year",
                                stepmode="todate"),
                        dict(count=1,
                                label="1y",
                                step="year",
                                stepmode="backward"),
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

        start = self.graph_dates[0]
        end   = self.graph_dates[-1]

        name = "%s --- %s"%(yearmonth(start), yearmonth(end))
        return name, dict(data=traces, layout=layout)
