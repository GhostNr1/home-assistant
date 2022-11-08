"""Helper script to update currency list from the official source."""
import pathlib

import black
from bs4 import BeautifulSoup
import requests

BASE = """
\"\"\"Automatically generated by currencies.py.

To update, run python3 -m script.currencies
\"\"\"

ACTIVE_CURRENCIES = {{ {} }}

HISTORIC_CURRENCIES = {{ {} }}
""".strip()

req = requests.get(
    "https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-one.xml"
)
soup = BeautifulSoup(req.content, "xml")
active_currencies = sorted(
    {
        x.Ccy.contents[0]
        for x in soup.ISO_4217.CcyTbl.children
        if x.name == "CcyNtry"
        and x.Ccy
        and x.CcyMnrUnts.contents[0] != "N.A."
        and "IsFund" not in x.CcyNm.attrs
        and x.Ccy.contents[0] != "UYW"
    }
)

req = requests.get(
    "https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-three.xml"
)
soup = BeautifulSoup(req.content, "xml")
historic_currencies = sorted(
    {
        x.Ccy.contents[0]
        for x in soup.ISO_4217.HstrcCcyTbl.children
        if x.name == "HstrcCcyNtry"
        and x.Ccy
        and "IsFund" not in x.CcyNm.attrs
        and x.Ccy.contents[0] not in active_currencies
    }
)

pathlib.Path("homeassistant/generated/currencies.py").write_text(
    black.format_str(
        BASE.format(repr(active_currencies)[1:-1], repr(historic_currencies)[1:-1]),
        mode=black.Mode(),
    )
)