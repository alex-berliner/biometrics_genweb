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

    def date_range_str(self, graph):
        return "%s --- %s"%(yearmonth(graph.graph_dates[0].replace(day=1,hour=0,minute=0,second=0,microsecond=0)),
                         yearmonth(graph.graph_dates[-1].replace(day=1,hour=0,minute=0,second=0,microsecond=0)))

    def gen_page(self):
        wfile = open("index.html", "w")
        for graph in reversed(self.graphs):
            graph_name, graph_dict = graph.gen_graph()

            head_pct = sum(graph.graph_percents)/len(graph.graph_percents)

            filename = "files/%s.html"%(graph_name.replace(" ", ""))
            plot(graph_dict, filename=filename, auto_open=False)
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
        self.name = name
        self.html_notes       = []
        self.annotation_dates = []
        self.annotation_text  = []
        self.graph_dates      = []
        self.graph_percents   = []

    def gen_graph(self):
        headache_trace = go.Scatter(
            name = self.name,
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

        name = "%s --- %s"%(yearmonth(start), yearmonth(end))

        return name, dict(data=data, layout=layout)

def main():
    one = GraphData("one")
    one.graph_dates += [1]
    two = GraphData("two")
    two.graph_dates += [2]
    print(two.graph_dates)
    # zorp = GraphData("Headache Intensity")

    # zorp.html_notes = ['<b>0</b> Maxalts taken<br/>']
    # zorp.annotation_dates = []
    # zorp.annotation_text = []
    # zorp.graph_dates = [
    #     datetime(2018, 5, 1, 0, 0),  datetime(2018, 5, 2, 0, 0),  datetime(2018, 5, 3, 0, 0),
    #     datetime(2018, 5, 4, 0, 0),  datetime(2018, 5, 5, 0, 0),  datetime(2018, 5, 6, 0, 0),
    #     datetime(2018, 5, 7, 0, 0),  datetime(2018, 5, 8, 0, 0),  datetime(2018, 5, 9, 0, 0),
    #     datetime(2018, 5, 10, 0, 0), datetime(2018, 5, 11, 0, 0), datetime(2018, 5, 12, 0, 0),
    #     datetime(2018, 5, 13, 0, 0), datetime(2018, 5, 14, 0, 0), datetime(2018, 5, 15, 0, 0),
    #     datetime(2018, 5, 16, 0, 0), datetime(2018, 5, 17, 0, 0), datetime(2018, 5, 18, 0, 0),
    #     datetime(2018, 5, 20, 0, 0), datetime(2018, 5, 21, 0, 0), datetime(2018, 5, 22, 0, 0),
    #     datetime(2018, 5, 27, 0, 0), datetime(2018, 5, 29, 0, 0), datetime(2018, 5, 31, 0, 0)
    # ]

    # zorp.graph_percents = [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.45645833333333335, 0.6825, 0.8, 1.0, 0.9143730886850153, 0.543417023882425, 0.0, 0.02556663644605621, 0.0, 0.6, 0.0, 0.0]

    # html = HeadacheHtmlBuilder([zorp])
    # html.gen_page()

if __name__ == '__main__':
  main()
