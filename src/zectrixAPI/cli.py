"""极趣云平台 CLI"""

from __future__ import annotations

import sys

import click

from .client import APIError, ZectrixClient
from .config import clear_api_key, load_api_key, save_api_key



def _get_client() -> ZectrixClient:
    api_key = load_api_key()
    if not api_key:
        click.echo("错误: 未配置 API Key，请先运行 zectrix config set <key>", err=True)
        sys.exit(1)
    return ZectrixClient(api_key)


# ── 根命令 ──

@click.group()
@click.version_option(package_name="zectrixAPI", prog_name="zectrix")
def main():
    """极趣云平台 CLI 工具"""
    pass


# ── config: API Key 管理 ──

@main.group()
def config():
    """API Key 配置管理"""
    pass


@config.command()
@click.argument("api_key")
def set(api_key: str):
    """设置 API Key"""
    save_api_key(api_key)
    click.echo("API Key 已保存")


@config.command()
def show():
    """查看当前 API Key"""
    key = load_api_key()
    if not key:
        click.echo("未配置 API Key")
    else:
        click.echo(f"{key[:8]}{'*' * (len(key) - 8)}")


@config.command()
def remove():
    """删除 API Key"""
    clear_api_key()
    click.echo("API Key 已删除")


# ── devices: 设备管理 ──

@main.group()
def devices():
    """设备管理"""
    pass


@devices.command("list")
def device_list():
    """获取设备列表"""
    client = _get_client()
    try:
        result = client.list_devices()
    except APIError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)

    if not result:
        click.echo("暂无设备")
        return

    click.echo(f"{'设备ID':<20} {'别名':<16} {'型号'}")
    click.echo("-" * 60)
    for d in result:
        click.echo(f"{d['deviceId']:<20} {d.get('alias', ''):<16} {d.get('board', '')}")


# ── todos: 待办事项 ──

@main.group()
def todos():
    """待办事项管理"""
    pass


@todos.command("list")
@click.option("--status", type=click.IntRange(0, 1), default=None, help="过滤状态: 0=待完成, 1=已完成")
@click.option("--device-id", default=None, help="按设备ID过滤")
def todo_list(status: int | None, device_id: str | None):
    """获取待办列表"""
    client = _get_client()
    try:
        result = client.list_todos(status=status, device_id=device_id)
    except APIError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)

    if not result:
        click.echo("暂无待办事项")
        return

    priority_labels = {0: "普通", 1: "重要", 2: "紧急"}
    status_labels = {0: "待完成", 1: "已完成"}

    click.echo(f"{'ID':<6} {'标题':<20} {'状态':<8} {'优先级':<6} {'截止日期':<12} {'设备'}")
    click.echo("-" * 80)
    for t in result:
        sid = t.get("id", "")
        title = t.get("title", "")[:18]
        st = status_labels.get(t.get("status", 0), "?")
        pr = priority_labels.get(t.get("priority", 0), "?")
        due = t.get("dueDate", "")
        dev = t.get("deviceName", "") or t.get("deviceId", "")
        click.echo(f"{sid:<6} {title:<20} {st:<8} {pr:<6} {due:<12} {dev}")


@todos.command("create")
@click.option("--title", required=True, help="标题")
@click.option("--description", default="", help="描述")
@click.option("--due-date", default=None, help="截止日期 (yyyy-MM-dd)")
@click.option("--due-time", default=None, help="截止时间 (HH:mm)")
@click.option("--repeat", "repeat_type", default="none",
              type=click.Choice(["none", "daily", "weekly", "monthly", "yearly"]),
              help="重复类型")
@click.option("--repeat-weekday", type=click.IntRange(0, 6), default=None, help="周几 (0=周日, weekly用)")
@click.option("--repeat-month", type=click.IntRange(1, 12), default=None, help="月份 (yearly用)")
@click.option("--repeat-day", type=click.IntRange(1, 31), default=None, help="日期 (monthly/yearly用)")
@click.option("--priority", type=click.IntRange(0, 2), default=0, help="优先级: 0=普通, 1=重要, 2=紧急")
@click.option("--device-id", default=None, help="设备ID (MAC地址)")
def todo_create(
    title: str, description: str, due_date: str | None, due_time: str | None,
    repeat_type: str, repeat_weekday: int | None, repeat_month: int | None,
    repeat_day: int | None, priority: int, device_id: str | None,
):
    """创建待办"""
    client = _get_client()
    body: dict = {
        "title": title,
        "description": description,
        "repeatType": repeat_type,
        "priority": priority,
    }
    if due_date:
        body["dueDate"] = due_date
    if due_time:
        body["dueTime"] = due_time
    if repeat_weekday is not None:
        body["repeatWeekday"] = repeat_weekday
    if repeat_month is not None:
        body["repeatMonth"] = repeat_month
    if repeat_day is not None:
        body["repeatDay"] = repeat_day
    if device_id:
        body["deviceId"] = device_id

    try:
        result = client.create_todo(**body)
    except APIError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    click.echo(f"待办已创建, ID={result.get('id')}")


