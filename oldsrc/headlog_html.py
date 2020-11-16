# https://plot.ly/python/line-charts/
import plotly.graph_objs as go
from plotly.offline import plot
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# def export_html(hel):
    # monthly_backing = hel.get_period("monthly")
    # generate_monthly_data(hel)
    # do_plots(hel)
    # get_pcts(hel)

# def generate_monthly_data(hel):
#     start = hel.headache_events[0].start.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
#     end   = hel.headache_events[-1].end

#     while runner < end:

#         runner += offset

# Generate headache plotly graph
# Take headache event list, normalize data into daily intensity percentage, then create plotly obj
# Only creates graphs with daily granularity, unless whole history is being passed, which does monthly granularity
def get_graph(hel, beg=None, end=None):
    head_x, head_y = hel.range_normalize(beg, end)
    headache_trace = go.Scatter(
        name = "Headache Intensity",
        x=head_x,
        y=head_y,
        text=[str(dates) for dates in head_x],
        mode='lines+markers',
        # hoverinfo='y',
        line=dict(shape='hv')
    )

    border_size = (head_x[-1] - head_x[0]).total_seconds()/20

    data = [headache_trace]
    layout = dict(
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
            range= [head_x[0]-timedelta(seconds=border_size),head_x[-1]+timedelta(seconds=border_size)],
            rangeslider = dict(
                autorange = True,
                range     = [head_x[0]-timedelta(seconds=border_size),head_x[-1]+timedelta(seconds=border_size)]
            )
        ),
        yaxis=dict(
            range=[0, 1]
        )
    )
    # get name for plot. hardcoded to be starting and ending month, unless it's the whole history
    if end is None and beg is None:
        name = "entire_history"
    else:
        if end is None:
            end = head_x[-1]
        if head_x.month is end.month:
            # end += relativedelta(months=1)
        name = "%s --- %s"%(yearmonth(head_x[0].replace(day=1,hour=0,minute=0,second=0,microsecond=0)),
                           yearmonth(end.replace(day=1,hour=0,minute=0,second=0,microsecond=0)))

    return name, dict(data=data, layout=layout)

# create monthly plots from headache event list, and export them as html
def do_plots(hel):
    figs=[]
    figs += [get_graph(hel)]

    start  = hel.headache_events[0].start.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
    end    = hel.headache_events[-1].end
    runner = start
    offset = relativedelta(months=1)

    while runner < end:
        figs += [get_graph(hel, runner, runner+offset)]
        runner += offset

    wfile = open("index.html", "a")
    for fig in figs:
        filename = "files/%s.html"%fig[0]
        plot(fig[1], filename=filename, auto_open=False)
        wfile.write("<a href=\"%s\">%s</a><br/>"%(filename,filename.split("/")[-1]))

    wfile.close()
