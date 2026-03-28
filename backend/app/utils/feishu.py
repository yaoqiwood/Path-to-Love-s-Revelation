#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
飞书机器人推送工具
支持异常告警和普通消息推送
"""
import asyncio
import base64
import hashlib
import hmac
import json
import time
import traceback
from typing import Optional, Dict, Any
import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

try:
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError


class FeishuBot:
    """飞书机器人核心类"""

    def __init__(
        self,
        webhook_token: str,
        secret: Optional[str] = None,
        topic: str = "dev",
        fail_notice: bool = False,
    ):
        """
        机器人初始化
        :param webhook_token: 飞书群自定义机器人webhook地址token
        :param secret: 机器人安全设置页面勾选"加签"时需要传入的密钥
        :param topic: 推送主题
        :param fail_notice: 消息发送失败提醒，默认为False不提醒
        """
        self.headers = {"Content-Type": "application/json; charset=utf-8"}
        self.webhook = f"https://open.feishu.cn/open-apis/bot/v2/hook/{webhook_token}"
        self.secret = secret
        self.topic = topic
        self.fail_notice = fail_notice
        # 创建异步HTTP客户端连接池
        self.client = httpx.AsyncClient(timeout=10.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    async def aclose(self):
        """关闭连接"""
        await self.client.aclose()

    async def send_exception_notice(
        self,
        title: str,
        error: Exception,
        request_info: Optional[Dict[str, Any]] = None,
        extra_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        发送异常通知到飞书
        :param title: 异常标题
        :param error: 异常对象
        :param request_info: 请求相关信息
        :param extra_info: 额外附加信息
        :return: 发送结果
        """
        # 构建消息卡片
        card = self._build_exception_card(title, error, request_info, extra_info)
        # 发送卡片消息
        return await self.send_card(card)

    def _build_exception_card(
        self,
        title: str,
        error: Exception,
        request_info: Optional[Dict[str, Any]] = None,
        extra_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        构建异常通知的卡片消息
        """
        # 基础卡片结构
        card = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True, "enable_forward": True},
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"⚠️ {title} 【{self.topic}】",
                    },
                    "template": "red",  # 红色主题表示错误
                },
                "elements": [],
            },
        }

        # 添加时间信息
        time_element = {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**发生时间**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}",
            },
        }
        card["card"]["elements"].append(time_element)

        # 添加异常信息
        exception_element = {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**异常类型**: {type(error).__name__}\n**异常信息**: {str(error)}",
            },
        }
        card["card"]["elements"].append(exception_element)

        # 添加请求信息
        if request_info:
            request_content = "**请求信息**:\n"
            for key, value in request_info.items():
                request_content += f"- {key}: {value}\n"

            request_element = {
                "tag": "div",
                "text": {"tag": "lark_md", "content": request_content},
            }
            card["card"]["elements"].append(request_element)

        # 添加额外信息
        if extra_info:
            extra_content = "**附加信息**:\n"
            for key, value in extra_info.items():
                extra_content += f"- {key}: {value}\n"

            extra_element = {
                "tag": "div",
                "text": {"tag": "lark_md", "content": extra_content},
            }
            card["card"]["elements"].append(extra_element)

        # 添加堆栈跟踪
        stack_trace = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
        stack_element = {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**堆栈跟踪**:\n```\n{stack_trace[:1500]}\n```",
            },
        }
        card["card"]["elements"].append(stack_element)

        return card

    async def send_card(self, card: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送卡片消息
        :param card: 卡片消息内容
        :return: 返回消息发送结果
        """
        # 添加签名
        if self.secret:
            card["sign"], card["timestamp"] = self._gen_signature()

        return await self._post(card)

    async def send_text(
        self,
        title: str,
        msg: str,
        extra_info: Optional[Dict[str, Any]] = None,
        at_info: Optional[Dict[str, Any]] = None,
    ):
        """
        消息类型为text类型
        :param title: 消息标题
        :param msg: 消息内容
        :param extra_info: 额外信息
        :param at_info: 艾特信息
        :return: 返回消息发送结果
        """
        data = {"msg_type": "text", "at": {}}
        if msg and msg.strip():  # 传入msg非空
            title = f"【{self.topic}】- {title}  \n"
            content = ""
            if at_info:
                for key, value in at_info.items():
                    at_str = FeishuBot._gen_at_text(value, key, "open_id")
                    content += at_str
                content += "\n"

            content += f"☀️{msg}\n"
            # 添加额外信息
            if extra_info:
                content += "\n 🌟附加信息: \n"
                for key, value in extra_info.items():
                    content += f"  - {key}: {value}\n"

            data["content"] = {"text": f"{title} \n {content}"}
        else:
            raise ValueError("text类型，消息内容不能为空！")

        if self.secret:
            data["sign"], data["timestamp"] = self._gen_signature()

        return await self._post(data)

    async def _post(self, data):
        """
        异步发送消息（内容UTF-8编码）
        :param data: 消息数据（字典）
        :return: 返回消息发送结果
        """
        try:
            post_data = json.dumps(data)
            response = await self.client.post(
                self.webhook,
                headers=self.headers,
                content=post_data,
            )
            response.raise_for_status()  # 检查HTTP状态码
        except httpx.HTTPStatusError as exc:
            logger.error(
                f"消息发送失败，HTTP error: {exc.response.status_code}, reason: {exc.response.reason_phrase}"
            )
            raise
        except httpx.RequestError as exc:
            logger.error(f"消息发送失败，请求错误: {str(exc)}")
            raise
        else:
            try:
                result = response.json()
            except JSONDecodeError:
                logger.error(
                    f"服务器响应异常，状态码：{response.status_code}，响应内容：{response.text}"
                )
                return {"errcode": 500, "errmsg": "服务器响应异常"}
            else:
                logger.info(f"发送结果：{result}")
                # 消息发送失败提醒（errcode 不为 0，表示消息发送异常）
                if self.fail_notice and result.get("code", True):
                    await self._send_fail_notice(result)
                return result

    async def _send_fail_notice(self, result):
        """异步发送失败通知"""
        time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        error_data = {
            "msgtype": "text",
            "text": {
                "content": f"[注意-自动通知]飞书机器人消息发送失败，时间：{time_now}，原因：{result.get('msg', '未知异常')}"
            },
            "at": {"isAtAll": False},
        }
        logger.warning(f"消息发送失败，自动通知：{error_data}")
        try:
            await self.client.post(
                self.webhook,
                headers=self.headers,
                content=json.dumps(error_data),
                timeout=5.0,
            )
        except Exception as e:
            logger.error(f"发送失败通知时出错: {str(e)}")

    def _gen_signature(self):
        """
        生成飞书机器人加签验证所需的签名
        :return: 时间戳和签名元组 (timestamp, sign)
        """
        # 生成时间戳（秒级）
        timestamp = str(int(time.time()))

        # 拼接timestamp和secret
        string_to_sign = "{}\n{}".format(timestamp, self.secret)
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        # 对结果进行base64处理
        sign = base64.b64encode(hmac_code).decode("utf-8")
        return sign, timestamp

    @staticmethod
    def _gen_at_text(id_str: str, name: str, id_type: str = "user_id"):
        """user_id or open_id"""
        return f'<at {id_type} = "{id_str}">{name}</at> '

    @staticmethod
    def _gen_at_interactive(id_str: str, name: str, id_type: str = "user_id"):
        return {
            "tag": "div",
            "text": {"content": f"at{name}<at id={id_str}></at> \n", "tag": "lark_md"},
        }

    @staticmethod
    def _gen_at_post(id_str: str, name: str, id_type: str = "user_id"):
        return {"tag": "at", id_type: id_str, "user_name": name}


# ==================== 简化的工具函数 ====================


async def send_alert(
    title: str,
    exc: Exception,
    request_info: Optional[Dict[str, Any]] = None,
    extra_info: Optional[Dict[str, Any]] = None,
    feishu_config: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    发送异常告警到飞书
    :param title: 异常标题
    :param exc: 异常对象
    :param request_info: 请求相关信息
    :param extra_info: 额外附加信息
    :param feishu_config: 自定义飞书配置（可选）
    :return: 发送结果
    """
    # 检查是否启用
    if not settings.FEISHU_ENABLED:
        logger.debug("飞书告警未启用，跳过发送")
        return None

    # 使用配置
    webhook_token = settings.FEISHU_WEBHOOK_TOKEN
    secret_key = settings.FEISHU_SECRET_KEY
    topic = "development" if settings.DEBUG else "production"

    # 如果提供了自定义配置，覆盖默认配置
    if feishu_config:
        webhook_token = feishu_config.get("webhook_token", webhook_token)
        secret_key = feishu_config.get("secret_key", secret_key)
        topic = feishu_config.get("topic", topic)

    try:
        async with FeishuBot(
            webhook_token, secret=secret_key, topic=topic, fail_notice=True
        ) as bot:
            result = await bot.send_exception_notice(
                title, exc, request_info, extra_info
            )
            return result
    except Exception as e:
        logger.error(f"发送飞书告警失败: {str(e)}")
        return None


async def send_notice(
    title: str,
    msg: str,
    extra_info: Optional[Dict[str, Any]] = None,
    at_info: Optional[Dict[str, Any]] = None,
    feishu_config: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    发送普通通知到飞书
    :param title: 消息标题
    :param msg: 消息内容
    :param extra_info: 额外信息
    :param at_info: 艾特信息
    :param feishu_config: 自定义飞书配置（可选）
    :return: 发送结果
    """
    # 检查是否启用
    if not settings.FEISHU_NOTICE_ENABLED:
        logger.debug("飞书通知未启用，跳过发送")
        return None

    # 使用配置
    webhook_token = settings.FEISHU_NOTICE_WEBHOOK_TOKEN
    secret_key = settings.FEISHU_NOTICE_SECRET_KEY
    topic = "development" if settings.DEBUG else "production"

    # 如果提供了自定义配置，覆盖默认配置
    if feishu_config:
        webhook_token = feishu_config.get("webhook_token", webhook_token)
        secret_key = feishu_config.get("secret_key", secret_key)
        topic = feishu_config.get("topic", topic)

    try:
        async with FeishuBot(
            webhook_token, secret=secret_key, topic=topic, fail_notice=True
        ) as bot:
            result = await bot.send_text(title, msg, extra_info, at_info)
            return result
    except Exception as e:
        logger.error(f"发送飞书通知失败: {str(e)}")
        return None
