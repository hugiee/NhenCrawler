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
# 网络代理
HTTP_PROXY=http://127.0.0.1:7890
```

## 计划

- 全路径可配置化, 支持根据模板的自定义上传爬虫脚本并将结果进行指定模式的返回
- 进行项目转whl, 支持对指定脚本直接进行控制台打开的操作
- 添加Docker支持, Docker-Compose支持