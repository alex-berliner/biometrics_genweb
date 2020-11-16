# https://plot.ly/python/line-charts/
from datetime import datetime, timedelta
import re
import sqlite3
from headlog_oop import HeadacheEvent

app_path = "head_backup/data/data/"
daylio_regex_headache = "headache (\\<?\\d(\\.?\\d)?)".lower()
daylio_regex_neck     = "neck pain (\\<?\\d(\\.?\\d)?)".lower()
daylio_text_new_scale = "Start new head ache scale"
drugs = ["aimovig", "tylenol", "maxalt", "caffiene", "advil", "gralise", "gabapentin"]

def get_pcts(hel, offset, start=None, end=None):
    if start is None:
        start = hel.headache_events[0].start.replace(day=1,hour=0,minute=0,second=0,microsecond=0)

    if end is None:
        end = hel.headache_events[-1].end

    runner = start

    pct_list  = []
    date_list = []

    while runner < end:
        gotpct = hel.get_head_percent(runner, runner + offset)
        if gotpct is not -1:
            pct_list  += [gotpct]
            date_list += [runner]
        runner += offset

    return pct_list, date_list

def parse_daylio(headache_list):
    def sortkey(item): return item[0]

    db = sqlite3.connect(app_path + 'net.daylio/databases/entries.db')
    cursor = db.cursor()
    main_entries = cursor.execute('SELECT date_time,note FROM table_entries')
    main_entries = sorted(main_entries, key=sortkey)

    for row in main_entries:
        te = HeadacheEvent()
        te.start  = datetime.fromtimestamp(int(row[0])/1000)
        te.notes = row[1].split("\n")

        # find medications taken
        for note_elem in te.notes:
            lowered_note = note_elem.lower()
            if "took" in lowered_note:
                for drug in drugs:
                    if drug in lowered_note:
                        te.meds += [drug]

            match = re.search(daylio_regex_neck, lowered_note)
            if match is not None:
                te.intensity_neck = str(match.group(1))

            match = re.search(daylio_regex_headache, lowered_note)
            if match is not None:
                te.intensity_head = str(match.group(1))
        if    te.intensity_neck is not None \
           or te.intensity_head is not None \
           or len(te.meds) > 0:
            headache_list += [te]

    return headache_list

def parse_buddy(headache_list):
    db = sqlite3.connect(app_path + 'com.healint.migraineapp/databases/migraine.db')
    cursor = db.cursor()

    for row in cursor.execute('SELECT painIntensity,startTime,endTime FROM migraineevent'):
        te = HeadacheEvent()
        te.intensity_head = str(row[0])
        te.start = datetime.fromtimestamp(row[1]/1000)
        headache_list += [te]

    return headache_list

