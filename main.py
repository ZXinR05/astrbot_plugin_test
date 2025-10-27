from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
import astrbot.api.message_components as Comp
import json
import aiofiles
from queue import Queue
from astrbot.core.utils.session_waiter import (
    session_waiter,
    SessionController,
)

from .utils.api import ElecAPI

@register("Elec_Query", "XIN", "一个简单的 Elec 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        self.queue = Queue()
        self.config = config
        self.api = ElecAPI(self.config.get("backend"))
        self.frontend = self.config.get("frontend")
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

        
    
    # 注册指令的装饰器
    @filter.command("bind")
    async def bind(self, event: AstrMessageEvent):
        """这是一个 bind 指令"""
        sid = event.unified_msg_origin
        if await self.api.is_exist(sid):
            yield event.plain_result(f'您已绑定成功，通过{self.frontend}查看或更改')
        else:
            await self.api.create_user(sid)
            yield event.plain_result(f'未绑定，通过{self.frontend}进行绑定')
        

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
