import aiohttp
import aiohttp_socks
import asyncio

async def check_proxy(proxy: str) -> bool:
    url = 'http://www.telegram.org'  # Замените на нужный вам URL для проверки
    try:
        proxy_url = f'socks5://{proxy}'
        connector = aiohttp_socks.ProxyConnector.from_url(proxy_url)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url, timeout=10) as response:
                print(response.status)
                if response.status == 200:
                    return True
                else:
                    return False
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(e)
        return False
    except Exception as e:
        print(e)

