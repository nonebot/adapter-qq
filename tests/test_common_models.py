from nonebot.adapters.qq.models import (
    Action,
    Button,
    InlineKeyboard,
    InlineKeyboardRow,
    MessageKeyboard,
    Modal,
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

    assert keyboard.model_dump(exclude_none=True) == {
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
