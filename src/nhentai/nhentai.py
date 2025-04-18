import requests
import os
import json
from .nhentai_struct import SearchResult, TitleAndId
import asyncio
from config import settings
from lxml import etree
from typing import List
from utils.downloader import download_images
import logging

logger = logging.getLogger('crawler')

class NhentaiCrawler:

    def __init__(self):
        self.history = os.path.join(settings.NHENTAI_STORAGE, '.history')
        os.path.exists(settings.NHENTAI_STORAGE) or os.makedirs(settings.NHENTAI_STORAGE, exist_ok=True)
        with open(self.history, 'w', encoding='utf-8') as his:
            pass

    async def search(self, query: str) -> SearchResult:
        """
        Searches for doujins on nhentai.net using the provided query string.
        Returns a list of dictionaries containing doujin data.
        """
        url = f'{settings.NHENTAI_HOST}/search'
        params = {'q': query}
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return None

        elems = etree.HTML(response.text, parser=etree.HTMLParser(encoding='utf-8'))
        datas = []

        parse_task = [self._parse_main_page(elems=elems)]
        
        last_num_ele = elems.xpath('//section[@class="pagination"]/a[@class="last"]/@href')
        last_num = 1
        if last_num_ele:
            last_num = int(last_num_ele[0].split('=')[-1])

        for idx in range(2, last_num + 1):
            parse_task.append(self._do_search(query=query, page_number=idx))

        results = await asyncio.gather(*parse_task)
        datas = [item for sublist in results for item in sublist]

        return SearchResult(datas=datas, pageNum=last_num)
    
    async def download(self, doujins: List[TitleAndId]):
         for doujin in doujins:
            if self.check_downloaded(doujin.id):
                logger.info(f"✅ {doujin.title} 下载完成!")
                continue
            await self._do_download(doujin)
            logger.info(f"✅ {doujin.title} 下载完成!")
            self.set_finished(doujin.id)
    
    async def _do_download(self, doujin: TitleAndId):
        storage_path = os.path.join(settings.NHENTAI_STORAGE, doujin.title)

        if not os.path.exists(storage_path):
            os.makedirs(storage_path, exist_ok=True)

        media_id, page_num, extension = self._get_meta_data(doujin.id)
        logger.info(f"➡️ 开始下载: {doujin.title}, Media ID: {media_id}, 页数: {page_num}, 文件后缀: {extension}")

        imgs = []
        for idx in range(1, page_num + 1):
            imgs.append(f"https://i2.nhentai.net/galleries/{media_id}/{idx}.{extension}")
        
        await download_images(imgs, storage_path)

    def _get_meta_data(self, doujin_id: str):
        url = f'{settings.NHENTAI_HOST}/g/{doujin_id}'
        response = requests.get(url)

        if response.status_code != 200:
            return None
        
        elems = etree.HTML(response.text, parser=etree.HTMLParser(encoding='utf-8'))
        extension = elems.xpath('//meta[@itemprop="image"]/@content')[0].split(".")[-1]
        script = elems.xpath('//body/script/text()')[-1]
        metadata = json.loads(script.split('"')[-2].encode('utf-8').decode('unicode_escape'))
        return metadata['media_id'], metadata['num_pages'], extension

    async def _do_search(self, query: str, page_number: int) -> List[TitleAndId]:
        url = f'{settings.NHENTAI_HOST}/search'
        params = {'q': query, 'page': page_number}
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return []
        
        return await self._parse_main_page(elems=etree.HTML(response.text, parser=etree.HTMLParser(encoding='utf-8')))

    async def _parse_main_page(self, elems) -> List[TitleAndId]:
        a_elems = elems.xpath('//a[@class="cover"]')
        datas = []
        for a_elem in a_elems:
            title = a_elem.xpath('./div[@class="caption"]/text()')[0]
            doujin_id = a_elem.xpath('./@href')[0].split('/')[-2]
            datas.append(TitleAndId(title=title, id=doujin_id))
        return datas
    
    def set_finished(self, doujin_id: str):
        with open(self.history, 'a', encoding='utf-8') as his:
                his.write(doujin_id + '\n')
    
    def check_downloaded(self, doujin_id: str) -> bool:
        with open(self.history, 'r', encoding='utf-8') as his:
            for line in his.readlines():
                if line.strip() == doujin_id.strip():
                    return True
        
        return False