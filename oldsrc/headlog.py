# [x:y] excludes y
# all [:] operations should be [x:y+1]
import sys
sys.path.append('./src')
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import re
from headlog_oop import HeadacheEventList, HeadacheGraph, HeadacheHTML
import headlog_data
import headlog_test

if __name__== "__main__":
    hel = HeadacheEventList()
    headlog_data.parse_buddy(hel.headache_events)
    headlog_data.parse_daylio(hel.headache_events)
    hel.headache_events = sorted(hel.headache_events)
    hel.sanitize()

    headlog_test.tests(hel)

    start  = hel.headache_events[0].start.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
    end    = hel.headache_events[-1].start

    graphs = []

    whole_history = HeadacheGraph()
    whole_history.graph_percents, whole_history.graph_dates = headlog_data.get_pcts(hel, relativedelta(months=1))
    whole_history.annotation_text, whole_history.annotation_dates = hel.get_annotations(start, end)
    whole_history.html_notes += ["<b>%d</b> Maxalts taken<br/>" % hel.find_num_occurrence_in_range("maxalt")]
    # whole_history.graph_percents, whole_history.graph_dates = headlog_data.get_pcts(hel, relativedelta(days=1), datetime.now() - relativedelta(months=1), datetime.now() )    # graph.gen_graph()


    runner = start
    offset = relativedelta(months=1)

    while runner < end:
        month_graph = HeadacheGraph()
        # go to end of month if all days are there, else go to end of recorded history

        month_graph.annotation_text, month_graph.annotation_dates = hel.get_annotations(runner, runner+offset)
        month_graph.html_notes += ["<b>%d</b> Maxalts taken<br/>" % hel.find_num_occurrence_in_range("maxalt", runner, runner+offset)]
        drugs_started = hel.find_occurrence_in_range("started", runner, runner+offset)
        for drug in drugs_started:
            month_graph.html_notes += ["%s<br/>" % drug]

        if runner + offset > end:
            month_graph.graph_percents, month_graph.graph_dates = headlog_data.get_pcts(hel, relativedelta(days=1), runner, end)
        else:
            month_graph.graph_percents, month_graph.graph_dates = headlog_data.get_pcts(hel, relativedelta(days=1), runner, runner + offset)
        # print("html_notes", month_graph.html_notes)
        # print("annotation_dates", month_graph.annotation_dates)
        # print("annotation_text", month_graph.annotation_text)
        # print("graph_dates", month_graph.graph_dates)
        # print("graph_percents", month_graph.graph_percents)
        # exit()
        graphs += [month_graph]
        runner += offset

    graphs += [whole_history]
    html = HeadacheHTML(graphs)

    html.gen_page()
    headlog_test.tests(hel)
