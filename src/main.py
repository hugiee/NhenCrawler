from nhentai import NhentaiCrawler
from config import setup_logging, settings
from reader import open_reader
import asyncio
import logging

logger = logging.getLogger(__name__)

async def main():

    # Example usage of the nhentai module
    try:
        crawler = NhentaiCrawler()
        result = await crawler.search(query="榨取", sort="popular", from_page=1, page_size=4)
        if not result:
            logger.info("没有搜索到相关数据")
            return

        logger.info(f"搜到{len(result.datas)}条数据即将开始下载")
        logger.info("目录如下:")
        for idx, data in enumerate(result.datas):
            logger.info(f"「{idx}」: {data.title}")

        idx = input('请输入要下载的图片序号(以空格分隔, 不填则下载全部): ').strip().split()

        final_datas = result.datas if not idx else [result.datas[int(i)] for i in idx]
        logger.info(f"开始下载: {', '.join([data.title for data in final_datas])}")
        await crawler.start_download(final_datas)
        
    except Exception as e:
        print(e)


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())

    open_reader(library_path=settings.DEFAULT_STORAGE)