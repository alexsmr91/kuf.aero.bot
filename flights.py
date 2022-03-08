from datetime import datetime
import pytz
tz = pytz.timezone('Europe/Samara')

class Flights:

    def __init__(self, *args, **kwargs):
        self.aw_time, self.aw_date, self.airlines, self.dest_city, self.dest_airport, self.status, self.rl_time, self.rl_date, self.combi_flights, self.arr_flag, self.flight = args

    def __eq__(self, other):
        return self.aw_time == other.aw_time and self.aw_date == other.aw_date and self.airlines == other.airlines and self.dest_city == other.dest_city and self.dest_airport == other.dest_airport and self.status == other.status and self.rl_time == other.rl_time and self.rl_date == other.rl_date and self.combi_flights == other.combi_flights and self.arr_flag == other.arr_flag and self.flight == other.flight

    def difference(self, other):
        res = ''
        if self.aw_time != other.aw_time:
            res = f'{res}at+'
        if self.aw_date != other.aw_date:
            res = f'{res}ad+'
        if self.airlines != other.airlines:
            res = f'{res}al+'
        if self.dest_city != other.dest_city:
            res = f'{res}dc+'
        if self.dest_airport != other.dest_airport:
            res = f'{res}da+'
        if self.status != other.status:
            res = f'{res}s+'
        if self.rl_time != other.rl_time:
            res = f'{res}rt+'
        if self.rl_date != other.rl_date:
            res = f'{res}rd+'
        #if self.combi_flights != other.combi_flights:
            #res = f'{res}cf+'
        return res.strip('+')

    def __repr__(self):
        if self.rl_time != self.aw_time:
            res = f'{self.flight}  ({self.airlines})\n<s>{self.aw_time}</s>\n{self.rl_time}\n{self.dest_city}  ({self.dest_airport})\n{self.status}\n'
        else:
            res = f'{self.flight}  ({self.airlines})\n{self.rl_time}\n{self.dest_city}  ({self.dest_airport})\n{self.status}\n'
        return res

    def get_aw_date(self) -> datetime:
        st = f'{self.aw_date} {self.aw_time}+0400'
        frm = '%d.%m.%Y %H:%M%z'
        return datetime.strptime(st, frm).astimezone(tz)

    def get_rl_date(self) -> datetime:
        st = f'{self.rl_date} {self.rl_time}+0400'
        frm = '%d.%m.%Y %H:%M%z'
        return datetime.strptime(st, frm).astimezone(tz)
