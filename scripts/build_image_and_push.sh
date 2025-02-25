#!/bin/bash
###
 # @Author: Daoji daoji.chang@gmail.com
 # @Date: 2024-10-17 15:41:00
 # @LastEditors: Daoji daoji.chang@gmail.com
 # @LastEditTime: 2024-11-21 15:54:55
 # @FilePath: /fut-frontend/command/build_prod_push_image.sh
 # @Description: 构建并推送镜像
###

BASE_NAME="daoji/vmq-fastapi-frontend"
# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  --help     显示帮助信息"
    echo "  --arm      构建 ARM64 架构镜像"
    echo "  --x86      构建 AMD64 架构镜像 (默认)"
    echo "  --both     同时构建 ARM64 和 AMD64 架构镜像"
    echo "  --tag      指定版本标签 (例如: v0.0.1)"
    echo
    echo "示例:"
    echo "  $0 --arm   # 构建 ARM64 镜像"
    echo "  $0 --both  # 构建多架构镜像"
    echo "  $0 --tag v0.0.1  # 使用指定版本标签构建"
}



IMAGE_NAME="$BASE_NAME:$VERSION_TAG"
LATEST_IMAGE_NAME="$BASE_NAME:latest"

# 默认平台为 linux/amd64
PLATFORM="linux/amd64"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --help)
      show_help
      exit 0
      ;;
    --arm)
      PLATFORM="linux/arm64"
      shift
      ;;
    --x86)
      PLATFORM="linux/amd64"
      shift
      ;;
    --both)
      PLATFORM="linux/amd64,linux/arm64"
      shift
      ;;
    --tag)
      shift
      if [ -n "$1" ]; then
        TAG="$1"
        shift
      else
        echo "错误: --tag 参数需要一个值"
        exit 1
      fi
      ;;
    *)
      echo "错误: 未知参数 $1"
      echo "使用 --help 查看帮助信息"
      exit 1
      ;;
  esac
done

# 如果环境变量 TAG 存在且以 v 开头，则使用它。否则退出脚本，并提示 TAG 不合法，返回 1
if [[ -n "$TAG" && "$TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+ ]]; then
    VERSION_TAG=$TAG
else
    echo "❌ 环境变量 TAG 不合法，请检查 TAG 是否以 v 开头，并符合 semver 格式"
    exit 1
fi

echo "开始构建镜像..."
echo "目标平台: $PLATFORM"
echo "镜像标签: $IMAGE_NAME"
echo "最新镜像标签: $LATEST_IMAGE_NAME"

docker buildx build \
  --platform $PLATFORM \
  -f scripts/vmq/Dockerfile \
  --push -t $IMAGE_NAME \
  --push -t $LATEST_IMAGE_NAME .

if [ $? -eq 0 ]; then
    # 防止 github actions 自动屏蔽敏感词
    ACTIONS_STEP_DEBUG=true
    echo "✅ 镜像构建并推送成功！"
    echo "镜像信息: $IMAGE_NAME"
    echo "最新镜像信息: $LATEST_IMAGE_NAME"
else
    echo "❌ 镜像构建或推送失败！"
    exit 1
fi
