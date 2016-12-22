# encoding: utf-8
# module time
# from (built-in)
# by generator 1.136
import datetime


def yesterday():
    return datetime.date.today() + datetime.timedelta(days=-1)
