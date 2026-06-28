<p align="center">
  <a href="https://nonebot.dev/"><img src="https://raw.githubusercontent.com/nonebot/adapter-qq/master/assets/logo.png" width="200" height="200" alt="nonebot-adapter-qq"></a>
</p>

<div align="center">

# NoneBot-Adapter-QQ

_✨ QQ 协议适配 ✨_

</div>

## 配置

修改 NoneBot 配置文件 `.env` 或者 `.env.*`。

### Driver

如果使用 WebSocket 连接方式，请参考 [driver](https://nonebot.dev/docs/appendices/config#driver) 配置项，添加 `HTTPClient` 和 `WebSocketClient` 支持。如：

```dotenv
DRIVER=~httpx+~websockets
DRIVER=~aiohttp
```

如果使用 WebHook 连接方式，则添加 `ASGIServer` 支持。如：

```dotenv
DRIVER=~fastapi
```

### QQ_IS_SANDBOX

是否为沙盒模式，默认为 `False`。

```dotenv
QQ_IS_SANDBOX=true
```

### QQ_BOTS

配置机器人帐号 `id` `token` `secret`，intent 需要根据机器人类型以及需要的事件进行配置。

#### Webhook / WebSocket

通过配置项 `use_websocket` 来选择是否启用 WebSocket 连接，当前默认为 `True`。如果关闭 WebSocket 连接方式，则可以通过 WebHook 方式来连接机器人，请在 QQ 开放平台中配置机器人回调地址：`https://host:port/qq/webhook`。

#### Intent

Intent 仅对 WebSocket 连接方式生效。以下为所有 Intent 配置项以及默认值：

```jsonc
{
  // 频道事件
  "guilds": true,
  // 频道成员事件
  "guild_members": true,
  // 频道消息事件
  "guild_messages": false,
  // 频道消息表态事件
  "guild_message_reactions": true,
  // 频道私信事件
  "direct_message": false,
  // 频道公域论坛事件
  "open_forum_event": false,
  // 频道音频或直播成员事件
  "audio_live_member": false,
  // 群成员变更事件
  "group_members": false,
  // 私聊与群聊消息事件
  "c2c_group_at_messages": false,
  // 互动事件
  "interaction": false,
  // 频道消息审核事件
  "message_audit": true,
  // 频道私域论坛事件
  "forum_event": false,
  // 频道音频操作事件
  "audio_action": false,
  // 频道@机器人消息事件
  "at_messages": true
}
```

#### 示例

私域频道机器人示例

```dotenv
QQ_BOTS='
[
  {
    "id": "xxx",
    "token": "xxx",
    "secret": "xxx",
    "intent": {
      "guild_messages": true,
      "at_messages": false
    },
    "use_websocket": false
  }
]
'
```

公域群机器人示例

```dotenv
QQ_BOTS='
[
  {
    "id": "xxx",
    "token": "xxx",
    "secret": "xxx",
    "intent": {
      "c2c_group_at_messages": true,
      "group_members": true
    },
    "use_websocket": false
  }
]
'
```
