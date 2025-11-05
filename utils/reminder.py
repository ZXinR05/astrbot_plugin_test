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

    async def get_schedule_list(self):
        jobs = self.scheduler.get_schedule_list()
        jobs_summary = ''
        for i, job in enumerate(jobs):
        # 格式化下次运行时间。如果 next_run_time 为 None (已完成或暂停)，则显示 N/A
            next_run = "N/A (Finished/Paused)"
            if job.next_run_time:
                # 统一时间格式，例如：2025-11-05 10:30:00 +0800
                next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')

            job_info_str = (
                f"--- 任务 {i+1} ---\n"
                f"  ID:          {job.id}\n"
                f"  函数:        {job.func.__name__}\n"
                f"  触发器类型:  {type(job.trigger).__name__}\n"
                f"  下次运行时间: {next_run}\n"
                f"  执行参数 (Args): {job.args}\n"
                f"  执行参数 (Kwargs): {job.kwargs}\n"
            )
            jobs_summary += job_info_str
        return jobs_summary

    async def unregister(self, sid:str):
        self.scheduler.remove_all(md5(sid))

    async def start(self):
        self.scheduler.start()

    async def shutdown(self):
        self.scheduler.shutdown()
