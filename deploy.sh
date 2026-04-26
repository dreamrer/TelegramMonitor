#!/bin/bash

# TelegramMonitor Docker 部署脚本

set -e

echo "🚀 TelegramMonitor Docker 部署脚本"
echo "=================================="

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if docker compose version &> /dev/null; then
    COMPOSE_CMD=(docker compose)
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD=(docker-compose)
else
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "✅ Docker和Docker Compose已安装"

# 检查.env文件
if [ ! -f .env ]; then
    echo "📝 创建.env文件..."
    cp .env.example .env
    echo "⚠️  请编辑.env文件，填入你的配置"
    echo "编辑完成后，再次运行此脚本"
    exit 0
fi

echo "✅ .env文件已存在"

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data/sessions logs

# 构建镜像
echo "🔨 构建Docker镜像..."
"${COMPOSE_CMD[@]}" build

# 启动容器
echo "🚀 启动容器..."
"${COMPOSE_CMD[@]}" up -d

# 等待容器启动
echo "⏳ 等待容器启动..."
sleep 3

# 检查容器状态
if "${COMPOSE_CMD[@]}" ps | grep -q "telegram-monitor.*Up"; then
    echo "✅ 容器启动成功！"
    echo ""
    echo "📊 容器状态："
    "${COMPOSE_CMD[@]}" ps
    echo ""
    echo "📝 查看日志："
    echo "  ${COMPOSE_CMD[*]} logs -f telegram-monitor"
    echo ""
    echo "🛑 停止容器："
    echo "  ${COMPOSE_CMD[*]} down"
else
    echo "❌ 容器启动失败"
    echo "📝 查看错误日志："
    "${COMPOSE_CMD[@]}" logs telegram-monitor
    exit 1
fi

echo ""
echo "🎉 部署完成！"
