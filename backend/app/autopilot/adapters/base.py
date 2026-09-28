from abc import ABC, abstractmethod


class ApplyResult:
    def __init__(self, status: str, message: str = "", screenshot: str | None = None):
        self.status = status   # submitted | needs_human | failed | skipped | prefill
        self.message = message
        self.screenshot = screenshot


class BaseAdapter(ABC):
    name: str = "base"
    domain_pattern: str = ""

    @abstractmethod
    async def apply(self, page, job, vault) -> ApplyResult:
        ...