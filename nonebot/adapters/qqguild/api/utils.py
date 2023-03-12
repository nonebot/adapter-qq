import json
from typing import Any, Dict

from .model import MessageSend


def parse_send_message(data: Dict[str, Any]) -> Dict[str, Any]:
    model_data = MessageSend(**data).dict(exclude_none=True)
    if file_image := model_data.pop("file_image", None):
        # 使用 multipart/form-data
        data_: Dict[str, Any] = {"file_image": ("file_image", file_image)}
        for k, v in model_data.items():
            if isinstance(v, (dict, list)):
                # 当字段类型为对象或数组时需要将字段序列化为 JSON 字符串后进行调用
                # https://bot.q.qq.com/wiki/develop/api/openapi/message/post_messages.html#content-type
                data_[k] = (
                    None,
                    json.dumps({k: v}).encode("utf-8"),
                    "application/json",
                )
            else:
                data_[k] = (None, v.encode("utf-8"), "text/plain")
        params = {"files": data_}
    else:
        params = {"json": model_data}
    return params
