import httpx

from astrbot.api import logger
from encrpy import md5


class ElecAPI:
    def __init__(self, backend_url: str):
        self.backend_url = backend_url
        self.api = {
            "addUser": "/api/v1/addUser",
            "getUser": "/api/v1/getUserByUserId",
        }

    async def create_user(self, user_id: str) -> dict:
        url = self.backend_url + self.api["addUser"]
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json={"userId": md5(user_id)})
                return response.json()
            except httpx.RequestError as e:
                logger.error(f"请求错误: {e}")
                return {"error": str(e)}
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP 状态错误: {e}")
                return {"error": str(e)}
            
    async def get_user(self, user_id: str) -> dict:
        url = self.backend_url + self.api["getUser"]
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json={"userId": md5(user_id)})
                return response.json()
            except httpx.RequestError as e:
                logger.error(f"请求错误: {e}")
                return {"error": str(e)}
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP 状态错误: {e}")
                return {"error": str(e)}
            
    async def is_exist(self, user_id: str) -> bool:
        user_data = await self.get_user(user_id)
        if user_data.get('status') == 'success':
            if user_data.get('data').get('aid'):
                return True
        return False
            
        
        
