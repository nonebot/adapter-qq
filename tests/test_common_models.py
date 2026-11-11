from nonebot.compat import model_dump, type_validate_python

from nonebot.adapters.qq.models import (
    Action,
    Button,
    InlineKeyboard,
    InlineKeyboardRow,
    MessageKeyboard,
    Modal,
    PostC2CMessagesReturn,
    PostGroupMessagesReturn,
)


def test_keyboard_button_modal_serialization():
    keyboard = MessageKeyboard(
        content=InlineKeyboard(
            rows=[
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            id="button-id",
                            group_id="group-id",
                            action=Action(
                                type=1,
                                data="callback",
                                modal=Modal(
                                    content="确认执行",
                                    confirm_text="确认",
                                    cancel_text="取消",
                                ),
                            ),
                        )
                    ]
                )
            ]
        )
    )

    assert model_dump(keyboard, exclude_none=True) == {
        "content": {
            "rows": [
                {
                    "buttons": [
                        {
                            "id": "button-id",
                            "group_id": "group-id",
                            "action": {
                                "type": 1,
                                "data": "callback",
                                "modal": {
                                    "content": "确认执行",
                                    "confirm_text": "确认",
                                    "cancel_text": "取消",
                                },
                            },
                        }
                    ]
                }
            ]
        }
    }


def test_post_messages_return_ext_info():
    data = {
        "id": "ROBOT1.0_MESSAGE",
        "timestamp": "2026-11-03T12:43:27+08:00",
        "ext_info": {"ref_idx": "REFIDX_SENT=="},
    }

    for model in (PostGroupMessagesReturn, PostC2CMessagesReturn):
        result = type_validate_python(model, data)
        assert result.ext_info is not None
        assert result.ext_info.ref_idx == "REFIDX_SENT=="

        legacy = type_validate_python(model, {"id": "ROBOT1.0_MESSAGE"})
        assert legacy.ext_info is None
