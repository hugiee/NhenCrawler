from nhentai import NhentaiCrawler
import asyncio
import logging

logger = logging.getLogger('crawler')
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler('crawler.log', 'a', encoding='utf-8')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

async def main():

    # Example usage of the nhentai module
    try:
        crawler = NhentaiCrawler()
        result = await crawler.search('正太')

        logger.info(f"搜到{len(result.datas)}条数据即将开始下载")
        logger.info("目录如下:")
        for idx, data in enumerate(result.datas):
            logger.info(f"「{idx}」: {data.title}")
        
        await crawler.start_download(result.datas)
        
    except Exception as e:
        print(e)


if __name__ == "__main__":
    asyncio.run(main())
