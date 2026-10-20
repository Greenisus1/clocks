"""Pure time logic for the clocks app: world clock zones, countdown timer, stopwatch."""
import time
from zoneinfo import ZoneInfo

WORLD_ZONES = [
    ("Local", None),
    ("New York", "America/New_York"),
    ("Chicago", "America/Chicago"),
    ("Denver", "America/Denver"),
    ("Los Angeles", "America/Los_Angeles"),
    ("London", "Europe/London"),
    ("Paris", "Europe/Paris"),
    ("Berlin", "Europe/Berlin"),
    ("Tokyo", "Asia/Tokyo"),
    ("Sydney", "Australia/Sydney"),
    ("Auckland", "Pacific/Auckland"),
]

def world_times(now=None):
    """[(label, 'HH:MM:SS', 'Mon 19 Oct')] for each zone."""
    now = time.time() if now is None else now
    out = []
    for label, zone in WORLD_ZONES:
        t = time.localtime(now) if zone is None else time.strftime  # placeholder
        if zone is None:
            lt = time.localtime(now)
            out.append((label, time.strftime("%H:%M:%S", lt), time.strftime("%a %d %b", lt)))
        else:
            import datetime
            dt = datetime.datetime.fromtimestamp(now, ZoneInfo(zone))
            out.append((label, dt.strftime("%H:%M:%S"), dt.strftime("%a %d %b")))
    return out

def fmt_hms(seconds, tenths=False):
    seconds = max(0.0, seconds)
    h = int(seconds // 3600); m = int((seconds % 3600) // 60); s = seconds % 60
    if tenths:
        return "%02d:%02d:%04.1f" % (h, m, s)
    return "%02d:%02d:%02d" % (h, m, int(s))

class Timer:
    """Countdown. States: idle -> running -> done. pause/resume supported."""
    def __init__(self):
        self.state = "idle"; self.duration = 0.0; self.ends_at = None; self.left_when_paused = 0.0
    def set(self, seconds):
        self.duration = max(0.0, float(seconds)); self.state = "idle"; self.ends_at = None
    def start(self, now=None):
        if self.duration <= 0: return
        now = time.monotonic() if now is None else now
        self.ends_at = now + self.duration; self.state = "running"
    def pause(self, now=None):
        if self.state != "running": return
        now = time.monotonic() if now is None else now
        self.left_when_paused = max(0.0, self.ends_at - now); self.state = "paused"
    def resume(self, now=None):
        if self.state != "paused": return
        now = time.monotonic() if now is None else now
        self.ends_at = now + self.left_when_paused; self.state = "running"
    def reset(self):
        self.state = "idle"; self.ends_at = None
    def remaining(self, now=None):
        if self.state == "running":
            now = time.monotonic() if now is None else now
            left = max(0.0, self.ends_at - now)
            if left <= 0: self.state = "done"
            return left
        if self.state == "paused": return self.left_when_paused
        if self.state == "done": return 0.0
        return self.duration

class Stopwatch:
    def __init__(self):
        self.running = False; self.started_at = None; self.acc = 0.0; self.laps = []
    def start(self, now=None):
        if self.running: return
        self.started_at = time.monotonic() if now is None else now
        self.running = True
    def stop(self, now=None):
        if not self.running: return
        now = time.monotonic() if now is None else now
        self.acc += now - self.started_at; self.running = False
    def reset(self):
        self.running = False; self.started_at = None; self.acc = 0.0; self.laps = []
    def elapsed(self, now=None):
        if self.running:
            now = time.monotonic() if now is None else now
            return self.acc + now - self.started_at
        return self.acc
    def lap(self, now=None):
        total = self.elapsed(now)
        prev = self.laps[-1][1] if self.laps else 0.0
        self.laps.append((total - prev, total))
        return self.laps[-1]
