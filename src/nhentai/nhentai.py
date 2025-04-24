import requests
import json
from core import SearchResult, TitleAndId, Crawler
import asyncio
from config import settings
from lxml import etree
from typing import List
import logging

logger = logging.getLogger("crawler")


class NhentaiCrawler(Crawler):

    def __init__(self):
        super().__init__(host=settings.DEFAULT_HOST, proxy=settings.HTTP_PROXY)
        self.proxies = (
            {"http": settings.HTTP_PROXY, "https": settings.HTTP_PROXY}
            if settings.HTTP_PROXY
            else None
        )

    async def search(self, **kwargs) -> SearchResult:
        """
        Searches for doujins on nhentai.net using the provided query string.
        Returns a list of dictionaries containing doujin data.

        :param query: The search query string.
        :param sort: The sorting method (optional). popular, popular-today, popular-week.
        :param from_page: The starting page number (optional).
        :param page_size: The size of page (optional).
        """
        url = f"{settings.DEFAULT_HOST}/search"
        params = {}
        from_page = kwargs.get("from_page", 1)
        page_size = kwargs.get("page_size", -1)
        if kwargs.get("query"):
            params["q"] = kwargs["query"]
        if kwargs.get("sort"):
            params["sort"] = kwargs["sort"]

        response = requests.get(
            url,
            params=params,
            proxies=self.proxies,
            timeout=(60.0, 60.0),
        )

        if response.status_code != 200:
            return None

        elems = etree.HTML(response.text, parser=etree.HTMLParser(encoding="utf-8"))
        datas = []

        if not elems.xpath('//div[@class="gallery"]'):
            return None

        parse_task = []
        if from_page <= 1:
            parse_task.append(self._parse_main_page(elems=elems))

        last_num_ele = elems.xpath(
            '//section[@class="pagination"]/a[@class="last"]/@href'
        )
        last_num = 1
        if last_num_ele:
            last_num = int(last_num_ele[0].split("=")[-1])
            for idx in range(
                max(2, from_page), min(last_num + 1, page_size + from_page)
            ):
                parse_task.append(self._do_search(params=params, page_number=idx))

        semaphore = asyncio.Semaphore(3)
        async with semaphore:
            results = await asyncio.gather(*parse_task)
            datas = [item for sublist in results for item in sublist]

        return SearchResult(datas=datas, pageNum=last_num)

    async def get_imgs(self, doujin: TitleAndId, **kwargs) -> List[str]:
        media_id, page_num, extension = self._get_meta_data(doujin.id)
        logger.info(
            f"➡️ 开始下载: {doujin.title}, Media ID: {media_id}, 页数: {page_num}, 文件后缀: {extension}"
        )

        imgs = []
        for idx in range(1, page_num + 1):
            imgs.append(
                f"https://i2.nhentai.net/galleries/{media_id}/{idx}.{extension}"
            )
        return imgs

    def _get_meta_data(self, doujin_id: str):
        url = f"{settings.DEFAULT_HOST}/g/{doujin_id}"
        response = requests.get(url, proxies=self.proxies, timeout=(60.0, 60.0))

        if response.status_code != 200:
            return None

        elems = etree.HTML(response.text, parser=etree.HTMLParser(encoding="utf-8"))
        extension = elems.xpath('//meta[@itemprop="image"]/@content')[0].split(".")[-1]
        script = elems.xpath("//body/script/text()")[-1]
        metadata = json.loads(
            script.split('"')[-2].encode("utf-8").decode("unicode_escape")
        )
        return metadata["media_id"], metadata["num_pages"], extension

    async def _do_search(self, params: dict, page_number: int) -> List[TitleAndId]:
        url = f"{settings.DEFAULT_HOST}/search"
        params["page_number"] = page_number
        response = requests.get(
            url,
            params=params,
            proxies=self.proxies,
            timeout=(60.0, 60.0),
        )
        if response.status_code != 200:
            return []

        return await self._parse_main_page(
            elems=etree.HTML(response.text, parser=etree.HTMLParser(encoding="utf-8"))
        )

    async def _parse_main_page(self, elems) -> List[TitleAndId]:
        a_elems = elems.xpath('//a[@class="cover"]')
        datas = []
        for a_elem in a_elems:
            title = a_elem.xpath('./div[@class="caption"]/text()')[0]
            doujin_id = a_elem.xpath("./@href")[0].split("/")[-2]
            datas.append(TitleAndId(title=title, id=doujin_id))
        return datas
