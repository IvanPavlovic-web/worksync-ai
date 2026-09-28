import re

from .ashby import AshbyAdapter
from .greenhouse import GreenhouseAdapter
from .lever import LeverAdapter
from .linkedin import LinkedInAdapter
from .workable import WorkableAdapter


ADAPTERS = [
    GreenhouseAdapter(),
    LeverAdapter(),
    AshbyAdapter(),
    WorkableAdapter(),
    LinkedInAdapter(),
]


def pick_adapter(url: str):
    for a in ADAPTERS:
        if a.domain_pattern and re.search(a.domain_pattern, url):
            return a
    return None