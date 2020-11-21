import os
import plotly.graph_objs as go
from plotly.offline import plot
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def yearmonth(time):
    return time.strftime("%b %d %Y")

WAKING_HRS_PER_WEEK = 16*7

class HeadacheHtmlBuilder():
    def __init__(self, graphs):
        self.graphs = graphs

    def gen_page(self):
        # TODO: use real HTML generator
        wfile = open(os.environ["BIOMETRICS_ROOT"] + "/web_biometrics/index.html", "w")
        for graph in reversed(self.graphs):
            graph_name, graph_dict = graph.gen_graph()

            head_pct = sum(graph.graph_percents)/len(graph.graph_percents)

            filename = "files/%s.html"%(graph_name.replace(" ", ""))
            # include_plotlyjs=True not useful, js always needed inside html file
            plot(graph_dict, filename=os.environ["BIOMETRICS_ROOT"] + "/web_biometrics/" + filename, auto_open=False)
            wfile.write("<a href=\"%s\">%s</a><br/>"%(filename,graph_name.split("/")[-1]))
            head_pct_str = "%2.2f" % (100.0*head_pct)
            pct_str  = ""
            pct_str += "&emsp;<b>%s&#37;</b> QOL<br/>" % head_pct_str
            print(pct_str)
            pct_str += "&emsp;<b>%d/%d</b> usable waking hours weekly<br/>" % (head_pct*WAKING_HRS_PER_WEEK, WAKING_HRS_PER_WEEK)

            for note in graph.html_notes:
                pct_str += "&emsp;%s" % note

            pct_str += "<br/>"
            wfile.write(pct_str)

        wfile.close()

class GraphData():
    def __init__(self, name):
        self.name             = name
        self.html_notes       = []
        self.annotation_dates = []
        self.annotation_text  = []
        self.graph_dates      = []
        self.graph_percents   = []
        self.range            = [-0.05, 1.05]

    def gen_graph(self):
        traces = []
        # main graph
        traces += [go.Line(
            name = self.name,
            x=self.graph_dates,
            y=[round(x, 2) for x in self.graph_percents],
            text=[str(dates) for dates in self.graph_dates],
            mode='lines+markers',
            hoverinfo='y+x',
            # line=dict(shape='hv', width=10)
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
                #    width=0.2, #bar width
                #    customdata=df['description'],
                #    hovertemplate='date: %{x}<br>event: %{customdata}',
                opacity=0.3
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

        border_size = (self.graph_dates[-1] - self.graph_dates[0]).total_seconds()/20
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
                bgcolor='rgba(255,255,255,0.75)',
            ),
            xaxis=dict(
                type= "date",
                range= [self.graph_dates[0]-timedelta(seconds=border_size),self.graph_dates[-1]+timedelta(seconds=border_size)],
                # rangeslider = dict(
                #     autorange = True,
                #     range     = [self.graph_dates[0]-timedelta(seconds=border_size),self.graph_dates[-1]+timedelta(seconds=border_size)]
                # )
            ),
            yaxis=dict(
                range=self.range
            )
        )

        start = self.graph_dates[0]
        end   = self.graph_dates[-1]

        name = "%s --- %s"%(yearmonth(start), yearmonth(end))
        return name, dict(data=traces, layout=layout)
