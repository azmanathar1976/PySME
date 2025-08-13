from typing import Callable, Optional


class Div:
    def __init__(self, cls_names: Optional[str] = None) -> None:
        self.cls_names = cls_names


class H1:
    def __init__(
        self, cls_names: Optional[str] = None, text: Optional[str] = None
    ) -> None:
        self.cls_names = cls_names
        self.text = text


class Button:
    def __init__(
        self,
        cls_names: Optional[str] = None,
        onclick: Optional[Callable[[], None]] = None,
        text: Optional[str] = None,
    ) -> None:
        self.cls_names = cls_names
        self.onclick = onclick
        self.text = text
