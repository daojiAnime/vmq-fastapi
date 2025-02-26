from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import tomllib


def get_project_version() -> str | Any:
    try:
        # 方法1：通过已安装的包元数据获取（需要先安装包）
        return version("vmq-fastapi")
    except PackageNotFoundError:
        # 方法2：直接解析pyproject.toml（开发环境使用）
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        with pyproject_path.open("rb") as f:
            config = tomllib.load(f)
        return config["project"]["version"]


__version__ = get_project_version()
