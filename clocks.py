#!/usr/bin/env python3
"""Clocks: world clock, countdown timer and stopwatch in one terminal app."""
import curses, os, sys, time

try:
    import pi18n
except ImportError:
    pi18n = None

# English UI strings; the Translations app owns every language via ~/pi-translations.
DEFAULT_STRINGS = {
 'TABS': '1 World clock   2 Timer   3 Stopwatch        Esc/q quit',
 'WORLD_TITLE': 'WORLD CLOCK',
 'TIMER_TITLE': 'TIMER',
 'TIMER_IDLE': 'T set minutes (e.g. 5 or 0.5) | Space start/pause | R reset',
 'TIMER_PROMPT': 'Minutes: ',
 'TIMER_DONE': 'TIME IS UP!',
 'TIMER_SET': 'Set: {dur}   Left: {left}',
 'SW_TITLE': 'STOPWATCH',
 'SW_KEYS': 'Space start/stop | L lap | R reset',
 'SW_LAPS': 'Laps (split / total):',
 'STATE_RUNNING': 'running',
 'STATE_PAUSED': 'paused',
 'STATE_DONE': 'done',
 'STATE_IDLE': 'set',
}
VERSION = '1.0.0'

def loop(s):
    from clocklogic import Timer, Stopwatch, fmt_hms, world_times
    from ui import put
    S = pi18n.load('clocks', DEFAULT_STRINGS) if pi18n else DEFAULT_STRINGS
    s.timeout(50)
    tab = 1
    timer = Timer(); sw = Stopwatch()
    editing = False
    while True:
        h, w = s.getmaxyx(); s.erase()
        put(s, 0, 1, S['TABS'], curses.A_BOLD)
        if tab == 1:
            put(s, 2, 1, S['WORLD_TITLE'], curses.A_BOLD)
            for i, (label, hms, day) in enumerate(world_times()):
                put(s, 3 + i, 2, '%-14s %s   %s' % (label, hms, day))
        elif tab == 2:
            put(s, 2, 1, S['TIMER_TITLE'], curses.A_BOLD)
            state = {'running': S['STATE_RUNNING'], 'paused': S['STATE_PAUSED'], 'done': S['STATE_DONE'], 'idle': S['STATE_IDLE']}[timer.state]
            left = timer.remaining()
            put(s, 4, 2, fmt_hms(left), curses.A_BOLD)
            put(s, 6, 2, S['TIMER_SET'].format(dur=fmt_hms(timer.duration), left=fmt_hms(left)) + '   [%s]' % state)
            if timer.state == 'done':
                put(s, 8, 2, S['TIMER_DONE'], curses.A_BOLD | curses.A_REVERSE)
                curses.beep()
            else:
                put(s, 8, 2, S['TIMER_IDLE'])
        else:
            put(s, 2, 1, S['SW_TITLE'], curses.A_BOLD)
            put(s, 4, 2, fmt_hms(sw.elapsed(), tenths=True), curses.A_BOLD)
            put(s, 6, 2, S['SW_KEYS'] + ('   [%s]' % (S['STATE_RUNNING'] if sw.running else S['STATE_PAUSED'])))
            if sw.laps:
                put(s, 8, 2, S['SW_LAPS'])
                for i, (split, total) in enumerate(sw.laps[-(h - 11):]):
                    put(s, 9 + i, 2, '%2d. %s / %s' % (len(sw.laps) - min(len(sw.laps), h - 11) + i + 1, fmt_hms(split), fmt_hms(total)))
        s.refresh()
        key = s.getch()
        if key in (27, ord('q')): return
        if key == ord('1'): tab = 1
        elif key == ord('2'): tab = 2
        elif key == ord('3'): tab = 3
        elif tab == 2:
            if key == ord(' '):
                if timer.state == 'running': timer.pause()
                elif timer.state == 'paused': timer.resume()
                elif timer.state in ('idle', 'done'): timer.start()
            elif key in (ord('r'), ord('R')): timer.reset()
            elif key in (ord('t'), ord('T')):
                curses.echo()
                put(s, 10, 2, S['TIMER_PROMPT'])
                s.refresh()
                s.timeout(-1)  # block for input; the main loop's 50ms tick would kill getstr
                try:
                    raw = s.getstr(10, 2 + len(S['TIMER_PROMPT']), 8).decode().strip()
                    timer.set(float(raw) * 60.0)
                except (ValueError, curses.error):
                    pass
                finally:
                    s.timeout(50)
                    curses.noecho()
        elif tab == 3:
            if key == ord(' '):
                if sw.running: sw.stop()
                else: sw.start()
            elif key in (ord('l'), ord('L')): sw.lap()
            elif key in (ord('r'), ord('R')): sw.reset()

if __name__ == '__main__':
    if '--version' in sys.argv:
        print(VERSION)
    else:
        from ui import run
        raise SystemExit(run(loop))
