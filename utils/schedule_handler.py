from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable
from astrbot.api import logger

class ScheduleHandler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def add_task(self, task:Callable, args:list, job_id:str, days:str, hour:str, minute:str):
        logger.info(f"Scheduler:{id(self.scheduler)}, 添加定时任务: job_id={job_id}, days={days}, hour={hour}, minute={minute}, args={args}")
        self.scheduler.add_job(task, trigger=CronTrigger(day_of_week=days, hour=hour, minute=minute), id=job_id, args=args)

    async def add_all(self, task:Callable, args:list, data:dict):
        days = ','.join(data.get('days'))
        hours = data.get('hours')
        minutes = data.get('minutes')
        for i, (h, m) in enumerate(zip(hours, minutes)):
            job_id = f"{data.get('userId')}_{i}"
            await self.add_task(task, args, job_id, days, h, m)


    async def remove_all(self, user_id: str):
        for job in self.scheduler.get_jobs():
            if job.id.startswith(user_id):
                self.scheduler.remove_job(job.id)

    async def start(self):
        self.scheduler.start()
    
    async def shutdown(self):
        if self.scheduler is not None:
            shutdown_task = self.scheduler.shutdown(wait=False)
            if shutdown_task is not None:
                await shutdown_task


    async def get_schedule_list(self):
        return self.scheduler.get_jobs()
