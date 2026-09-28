from app.scrapers.ats.ashby import AshbyScraper
from app.scrapers.ats.greenhouse import GreenhouseScraper
from app.scrapers.ats.lever import LeverScraper
from app.scrapers.ats.smartrecruiters import SmartRecruitersScraper
from app.scrapers.ats.workable import WorkableScraper
from app.scrapers.boards.arbeitnow import ArbeitnowScraper
from app.scrapers.boards.himalayas import HimalayasScraper
from app.scrapers.boards.jobicy import JobicyScraper
from app.scrapers.boards.remoteok import RemoteOKScraper
from app.scrapers.boards.remotive import RemotiveScraper
from app.scrapers.boards.wwr import WWRScraper
from app.scrapers.regional.eures import EURESScraper
from app.scrapers.regional.helloworld_rs import HelloWorldRsScraper
from app.scrapers.regional.make_it_in_germany import MakeItInGermanyScraper
from app.scrapers.regional.mojposao_ba import MojPosaoBaScraper
from app.scrapers.regional.posao_ba import PosaoBaScraper
from app.scrapers.regional.posao_hr import PosaoHrScraper
from app.scrapers.catalog import CatalogScraper


GREENHOUSE_BOARDS = [
    "stripe", "airbnb", "figma", "notion", "linear",
    "supabase", "retool", "brex", "gusto", "doordash", "instacart",
    "robinhood", "reddit", "discord", "dropbox", "coinbase",
]

LEVER_BOARDS = [
    "netflix", "shopify", "kraken", "plaid", "attentive", "nubank",
]

ASHBY_BOARDS = [
    "ramp", "mercury", "arc", "vanta", "deel",
]

WORKABLE_BOARDS = [
    "hotjar", "toptal", "deel", "uphold",
]

SMARTRECRUITERS_BOARDS = [
    "Bosch", "Visa", "Ubisoft", "McDonalds", "Lidl",
]


REGISTRY = {
    "greenhouse":     (GreenhouseScraper,       {"boards": GREENHOUSE_BOARDS}),
    "lever":          (LeverScraper,            {"boards": LEVER_BOARDS}),
    "ashby":          (AshbyScraper,            {"boards": ASHBY_BOARDS}),
    "workable":       (WorkableScraper,         {"boards": WORKABLE_BOARDS}),
    "smartrecruiters":(SmartRecruitersScraper,  {"boards": SMARTRECRUITERS_BOARDS}),

    "remotive":       (RemotiveScraper,         {}),
    "jobicy":         (JobicyScraper,           {"count": 100}),
    "wwr":            (WWRScraper,              {}),
    "remoteok":       (RemoteOKScraper,         {"limit": 100}),
    "arbeitnow":      (ArbeitnowScraper,        {"limit": 100}),
    "himalayas":      (HimalayasScraper,        {"limit": 100}),

    "posao.ba":       (PosaoBaScraper,          {"max_pages": 5}),
    "mojposao.ba":    (MojPosaoBaScraper,       {"max_pages": 5}),
    "posao.hr":       (PosaoHrScraper,          {"max_pages": 5}),
    "helloworld.rs":  (HelloWorldRsScraper,     {"max_pages": 5}),

    "eures":          (EURESScraper,            {"keyword": "developer", "country": "de"}),
    "make-it-in-germany": (MakeItInGermanyScraper, {}),
}

# Sources are explicit and can be enabled by adding a public JSON/RSS endpoint.
# Catalog entries avoid pretending that an unsupported source has a scraper.
CATALOG_SOURCES = [
    "karijera.ba", "posao.rs", "moj-posao.net", "zaposleni.rs", "posao.mk", "vrabotuvanje.mk", "posao.me", "kariere.me", "zaposlitve.si", "optimus.hr",
    "arbeitsagentur", "stepstone", "xing", "karriere.at", "jobs.ch", "jobsinnorway", "workindenmark", "arbetsformedlingen", "te-palvelut", "workinestonia",
    "weworkremotely", "remote.co", "justremote", "workingnomads", "dynamitejobs", "remote.io", "nodesk",
    "teamtailor", "recruitee", "breezy", "jazzhr", "jobvite", "workable", "smartrecruiters",
    "bauforum24", "baunetz", "pflege.de", "hosco", "trans.info", "sezonski.hr",
]
for _source in CATALOG_SOURCES:
    REGISTRY.setdefault(_source, (CatalogScraper, {"source": _source}))


PRIORITY_TIERS = {
    "critical": ["posao.ba", "mojposao.ba", "eures", "greenhouse", "lever", "ashby"],
    "high":     ["helloworld.rs", "posao.hr", "remotive", "jobicy", "workable", "smartrecruiters"],
    "medium":   ["wwr", "arbeitnow", "remoteok", "himalayas", "make-it-in-germany"],
}


def get_scraper(name: str):
    if name not in REGISTRY:
        return None, {}
    cls, kwargs = REGISTRY[name]
    return (cls(**kwargs) if cls is CatalogScraper else cls()), ({k: v for k, v in kwargs.items() if k != "source"})


def get_scrapers_for_tier(tier: str) -> list[tuple[str, object, dict]]:
    names = PRIORITY_TIERS.get(tier, [])
    out = []
    for name in names:
        s, kwargs = get_scraper(name)
        if s:
            out.append((name, s, kwargs))
    return out
