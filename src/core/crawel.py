from config import settings
from .crawel_struct import SearchResult, TitleAndId
from urllib.parse import urlparse
from utils.downloader import download_images
from typing import List
import os
import logging

logger = logging.getLogger('crawler')

class Crawler:

    def __init__(self, host: str = settings.DEFAULT_HOST):
        self.domain = urlparse(host).netloc
        self.history = os.path.join(settings.DEFAULT_STORAGE, '.history')
        os.path.exists(settings.DEFAULT_STORAGE) or os.makedirs(settings.DEFAULT_STORAGE, exist_ok=True)
        with open(self.history, 'w', encoding='utf-8') as his:
            pass
    
    async def search(self, query: str) -> SearchResult:
        """基本检索"""
        pass

    async def get_imgs(self, doujin: TitleAndId) -> List[str]:
        """获取图片列表"""
        pass
    
    async def start_download(self, doujins: List[TitleAndId]):
        for doujin in doujins:
            if self.check_downloaded(doujin.id):
                logger.info(f"✅ {doujin.title} 下载完成!")
                continue
            imgs = await self.get_imgs(doujin)
            if not imgs:
                logger.warring(f"⚠️ {doujin.title} 图片列表为空!")
                continue
            doujin.imgs = imgs
            await self._download(doujin)
            logger.info(f"✅ {doujin.title} 下载完成!")
            self.set_finished(doujin.id)
    
    async def _download(self, doujin: TitleAndId):
        storage_path = os.path.join(settings.DEFAULT_STORAGE, doujin.title)

        if not os.path.exists(storage_path):
            os.makedirs(storage_path, exist_ok=True)

        if doujin.imgs:
            await download_images(doujin.imgs, storage_path)
    
    def set_finished(self, doujin_id: str):
        with open(self.history, 'a', encoding='utf-8') as his:
                his.write(f"{self.domain}:{doujin_id}\n")
    
    def check_downloaded(self, doujin_id: str) -> bool:
        with open(self.history, 'r', encoding='utf-8') as his:
            for line in his.readlines():
                if line.strip() == f"{self.domain}:{doujin_id.strip()}":
                    return True
        
        return False