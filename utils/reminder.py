from .schedule_handler import ScheduleHandler
from .api import ElecAPI
from .encrpy import md5
from typing import Callable
from astrbot.api import logger

class Reminder:
    def __init__(self, api: ElecAPI):
        self.scheduler = ScheduleHandler()
        self.api = api

    async def register(self, task:Callable, args:list, sid:str):
        data = await self.api.get_schedule(sid)
        await self.unregister(sid)
        self.scheduler.add_all(task, args, data)

    async def unregister(self, sid:str):
        self.scheduler.remove_all(md5(sid))

    async def start(self):
        self.scheduler.start()

    async def shutdown(self):
        self.scheduler.shutdown()
