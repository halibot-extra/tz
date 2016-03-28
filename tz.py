from halibot import HalModule
from datetime import datetime, timedelta
from pytz import timezone, UnknownTimeZoneError, utc
import json

def is_valid_tz(tz):
    try:
        timezone(tz)
        return True
    except UnknownTimeZoneError:
        return False

FMT = '%Y-%m-%d %H:%M:%S %Z%z'
def time_for(tz):
    return utc.localize(datetime.utcnow())
              .astimezone(timezone(tz))
              .strftime(FMT)


TZLINK = 'https://en.wikipedia.org/wiki/List_of_tz_database_time_zones'

class TZ(HalModule):
    def init(self):
        self.dbpath = self.config['tz-path']
        self.load()

    def load(self):
        try:
            with open(self.dbpath, 'r') as f:
                self.users = json.loads(f.read())
        except FileNotFoundError:
            self.users = {}
            self.save()
    
    def save(self):
        with open(self.dbpath, 'w') as f:
            f.write(json.dumps(self.users))

    def receive(self, msg):
        words = msg.body.split(' ')
        cmd = words[0]
        
        if cmd != '!tz':
            return

        if len(words) == 2:
            if words[1] in self.users:
                self.reply(msg, body=time_for(self.users[words[1]]))
            else:
                self.reply(msg, body='Unknown user')
        elif len(words) > 3:
            if words[2] == '=':
                tz = '_'.join(words[3:]) 
                if is_valid_tz(tz):
                    self.users[words[1]] = tz
                    self.save()
                    self.reply(msg, body='Associated user and timezone')
                else:
                    self.reply(msg, body='I don\'t know that timezone. See ' +
                            TZLINK)
