<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://raw.githubusercontent.com/nonebot/adapter-qqguild/master/assets/logo.png" width="200" height="200" alt="nonebot-adapter-qqguild"></a>
</p>

<div align="center">

# NoneBot-Adapter-QQGuild

_✨ QQ 频道协议适配 ✨_

</div>

## 配置

修改 NoneBot 配置文件 `.env` 或者 `.env.*`。

### Driver

参考 [driver](https://v2.nonebot.dev/docs/tutorial/configuration#driver) 配置项，添加 `ForwardDriver` 支持。

如：

```dotenv
DRIVER=~httpx+~websockets
DRIVER=~aiohttp
```

### QQGUILD_IS_SANDBOX

是否为沙盒模式，默认为 `False`。

```dotenv
QQGUILD_IS_SANDBOX=true
```

### QQGUILD_BOTS

配置机器人帐号，如：

```dotenv
QQGUILD_BOTS='
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
