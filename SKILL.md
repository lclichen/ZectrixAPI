---
name: zectrix-cloud-manager
description: 通过极趣云平台 API 管理和控制 AI 便利贴设备。支持设备管理、待办事项 CRUD、推送图片/文本/结构化内容到设备显示。当用户需要管理极趣云平台设备、操作待办事项或向设备推送显示内容时使用此技能。
---

# 极趣云平台管理器

## 概述

此技能用于通过极趣云平台 API 管理和控制 AI 便利贴设备，直接调用 [zectrixAPI](https://github.com/lclichen/ZectrixAPI) CLI 完成设备管理、待办事项操作和显示内容推送。

## 功能特性

- 配置和管理 API Key
- 获取设备列表
- 待办事项的增删改查与状态切换
- 推送图片、文本、标题+正文到设备屏幕

## 前提条件

1. 安装依赖：
```bash
pip install zectrixAPI -U

或

pip install git+https://github.com/lclichen/ZectrixAPI.git
```

2. 配置 API Key（首次使用需要）：
```bash
zectrix config set <your_api_key>
```

## 快速开始

### 1. 配置 API Key

API Key 在极趣云平台获取，配置后自动存储在本地 `~/.zectrix/config.json`，后续所有请求自动携带。

```bash
zectrix config set zt_xxxxxxxxxxxxx
```

### 2. 查看设备列表

```bash
zectrix devices list
```

输出中每条设备信息包含 `deviceId`（MAC 地址），后续推送命令使用该值。

### 3. 管理待办事项

```bash
# 查看待办列表
zectrix todos list

# 创建待办
zectrix todos create --title "买牛奶" --due-date 2026-03-20 --priority 1

# 标记完成
zectrix todos complete 1

# 删除待办
zectrix todos delete 1
```

### 4. 推送内容到设备

```bash
# 推送文本
zectrix display text AA:BB:CC:DD:EE:FF "今日天气：晴" --font-size 24

# 推送图片
zectrix display image AA:BB:CC:DD:EE:FF /path/to/image.png

# 推送标题+正文
zectrix display structured-text AA:BB:CC:DD:EE:FF -t "会议提醒" -b "15:00 三楼会议室"
```

## 命令参考

```bash
zectrix --help
zectrix config --help
zectrix devices --help
zectrix todos --help
zectrix display --help
```

**完整命令示例：**

### config — API Key 管理

```bash
# 设置 API Key
zectrix config set zt_xxxxxxxxxxxxx

# 查看当前 Key（部分遮蔽）
zectrix config show

# 删除 Key
zectrix config remove
```

### devices — 设备管理

```bash
# 获取设备列表
zectrix devices list
```

### todos — 待办事项

```bash
# 列出所有待办
zectrix todos list

# 仅列出待完成的
zectrix todos list --status 0

# 按设备过滤
zectrix todos list --device-id AA:BB:CC:DD:EE:FF

# 创建待办
zectrix todos create --title "买牛奶"
zectrix todos create --title "周报" --description "完成Q1周报" --due-date 2026-03-20 --due-time 18:00 --priority 2
zectrix todos create --title "每日站会" --repeat weekly --repeat-weekday 1 --priority 1

# 更新待办
zectrix todos update 1 --title "买牛奶和面包"
zectrix todos update 1 --priority 2 --due-date 2026-03-21

# 标记完成（再次调用取消完成）
zectrix todos complete 1

# 删除待办
zectrix todos delete 1
```

**创建待办参数参考：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `--title` | 标题（必填） | `"买牛奶"` |
| `--description` | 描述 | `"完成Q1周报"` |
| `--due-date` | 截止日期 | `2026-03-20` |
| `--due-time` | 截止时间 | `09:00` |
| `--repeat` | 重复类型 | `none`/`daily`/`weekly`/`monthly`/`yearly` |
| `--repeat-weekday` | 周几 (0=周日) | `1`（weekly 用） |
| `--repeat-month` | 月份 | `3`（yearly 用） |
| `--repeat-day` | 日期 | `15`（monthly/yearly 用） |
| `--priority` | 优先级 | `0`=普通, `1`=重要, `2`=紧急 |
| `--device-id` | 关联设备 MAC | `AA:BB:CC:DD:EE:FF` |

### display — 显示推送

```bash
# 推送纯文本
zectrix display text AA:BB:CC:DD:EE:FF "Hello World"
zectrix display text AA:BB:CC:DD:EE:FF "天气：晴\n温度：25°C" --font-size 24 --page-id 1

# 推送图片（最多5张，单张≤2MB）
zectrix display image AA:BB:CC:DD:EE:FF /path/to/img1.png /path/to/img2.png
zectrix display image AA:BB:CC:DD:EE:FF img.png --no-dither --page-id 2

# 推送标题+正文
zectrix display structured-text AA:BB:CC:DD:EE:FF -t "会议提醒" -b "15:00 三楼会议室"
zectrix display structured-text AA:BB:CC:DD:EE:FF -t "今日计划" -b "1. 完成报告\n2. 团队会议" --page-id 1
```

**显示推送参数参考：**

| 命令 | 必填参数 | 可选参数 |
|------|----------|----------|
| `display text` | `device_id`, `text` | `--font-size` (12-48, 默认20), `--page-id` (1-5) |
| `display image` | `device_id`, `images` | `--no-dither`, `--page-id` (1-5) |
| `display structured-text` | `device_id`, `-t`/`-b` 至少一项 | `--page-id` (1-5) |

## 故障排除

### API Key 问题

**问题：命令提示"未配置 API Key"**

```bash
zectrix config set <your_api_key>
```

确认 Key 以 `zt_` 开头。查看当前配置：
```bash
zectrix config show
```

### 设备问题

**问题：设备列表为空**

1. 确认设备已在极趣云平台注册并绑定账号
2. 检查 API Key 对应的账号是否正确

**问题：不知道设备 ID**

使用 `zectrix devices list` 查看，`deviceId` 字段即为设备 MAC 地址。

### 推送问题

**问题：图片推送失败**

1. 确认图片格式支持（PNG、JPG）
2. 单张图片不超过 2MB
3. 同时推送不超过 5 张
4. 确认设备在线

**问题：文本显示异常**

1. 文本不超过 5000 字
2. 字体大小范围 12-48，建议 20-28
3. 使用 `\n` 换行

**问题：指定 page-id 后内容未持久化**

确认 page-id 范围为 1-5，超出范围将不会持久化存储。

### 获取帮助

- 极趣云平台：https://cloud.zectrix.com
- API 文档：参考项目 `API_SPEC.md`
