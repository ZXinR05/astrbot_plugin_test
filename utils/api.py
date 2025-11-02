import httpx

from astrbot.api import logger
from .encrpy import md5


class ElecAPI:
    def __init__(self, backend_url: str):
        self.backend_url = backend_url
        self.api = {
            "addUser": "/api/v1/addUser",
            "getUser": "/api/v1/getUserByUserId",
            "getElec": "/api/v1/getElec",
            "getSchedule": "/api/v1/getScheduleByUserId",
        }

    async def create_user(self, user_id: str) -> dict:
        url = self.backend_url + self.api["addUser"]
        async with httpx.AsyncClient() as client:
            try:
                response_1 = await client.post(url, data={"userId": md5(user_id), "isAc": 0})
                response_2 = await client.post(url, data={"userId": md5(user_id), "isAc": 1})
                if response_1.json().get('code') != 200:
                    logger.error(f"创建用户失败: {response_1.json().get('msg')}")
                if response_2.json().get('code') != 200:
                    logger.error(f"创建用户失败: {response_2.json().get('msg')}")

            except httpx.RequestError as e:
                logger.error(f"请求错误: {e}")
                return {"error": str(e)}
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP 状态错误: {e}")
                return {"error": str(e)}
            
    async def get_user(self, sid:str, isac:int) -> dict:
        url = self.backend_url + self.api["getUser"]
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, data={"userId": md5(sid), "isAc": isac})
                return response.json()
            except httpx.RequestError as e:
                logger.error(f"请求错误: {e}")
                return {"error": str(e)}
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP 状态错误: {e}")
                return {"error": str(e)}
            
    async def get_elec(self, sid:str, isac:int) -> dict:
        url = self.backend_url + self.api["getElec"]
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, data={"userId": md5(sid), "isAc": isac})
                return f"{eval(response.json().get('data')):.2f}"
            except httpx.RequestError as e:
                logger.error(f"请求错误: {e}")
                return {"error": str(e)}
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP 状态错误: {e}")
                return {"error": str(e)}
            
    async def is_exist(self, sid: str) -> bool:
        room_data = await self.get_user(sid, 0)
        ac_data = await self.get_user(sid, 1)
        return room_data.get('code') == 200 and ac_data.get('code') == 200
    
    async def get_schedule(self, sid: str) -> dict:
        url = self.backend_url + self.api["getSchedule"]
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, data={"userId": md5(sid)})
                data = response.json().get('data', {})
                result = {
                    "days": data.get("remindWeek", []),
                    "hours": data.get("remindHour", []),
                    "minutes": data.get("remindMin", []),
                    "userId": data.get("userId", ""),
                }
                return result
            except httpx.RequestError as e:
                logger.error(f"请求错误: {e}")
                return {"error": str(e)}
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP 状态错误: {e}")
                return {"error": str(e)}
            
        
        
