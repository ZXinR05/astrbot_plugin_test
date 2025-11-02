import aiofiles
import json

async def load_data() -> dict:
    """异步加载 JSON 数据"""
    try:
        async with aiofiles.open('./data/elec_query.json', mode='r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    

async def save_data(data: dict):
    """异步保存 JSON 数据"""
    async with aiofiles.open('./data/elec_query.json', mode='w', encoding='utf-8') as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=4))
    