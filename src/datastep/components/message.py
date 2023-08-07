from abc import abstractmethod
from dataclasses import dataclass

import pandas as pd


@dataclass
class MessageContent:
    content: str | pd.DataFrame

    @abstractmethod
    def get(self) -> str:
        pass


class SimpleText(MessageContent):
    def get(self) -> str:
        return self.content


class Table(MessageContent):
    def get(self) -> str:
        if self.content is not None and any(self.content):
            return self.content.to_markdown(index=False, floatfmt=".3f")
        return ""


class SqlCode(MessageContent):
    def get(self) -> str:
        if self.content:
            return f"~~~sql\n{self.content}\n~~~"
        return ""
