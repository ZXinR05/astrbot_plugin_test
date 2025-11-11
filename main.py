from astrbot.api.event import filter, AstrMessageEvent, MessageChain
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
import astrbot.api.message_components as Comp
from queue import Queue
from .utils.data_handler import load_data, save_data
from .utils.api import ElecAPI
from .utils.encrpy import md5
from .utils.reminder import Reminder

@register("Elec_Query", "XIN", "一个简单的 Elec 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        self.queue = Queue()
        self.config = config
        self.api = ElecAPI(self.config.get("backend"))
        self.frontend = self.config.get("frontend")
        self.reminder = Reminder(self.api)
        self.schedule_data = {}
        self.user_map = {}
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        self.schedule_data = await load_data()
        self.user_map = self.schedule_data.get('user_map', {})
        for sid, user_id in self.user_map.items():
            await self.reminder.register(self.reminder_task, [sid], sid)
        await self.reminder.start()
            
    
    # 注册指令的装饰器
    @filter.command("bind")
    async def bind(self, event: AstrMessageEvent):
        """这是一个 bind 指令"""
        sid = event.unified_msg_origin
        self.user_map[sid] = md5(sid)
        if await self.api.is_exist(sid):
            if await self.api.is_completed(sid):   
                yield event.plain_result(f'您已绑定成功，请通过 {self.frontend}/{self.user_map[sid]} 查看或更改')
            else:
                yield event.plain_result(f'信息不完整，请通过 {self.frontend}/{self.user_map[sid]} 完善信息')
                return
        else:
            await self.api.create_user(sid)
            yield event.plain_result(f'还未绑定，请通过 {self.frontend}/{self.user_map[sid]} 进行绑定')
            return

        self.schedule_data['user_map'] = self.user_map
        await save_data(self.schedule_data)
    
    @filter.command("dian")
    async def dian(self, event: AstrMessageEvent):
        """这是一个 dian 指令"""
        sid = event.unified_msg_origin
        self.user_map[sid] = md5(sid)
        if not await self.api.is_exist(sid):
            yield event.plain_result(f'未绑定，请通过 /bind 进行绑定')
            return
        if not await self.api.is_completed(sid):
            yield event.plain_result(f'信息不完整，请通过 {self.frontend}/{self.user_map[sid]} 完善信息')
            return
        await self.reminder.register(self.reminder_task, [sid], sid)
        room_elec = await self.api.get_elec(sid, 0)
        ac_elec = await self.api.get_elec(sid, 1)
        yield event.plain_result(f'当前房间电量剩余为: {room_elec}，空调电量剩余为: {ac_elec}')
        
        self.schedule_data['user_map'] = self.user_map
        await save_data(self.schedule_data)

    @filter.command("chart")
    async def chart(self, event: AstrMessageEvent):
        sid = event.unified_msg_origin
        self.user_map[sid] = md5(sid)
        if not await self.api.is_exist(sid):
            yield event.plain_result(f'未绑定，请通过 /bind 进行绑定')
            return
        if not await self.api.is_completed(sid):
            yield event.plain_result(f'信息不完整，请通过 {self.frontend}/{self.user_map[sid]} 完善信息')
            return
        
        imgbase64 = await self.api.get_line_chart(sid, 0)
        chain = [
            Comp.Image.fromBase64(imgbase64)
        ]
        yield event.chain_result(chain)
        

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("debug")
    async def debug(self, event: AstrMessageEvent):
        """这是一个 debug 指令"""
        yield event.plain_result(await self.reminder.get_schedule_list())

    async def reminder_task(self, sid: str, scheduler_id: str='Undefined'):
        """这是一个定时提醒任务的示例方法"""
        room_elec = await self.api.get_elec(sid, 0)
        ac_elec = await self.api.get_elec(sid, 1)

        logger.info(f'Scheduler: {scheduler_id} 正在向SID: {sid} 执行任务!')

        message = MessageChain().message(f"[自动提醒]当前房间电量剩余为: {room_elec}，空调电量剩余为: {ac_elec}")
        await self.context.send_message(sid, message_chain=message)
        

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        self.schedule_data['user_map'] = self.user_map
        await save_data(self.schedule_data)
        for sid, user_id in self.user_map.items():
            await self.reminder.unregister(sid)
        await self.reminder.shutdown()
