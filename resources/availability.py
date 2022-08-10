import calendar
from datetime import date

from flask_smorest import Blueprint, abort
from flask.views import MethodView

from model.teaching_hours import TeachingHourModel
from model.event import EventModel
from model.available_slot import AvailableSlot

from schema.availability import QueryArgSchema, AvailableSlotSchema

blp = Blueprint("Availability", "availability", description="Displays available teaching times for a single teacher.")


@blp.route("/teacher/<int:teacher_id>/availability")
class ScheduleList(MethodView):

    @blp.arguments(QueryArgSchema, location="query")
    @blp.response(200)
    def get(cls, args, teacher_id):

        # parse query args
        today = date.today()
        month = today.month
        year = today.year
        
        if "year" in args:
            year = args["year"]
        if "month" in args:
            month = args["month"]

        if year < today.year:
            return {"message": "invalid year"}
        elif year == today.year and month < today.month:
            return {"message": "invalid month"}
        elif year == today.year and month == today.month:
            startDate = today
        else:
            startDate = date(year, month, 1)
        
        minDur = 1800 if "minDuration" not in args else args["minDuration"] * 60


        # load teaching hour specs from db and sort them in a list by weekday
        hours = {}
        for h in TeachingHourModel.get_valid_teacher_hours_ordered(teacher_id, startDate.isoformat()):
            if h.dayOfWeek not in hours:
                hours[h.dayOfWeek] = []
            hours[h.dayOfWeek].append(h)


        # load all confirmed events (ordered by date) from database 
        events = [
            e for e in EventModel.get_teacher_events_from_date(teacher_id, startDate.isoformat())
        ]


        # calculate available slots
        first_day_of_month, month_length = calendar.monthrange(startDate.year, startDate.month)

        slot_list = []
        for d in range(0, startDate.day-1):
            slot_list.append([])

        for d in range(startDate.day, month_length):

            slot_list.append([])

            curDay = date(startDate.year, startDate.month, d)
            curDayName = calendar.day_name[ (first_day_of_month + curDay.day - 1) %7]

            # no defined teaching hours
            if curDayName not in hours:
                continue

            # iterate over teaching hours for current week day
            for h in hours[curDayName]:                
                if h.validFrom <= curDay.isoformat() and h.validThrough >= curDay.isoformat() and h.opens != "":
                    slot = AvailableSlot(h.opens)

                    # iterate over lessons with same date
                    while len(events) > 0 and events[0].date == curDay.isoformat():
                        curEvent = events.pop(0)

                        # complete slot times and add append if long enough
                        slot.setEnd(curEvent.timeStart)
                        if slot.duration() >= minDur:
                            slot_list[d-1].append(slot.json())
                        
                        #create new slot
                        slot = AvailableSlot(curEvent.timeEnd)

                    # finish last created slot
                    slot.setEnd(h.closes)
                    
                    if slot.duration() >= minDur:
                        slot_list[d-1].append(slot.json())



        return {"slots": slot_list}, 200