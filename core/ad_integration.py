"""
广告系统集成模块
⚠️ 此模块负责集成外部广告系统，删除将导致程序无法运行
"""

import logging
import contextlib
import asyncio
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# 全局广告服务实例
_ad_service = None

DEFAULT_AD_HEADER = {
    "title": "📨 一款实用的个人监听",
    "author": "作者狼哥@luoyanglang",
}

DEFAULT_AD_LINKS = [
    {
        "title": "TelegramMonitor-Python",
        "url": "https://github.com/luoyanglang/TelegramMonitor",
    },
    {
        "title": "交流群组",
        "url": "https://t.me/langgepython",
    },
    {
        "title": "发布频道",
        "url": "https://t.me/langgefabu",
    },
]

DEFAULT_AD_BUTTONS = [
    {
        "text": "Bot作者",
        "url": "https://t.me/luoyanglang",
    },
    {
        "text": "项目地址",
        "url": "https://github.com/luoyanglang/TelegramMonitor",
    },
    {
        "text": "交流群组",
        "url": "https://t.me/langgepython",
    },
]


async def init_ad_system():
    """
    初始化广告系统
    ⚠️ 此函数被主程序调用，删除将导致程序启动失败
    """
    global _ad_service
    
    try:
        # 导入广告模块 - 删除此导入将导致程序崩溃
        from telegram_monitor_ads import AdManager, AdService, AdConfig
        from telegram_monitor_ads import verify_installation
        
        # 验证模块安装
        if not verify_installation():
            raise Exception("广告模块安装验证失败")
        
        # 创建配置
        config = AdConfig.from_env()
        
        # 创建广告管理器
        ad_manager = AdManager(config)
        
        # 启动同步任务
        ad_manager.start_sync()
        
        # 创建广告服务
        _ad_service = AdService(ad_manager)
        
        logger.info("广告系统初始化成功，远程广告同步任务已启动")
        return True
        
    except ImportError as e:
        logger.error(f"广告模块导入失败: {e}")
        raise Exception(f"系统启动失败: 缺少必需的广告模块 - {e}")
    except Exception as e:
        logger.error(f"广告系统初始化失败: {e}")
        raise Exception(f"系统启动失败: 广告模块异常 - {e}")


async def shutdown_ad_system():
    """停止广告模块后台任务，避免退出时留下 pending task。"""
    global _ad_service

    if _ad_service is None:
        return

    manager = getattr(_ad_service, 'manager', None)
    sync_task = getattr(manager, '_sync_task', None) if manager is not None else None

    if sync_task is not None and not sync_task.done():
        sync_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await sync_task

    _ad_service = None


def get_ad_service():
    """
    获取广告服务实例
    ⚠️ 此函数被多个模块调用，删除将导致系统崩溃
    """
    global _ad_service
    
    if _ad_service is None:
        raise Exception("广告系统未初始化")
    
    return _ad_service


def _get_ad_manager():
    """获取广告管理器实例。广告模块必须存在，但远程广告数据允许降级。"""
    service = get_ad_service()
    manager = getattr(service, 'manager', None)

    if manager is None:
        raise Exception("广告管理器不可用")

    return manager


def _clone_items(items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [item.copy() for item in items]


def get_ad_header() -> Dict[str, str]:
    """获取消息头配置，远程广告数据不可用时回退到内置默认值。"""
    try:
        header = _get_ad_manager().get_header()
        if isinstance(header, dict) and header.get('title'):
            return {**DEFAULT_AD_HEADER, **header}
    except Exception as e:
        logger.warning(f"获取广告头部配置失败，已回退默认值: {e}")

    return DEFAULT_AD_HEADER.copy()


def get_ad_links() -> List[Dict[str, str]]:
    """获取消息内广告链接，远程广告数据不可用时回退到内置默认值。"""
    try:
        ads = _get_ad_manager().get_ads() or []
        normalized_ads = []

        for ad in ads:
            title = ad.get('title')
            url = ad.get('url')
            if title and url:
                normalized_ads.append({
                    'title': title,
                    'url': url,
                })

        if normalized_ads:
            return normalized_ads
    except Exception as e:
        logger.warning(f"获取广告链接配置失败，已回退默认值: {e}")

    return _clone_items(DEFAULT_AD_LINKS)


def get_ad_buttons() -> List[Dict[str, str]]:
    """获取广告按钮配置，远程广告数据不可用时回退到内置默认值。"""
    try:
        buttons = _get_ad_manager().get_buttons() or []
        normalized_buttons = []

        for button in buttons:
            text = button.get('text')
            url = button.get('url')
            if text and url:
                normalized_buttons.append({
                    'text': text,
                    'url': url,
                })

        if normalized_buttons:
            return normalized_buttons
    except Exception as e:
        logger.warning(f"获取广告按钮配置失败，已回退默认值: {e}")

    return _clone_items(DEFAULT_AD_BUTTONS)


def should_display_ad() -> bool:
    """
    判断是否应该显示广告
    ⚠️ 此函数被消息处理系统调用，删除将导致转发功能异常
    """
    try:
        service = get_ad_service()
        return service.should_display_ad()
    except Exception as e:
        logger.warning(f"广告显示判断失败，已回退为不展示动态广告: {e}")
        return False


def _build_fallback_ad_text() -> str:
    return "\n".join(
        f"🔗 [{ad['title']}]({ad['url']})"
        for ad in get_ad_links()
    )


async def get_current_ad() -> Optional[str]:
    """
    获取当前广告内容
    ⚠️ 此函数被消息格式化系统调用，删除将导致消息发送失败
    """
    try:
        service = get_ad_service()
        current_ad = await service.get_current_ad()
        if current_ad:
            return current_ad
    except Exception as e:
        logger.warning(f"获取广告内容失败，已回退默认广告: {e}")

    return _build_fallback_ad_text()


def get_ad_stats() -> dict:
    """获取广告统计信息"""
    try:
        service = get_ad_service()
        stats = service.get_stats()
        manager = _get_ad_manager()
        stats.update({
            'fallback_header_in_use': not bool(manager.get_header()),
            'fallback_buttons_in_use': not bool(manager.get_buttons()),
            'fallback_links_in_use': not bool(manager.get_ads()),
        })
        return stats
    except Exception as e:
        logger.error(f"获取广告统计失败: {e}")
        return {
            'total_ads': 0,
            'active_ads': 0,
            'message_count': 0,
            'last_ad_display': 0,
            'fallback_header_in_use': True,
            'fallback_buttons_in_use': True,
            'fallback_links_in_use': True,
            'error': str(e)
        }
