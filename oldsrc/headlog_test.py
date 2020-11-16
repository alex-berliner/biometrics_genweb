import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# one entry of intensity 1
def test_feb_15(hel):
    t1 = datetime(year=2019,month=2,day=15)
    t2 = datetime(year=2019,month=2,day=16)
    i1,i2 = hel.get_range(t1,t2)

    res = len(hel.headache_events[i1:i2+1]) == 1
    if not res:
        print("Fail: %s" % sys._getframe().f_code.co_name)
    return res

def test_before_range(hel):
    t1 = datetime(year=2000,month=2,day=15)
    t2 = datetime(year=2019,month=2,day=16)
    i1,i2 = hel.get_range(t1,t2)

    res = i1 == 0
    if not res:
        print("Fail: %s" % sys._getframe().f_code.co_name)
    return res

def test_after_range(hel):
    t1 = datetime(year=2019,month=1,day=1)
    t2 = datetime(year=2020,month=1,day=1)
    i1,i2 = hel.get_range(t1,t2)

    res = i2 == (len(hel.headache_events)-1)
    if not res:
        print("Fail: %s" % sys._getframe().f_code.co_name)
    return res

def test_no_delta(hel):
    t1 = datetime(year=2019,month=1,day=1)
    t2 = datetime(year=2019,month=1,day=1)
    i1,i2 = hel.get_range(t1,t2)

    res = i1 == i2 and i2 == -1
    if not res:
        print("Fail: %s" % sys._getframe().f_code.co_name)
    return res

def test_neither_in_range_before(hel):
    t1 = datetime(year=2000,month=1,day=1)
    t2 = datetime(year=2000,month=1,day=1)
    i1,i2 = hel.get_range(t1,t2)

    res = i1 == i2 == 0
    if not res:
        print("Fail: %s" % sys._getframe().f_code.co_name)
    return res

def test_neither_in_range_before(hel):
    t1 = datetime(year=2000,month=1,day=1)
    t2 = datetime(year=2000,month=1,day=1)
    i1,i2 = hel.get_range(t1,t2)

    res = i1 == i2 == 0
    if not res:
        print("Fail: %s" % sys._getframe().f_code.co_name)
    return res

def test_cross_dates(hel):
    t1 = datetime(year=2000,month=1,day=2)
    t2 = datetime(year=2000,month=1,day=1)
    i1,i2 = hel.get_range(t1,t2)

    res = i1 == i2 == -1
    if not res:
        print("Fail: %s" % sys._getframe().f_code.co_name)
    return res

def test_range_boundaries(hel):
    t1 = datetime(year=2019,month=1,day=1)
    t2 = datetime(year=2019,month=2,day=1)
    t3 = datetime(year=2019,month=3,day=1)
    i1, i2 = hel.get_range(t1,t2)
    # print(i1, i2)
    # print(hel.headache_events[i1])
    # print(hel.headache_events[i2])
    i3, i4 = hel.get_range(t2,t3)
    # print(i3, i4)
    # print(hel.headache_events[i3])
    # print(hel.headache_events[i4])
    # print(len(hel.headache_events))


    # print()
    # print()
    # print(hel.headache_events[i1:i2+1][-1])
    # print(hel.headache_events[i3:i4+1][0])

    res = i2+1 == i3
    if not res:
        print("Fail: %s" % sys._getframe().f_code.co_name)
    return res

def test_range_boundary_end(hel):
    t2 = datetime.now()
    t1 = t2-relativedelta(months=1)
    i1, i2 = hel.get_range(t1,t2)
    # print(i1, i2, len(hel.headache_events)-1)
    # print()
    # print()
    # print("##", hel.headache_events[i1:i2+1][-1])
    res = hel.headache_events[i1:i2+1][-1] == hel.headache_events[-1]
    if not res:
        print("Fail: %s" % sys._getframe().f_code.co_name)
    return res

def tests(hel):
    test_feb_15(hel)
    test_before_range(hel)
    test_after_range(hel)
    test_no_delta(hel)
    test_neither_in_range_before(hel)
    test_cross_dates(hel)
    test_range_boundaries(hel)
    test_range_boundary_end(hel)