@todos.command("update")
@click.argument("todo_id", type=int)
@click.option("--title", default=None, help="新标题")
@click.option("--description", default=None, help="新描述")
@click.option("--due-date", default=None, help="新截止日期 (yyyy-MM-dd)")
@click.option("--due-time", default=None, help="新截止时间 (HH:mm)")
@click.option("--priority", type=click.IntRange(0, 2), default=None, help="新优先级: 0=普通, 1=重要, 2=紧急")
def todo_update(
    todo_id: int, title: str | None, description: str | None,
    due_date: str | None, due_time: str | None, priority: int | None,
):
    """更新待办"""
    client = _get_client()
    body: dict = {}
    if title is not None:
        body["title"] = title
    if description is not None:
        body["description"] = description
    if due_date is not None:
        body["dueDate"] = due_date
    if due_time is not None:
        body["dueTime"] = due_time
    if priority is not None:
        body["priority"] = priority

    if not body:
        click.echo("错误: 至少指定一个更新字段", err=True)
        sys.exit(1)

    try:
        client.update_todo(todo_id, **body)
    except APIError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    click.echo("待办已更新")


@todos.command("complete")
@click.argument("todo_id", type=int)
def todo_complete(todo_id: int):
    """标记待办完成（再次调用则取消完成）"""
    client = _get_client()
    try:
        client.complete_todo(todo_id)
    except APIError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    click.echo("操作成功")


@todos.command("delete")
@click.argument("todo_id", type=int)
def todo_delete(todo_id: int):
    """删除待办"""
    client = _get_client()
    try:
        client.delete_todo(todo_id)
    except APIError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    click.echo("待办已删除")


# ── display: 显示推送 ──

@main.group()
def display():
    """显示推送"""
    pass


@display.command("image")
@click.argument("device_id")
@click.argument("images", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--no-dither", is_flag=True, default=False, help="关闭抖动算法")
@click.option("--page-id", default=None, help="页面编号 (1-5)，持久化存储")
def display_image(device_id: str, images: tuple[str, ...], no_dither: bool, page_id: str | None):
    """推送图片到设备 (最多5张)"""
    if len(images) > 5:
        click.echo("错误: 最多推送5张图片", err=True)
        sys.exit(1)

    client = _get_client()
    try:
        result = client.push_image(device_id, list(images), dither=not no_dither, page_id=page_id)
    except APIError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    click.echo(f"推送成功, {result.get('pushedPages', 0)}/{result.get('totalPages', 0)} 页")


@display.command("text")
@click.argument("device_id")
@click.argument("text")
@click.option("--font-size", type=click.IntRange(12, 48), default=20, help="字体大小 (12-48, 默认20)")
@click.option("--page-id", default=None, help="页面编号 (1-5)，持久化存储")
def display_text(device_id: str, text: str, font_size: int, page_id: str | None):
    """推送文本到设备"""
    client = _get_client()
    try:
        result = client.push_text(device_id, text, font_size=font_size, page_id=page_id)
    except APIError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    click.echo(f"推送成功, {result.get('pushedPages', 0)}/{result.get('totalPages', 0)} 页")


@display.command("structured-text")
@click.argument("device_id")
@click.option("--title", "-t", default=None, help="标题 (与 --body 至少填一项)")
@click.option("--body", "-b", default=None, help="正文内容")
@click.option("--page-id", default=None, help="页面编号 (1-5)，持久化存储")
def display_structured(device_id: str, title: str | None, body: str | None, page_id: str | None):
    """推送标题+正文到设备"""
    if not title and not body:
        click.echo("错误: --title 和 --body 至少指定一项", err=True)
        sys.exit(1)

    client = _get_client()
    try:
        result = client.push_structured_text(device_id, title=title, body=body, page_id=page_id)
    except APIError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    click.echo(f"推送成功, {result.get('pushedPages', 0)}/{result.get('totalPages', 0)} 页")
