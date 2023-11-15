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

参考 [driver](https://nonebot.dev/docs/appendices/config#driver) 配置项，添加 `HTTPClient` 和 `WebSocketClient` 支持。

如：

```dotenv
DRIVER=~httpx+~websockets
DRIVER=~aiohttp
```

### QQ_IS_SANDBOX

是否为沙盒模式，默认为 `False`。

```dotenv
QQ_IS_SANDBOX=true
```

### QQ_BOTS

配置机器人帐号 `id` `token` `secret`，intent 需要根据机器人类型以及需要的事件进行配置。

#### Intent

以下为所有 Intent 配置项以及默认值：

```json
{
  "guilds": true,
  "guild_members": true,
  "guild_messages": false,
  "guild_message_reactions": true,
  "direct_message": false,
  "open_forum_event": false,
  "audio_live_member": false,
  "c2c_group_at_messages": false,
  "interaction": false,
  "message_audit": true,
  "forum_event": false,
  "audio_action": false,
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
    }
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
      "c2c_group_at_messages": true
    }
  }
]
'
```
