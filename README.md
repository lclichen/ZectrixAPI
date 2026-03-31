# zectrixAPI

极趣云平台 CLI 工具，通过命令行控制与管理极趣云平台服务。

## 安装

从源码安装依赖：

```bash
pip install git+https://github.com/lclichen/ZectrixAPI.git
```

## 快速开始

### 1. 配置 API Key

```bash
zectrix config set <your_api_key>
```

API Key 在极趣云平台获取。配置后存储在 `~/.zectrix/config.json`。

查看或管理 API Key：

```bash
zectrix config show      # 查看当前 Key（部分遮蔽）
zectrix config remove    # 删除当前 Key
```

### 2. 查看设备列表

```bash
zectrix devices list
```

### 3. 管理待办事项

```bash
# 查看待办列表
zectrix todos list
zectrix todos list --status 0        # 仅待完成
zectrix todos list --device-id AA:BB:CC:DD:EE:FF

# 创建待办
zectrix todos create --title "买牛奶" --due-date 2026-03-20 --due-time 09:00 --priority 1

# 更新待办
zectrix todos update 1 --title "买牛奶和面包"

# 标记完成（再次调用则取消）
zectrix todos complete 1

# 删除待办
zectrix todos delete 1
```

### 4. 推送内容到设备

```bash
# 推送文本
zectrix display text AA:BB:CC:DD:EE:FF "今日天气：晴\n温度：25°C" --font-size 24

# 推送图片（支持多张，最多5张）
zectrix display image AA:BB:CC:DD:EE:FF /path/to/image1.png /path/to/image2.png

# 推送标题+正文
zectrix display structured-text AA:BB:CC:DD:EE:FF -t "会议提醒" -b "15:00 三楼会议室"
```

## 命令参考

```
zectrix config set <key>          设置 API Key
zectrix config show               查看当前 API Key
zectrix config remove             删除 API Key

zectrix devices list              获取设备列表

zectrix todos list                获取待办列表
zectrix todos create              创建待办
zectrix todos update <id>         更新待办
zectrix todos complete <id>       标记完成/取消完成
zectrix todos delete <id>         删除待办

zectrix display image <dev> <imgs...>            推送图片
zectrix display text <dev> <text>                推送文本
zectrix display structured-text <dev> [-t] [-b]  推送标题+正文
```

## 作为 Python 库使用

```python
from zectrixAPI.client import ZectrixClient, APIError

client = ZectrixClient("your_api_key")

# 获取设备列表
devices = client.list_devices()

# 创建待办
todo = client.create_todo(title="买牛奶", priority=1)

# 推送文本到设备
client.push_text("AA:BB:CC:DD:EE:FF", "Hello World", font_size=24)
```

## 依赖

- Python >= 3.9
- requests >= 2.28
- click >= 8.0

## License

MIT
