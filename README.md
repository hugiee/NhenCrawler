# NhenCrawler

## 用法
- 下载本项目到本地
- 运行`pip install -r requirements.txt` 进行依赖安装
- (可选) 如果使用uv进行管理, 可以直接使用`uv pip sync`安装依赖
- 复制`.env_template`文件为`.env`文件并进行对应修改
- 运行`python3 src/main.py`或`uv run src/main.py`

## 配置文件
```
# nhentai官网地址
NHENTAI_HOST=https://nhentai.net
# 本地下载位置
NHENTAI_STORAGE=/**/storage
```
