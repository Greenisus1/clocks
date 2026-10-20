import unittest
from clocklogic import Timer, Stopwatch, fmt_hms, world_times, WORLD_ZONES

class FmtTests(unittest.TestCase):
    def test_fmt(self):
        self.assertEqual(fmt_hms(0), "00:00:00")
        self.assertEqual(fmt_hms(3661), "01:01:01")
        self.assertEqual(fmt_hms(59.9), "00:00:59")
    def test_tenths(self):
        self.assertEqual(fmt_hms(61.25, tenths=True), "00:01:01.2")

class WorldTests(unittest.TestCase):
    def test_zones_return_rows(self):
        rows = world_times(0)  # epoch
        self.assertEqual(len(rows), len(WORLD_ZONES))
        for label, hms, day in rows:
            self.assertRegex(hms, r"^\d\d:\d\d:\d\d$")
    def test_london_ahead_of_chicago_at_epoch(self):
        rows = dict((l, h) for l, h, _ in world_times(0))
        self.assertEqual(rows["London"], "01:00:00")  # UTC+1 in Jan 1970
        self.assertEqual(rows["Chicago"], "18:00:00")  # UTC-6

class TimerTests(unittest.TestCase):
    def test_countdown_and_done(self):
        t = Timer(); t.set(10); t.start(now=100.0)
        self.assertAlmostEqual(t.remaining(now=104.0), 6.0)
        self.assertEqual(t.remaining(now=111.0), 0.0)
        self.assertEqual(t.state, "done")
    def test_pause_resume(self):
        t = Timer(); t.set(10); t.start(now=0.0)
        t.pause(now=4.0)
        self.assertAlmostEqual(t.remaining(now=100.0), 6.0)
        t.resume(now=50.0)
        self.assertAlmostEqual(t.remaining(now=53.0), 3.0)
    def test_reset(self):
        t = Timer(); t.set(10); t.start(now=0.0); t.reset()
        self.assertEqual(t.state, "idle")
        self.assertEqual(t.remaining(), 10.0)
    def test_zero_set_does_not_start(self):
        t = Timer(); t.set(0); t.start(now=0.0)
        self.assertEqual(t.state, "idle")

class StopwatchTests(unittest.TestCase):
    def test_run_stop(self):
        s = Stopwatch(); s.start(now=10.0)
        self.assertAlmostEqual(s.elapsed(now=15.5), 5.5)
        s.stop(now=20.0)
        self.assertAlmostEqual(s.elapsed(now=999.0), 10.0)
    def test_resume_accumulates(self):
        s = Stopwatch(); s.start(now=0.0); s.stop(now=5.0); s.start(now=10.0)
        self.assertAlmostEqual(s.elapsed(now=13.0), 8.0)
    def test_laps(self):
        s = Stopwatch(); s.start(now=0.0)
        lap1 = s.lap(now=5.0); lap2 = s.lap(now=12.0)
        self.assertAlmostEqual(lap1[0], 5.0)
        self.assertAlmostEqual(lap2[0], 7.0)
        self.assertAlmostEqual(lap2[1], 12.0)
    def test_reset(self):
        s = Stopwatch(); s.start(now=0.0); s.lap(now=3.0); s.reset()
        self.assertEqual(s.elapsed(), 0.0)
        self.assertEqual(s.laps, [])

if __name__ == '__main__':
    unittest.main()
