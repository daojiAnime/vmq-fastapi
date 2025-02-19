<!-- markdownlint-restore -->

<div align="center">

# VMQ-FastAPI

![GitHub License](https://img.shields.io/github/license/daojiAnime/vmq-fastapi)
[![GitHub stars](https://img.shields.io/github/stars/daojiAnime/vmq-fastapi.svg)](https://github.com/daojiAnime/vmq-fastapi/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/daojiAnime/vmq-fastapi.svg)](https://github.com/daojiAnime/vmq-fastapi/network)
[![GitHub issues](https://img.shields.io/github/issues-raw/daojiAnime/vmq-fastapi)](https://github.com/daojiAnime/vmq-fastapi/issues)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/daojiAnime/vmq-fastapi/total)

</div>

## 项目结构

pass

## 前端项目

**项目地址**: [vmq-frontend https://github.com/daojiAnime/vmq-frontend](https://github.com/daojiAnime/vmq-frontend)

前端项目是基于 [vben admin v5版本](https://github.com/vbenjs/vue-vben-admin) 进行二次开发的。 `vben admin`是一个集成度高、功能丰富、易于上手的 Vue3 中后台管理框架，[daojiAnime](https://daojianime.github.io/) 使用该框架开发过个人项目非常好用，在这里推荐给大家。

#### 预览

![image-20250219100105297](https://cdn.jsdelivr.net/gh/daojiAnime/cdn@master/img/image-20250219100105297.png)

![image-20250219100201541](https://cdn.jsdelivr.net/gh/daojiAnime/cdn@master/img/image-20250219100201541.png)

![image-20250219100216235](https://cdn.jsdelivr.net/gh/daojiAnime/cdn@master/img/image-20250219100216235.png)



## 监控端

### Andorid端监控

[vmq-fastapi-apk](https://github.com/daojiAnime/vmqApk)

[vmq-fastapi-apk](https://github.com/daojiAnime/vmqApk)是根据[zwc456baby的vmqApk](https://github.com/zwc456baby/vmqApk)项目进行二次开发的。采用监听通知消息进行支付账单推送，在原有基础上增加了多租户支持。

## 开发流程

> 推荐使用 uv 安装依赖
> https://docs.astral.sh/uv/
> 或者使用 Poetry 安装依赖
> https://python-poetry.org/

### 安装依赖

在项目根目录执行`uv venv`创建虚拟环境，然后执行`uv sync`安装依赖。

```bash
uv venv -p python3.12
uv sync
```

### 配置

env.example 文件中包含了所有需要配置的变量。重命名为.env 文件，并填写相应的值。

### 安装pre-commit hook

```bash
pre-commit install
```

如果是Mac用户，可能遇到权限问题，`PermissionError: [Errno 13] Permission denied: xxx`，可以使用`sudo pre-commit install`进行安装。

### 初始化数据库

```bash
uv run app/initial_data.py
```

### 创建demo数据

```bash
uv run app/initial_demo_data.py
```

### 开发启动

`FastAPI CLI`使用`Uvicorn`作为ASGI服务器，在项目根目录执行`fastapi dev app/main.py`启动项目。生产环境则使用`fastapi run --workers 4 app/main.py`启动项目。

```bash
fastapi dev app/main.py
```
