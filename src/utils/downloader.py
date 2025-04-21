import asyncio
import aiofiles
import aiohttp
import os
import logging

from aiohttp import ClientSession
from config import settings

logger = logging.getLogger('crawler')

known_ext = ['jpg', 'png', 'webp']

# 异步下载单张图片
async def download_image(session: ClientSession, url: str, save_path: str):
    extension = url.split(".")[-1]

    code = await _do_download(session=session, url=url, save_path=save_path)
    if code == 404:
        for ext in [item for item in known_ext if item != extension]:
            new_url = url.replace(extension, ext)
            code = await _do_download(session=session, url=new_url, save_path=save_path)
            if code == 200:
                break
        if code == 404:
            logger.error(f"❌ 下载失败 {url}, 404")

async def _do_download(session: ClientSession, url: str, save_path: str):
    retry_num = 3
    for count in range(retry_num):
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(save_path, 'wb') as f:
                        await f.write(await resp.read())
                    return 200
                elif resp.status == 404:
                    return 404
                else:
                    logger.warning(f"⚠️ 第{count + 1}次尝试, 下载失败 {url}: {resp.status}")
                
                await asyncio.sleep(1)
        except Exception as e:
            logger.warning(f"⚠️ 第{count + 1}次尝试, 下载失败 {url}: {e}")
            await asyncio.sleep(1)
    
    logger.error(f"❌ 下载失败 {url}")
    
    return -1

# 批量下载
async def download_images(url_list, save_dir):
    headers = {
        "Host": "i2.nhentai.net",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "*/*",
    }
    proxy = settings.DOWNLOAD_PROXY

    timeout = aiohttp.ClientTimeout(
        total=60,           # 整个请求超时
        connect=30,          # 连接超时
        sock_read=30,        # 读超时
        sock_connect=30      # 套接字连接超时
    )

    async with ClientSession(headers=headers, proxy=proxy, timeout=timeout) as session:
        tasks = []
        for idx, url in enumerate(url_list):
            filename = os.path.basename(url)
            save_path = os.path.join(save_dir, filename)
            tasks.append(download_image(session, url, save_path))
        
        semaphore = asyncio.Semaphore(3)
        async with semaphore:
            # 限制并发下载数量
            await asyncio.gather(*tasks)


if __name__ == "__main__":
    # 示例用法
    urls = [
        "https://i2.nhentai.net/galleries/2938951/2.jpg",
    ]
    save_directory = "/Users/hugiee/PycharmProjects/spider/storage/nhentai/(ShotaFes16)) [Aisukureyo (Hoshikuzu Noyu)] 29-sai Gouhou Shota ｜29歲合法正太 (Dungeon Meshi) [Chinese] [貓漢化]"

    asyncio.run(download_images(urls, save_directory))