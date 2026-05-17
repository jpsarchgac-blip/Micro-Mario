# time_shim.py - monkey-patches the standard `time` module with MicroPython tick helpers.
# Imported by webloop.py before anything else.
import time as _time

_BASE = _time.time()


def ticks_ms():
    return int((_time.time() - _BASE) * 1000)


def ticks_us():
    return int((_time.time() - _BASE) * 1_000_000)


def ticks_diff(a, b):
    return a - b


def ticks_add(t, d):
    return t + d


def sleep_ms(ms):
    # JS drives the loop via requestAnimationFrame; sleeping would block the browser.
    return


def sleep_us(us):
    return


_time.ticks_ms = ticks_ms
_time.ticks_us = ticks_us
_time.ticks_diff = ticks_diff
_time.ticks_add = ticks_add
_time.sleep_ms = sleep_ms
_time.sleep_us = sleep_us
