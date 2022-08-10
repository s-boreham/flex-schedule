import datetime as dt


class AvailableSlot:
    timeStart = ""
    timeEnd = ""

    def __init__(self, timeStart):
        self.timeStart = dt.datetime.combine(dt.date.today(), dt.time.fromisoformat(timeStart))

    def setEnd(self, timeEnd):
        self.timeEnd = dt.datetime.combine(dt.date.today(), dt.time.fromisoformat(timeEnd))

        return self

    def duration(self):
        return (self.timeEnd - self.timeStart).total_seconds()

    def json(self):
        return {"timeStart": self.timeStart.strftime("%H:%M"), "timeEnd": self.timeEnd.strftime("%H:%M")}