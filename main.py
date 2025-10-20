from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import astrbot.api.message_components as Comp
import json
import aiofiles
from queue import Queue
from astrbot.core.utils.session_waiter import (
    session_waiter,
    SessionController,
)

@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        self.room_data = {}
        self.aid = None
        self.area_id = None
        self.area_name = None
        self.building_id = None
        self.building_name = None
        self.floor_id = None
        self.floor_name = None
        self.room_id = None
        self.room_name = None
        self.queue = Queue()
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        
        async with aiofiles.open('data/plugins/astrbot_plugin_test/room.json', 'r', encoding='utf-8') as f:
            self.room_data = json.loads(await f.read())
        self.queue.put('location')
    
    # 注册指令的装饰器
    @filter.command("bind")
    async def bind(self, event: AstrMessageEvent):
        """这是一个 bind 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        try:
            yield event.plain_result("下面开始绑定，请在60秒内做出响应。")
            msg = "请选择区域:\n"
            for i, loc in enumerate(self.room_data.get('locList', []), start=1):
                msg += f'{i}.{loc.get("name")}\n'
            yield event.plain_result(msg)

            @session_waiter(timeout=60, record_history_chains=False)
            async def wait_for_response(controller: SessionController, event: AstrMessageEvent):
                inp = event.message_str
                try:
                    method = self.queue.get_nowait()
                    msg = "请选择:\n"
                    match method:
                        case 'location':
                            loc_i = eval(inp) - 1
                            loc = self.room_data.get('locList', [])[loc_i]
                            self.aid = loc.get('aid')
                            if loc.get('buildingList', None) is not None:
                                for i, building in enumerate(loc.get('buildingList', []), start=1):
                                    msg += f'{i}.{building.get("building")}\n'
                                self.queue.put('building')
                            elif loc.get('areaList', None) is not None:
                                for i, area in enumerate(loc.get('areaList', []), start=1):
                                    msg += f'{i}.{area.get("areaname")}\n'
                                self.queue.put('area')
                        case 'area':
                            area_i = eval(inp) - 1
                            area = loc.get('areaList', [])[area_i]
                            self.area_id = area.get('area')
                            self.area_name = area.get('areaname')
                            for i, building in enumerate(area.get('buildingList', []), start=1):
                                msg += f'{i}.{building.get("building")}\n'
                            self.queue.put('building')
                        case 'building':
                            building_i = eval(inp) - 1
                            building = loc.get('buildingList', area.get('buildingList', []))[building_i]
                            self.building_id = building.get('buildingid')
                            self.building_name = building.get('building')
                            if building.get('floorList', None) is not None:
                                for i, floor in enumerate(building.get('floorList', []), start=1):
                                    msg += f'{i}.{floor.get("floor")}\n'
                                self.queue.put('floor')
                        case 'floor':
                            floor_i = eval(inp) - 1
                            floor = building.get('floorList', [])[floor_i]
                            self.floor_id = floor.get('floorid')
                            self.floor_name = floor.get('floor')
                            if floor.get('roomList', None) is not None:
                                for i, room in enumerate(floor.get('roomList', []), start=1):
                                    msg += f'{i}.{room.get("room")}\n'
                                self.queue.put('room')
                        case 'room':
                            room_i = eval(inp) - 1
                            room = floor.get('roomList', [])[room_i]
                            self.room_id = room.get('roomid')
                            self.room_name = room.get('room')
                            msg = '完成'
                            
                    if not self.queue.empty():
                        await event.send(event.plain_result(msg))
                        controller.keep(timeout=60, reset_timeout=True)
                    else:
                        controller.stop()
                        
                except TypeError:
                    event.send(event.plain_result("输入类型错误，请重新绑定。"))
                    logger.error('[bind]输入类型错误')
                    controller.stop()
                except IndexError:
                    event.send(event.plain_result("输入索引错误，请重新绑定。"))
                    logger.error('[bind]输入索引错误')
                    controller.stop()


        except Exception as e:
            logger.error(f"[bind]发生错误: {e}")
            return


        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息
        

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
