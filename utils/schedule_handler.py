from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable
from astrbot.api import logger

class ScheduleHandler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def add_task(self, task:Callable, args:list, id:str, days:str, hour:str, minute:str):
        logger.info(f"添加定时任务: id={id}, days={days}, hour={hour}, minute={minute}, args={args}")
        self.scheduler.add_job(task, trigger=CronTrigger(day_of_week=days, hour=hour, minute=minute), id=id, args=args)

    def add_all(self, task:Callable, args:list, data:dict):
        days = ','.join(data.get('days'))
        hours = data.get('hours')
        minutes = data.get('minutes')
        for i, (h, m) in enumerate(zip(hours, minutes)):
            job_id = f"{data.get('userId')}_{i}"
            self.add_task(task, args, job_id, days, h, m)


    def remove_all(self, user_id: str):
        for job in self.scheduler.get_jobs():
            if job.id.startswith(user_id):
                self.scheduler.remove_job(job.id)

    def start(self):
        self.scheduler.start()
    
    def shutdown(self):
        self.scheduler.shutdown(wait=False)

    def get_schedule_list(self):
        return self.scheduler.get_jobs()
