import json, sys, pathlib
sys.stdout.reconfigure(encoding="utf-8")
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import tax as T
rows = json.load(open(here / "_calc_js.json", encoding="utf-8"))
bad = 0
for kind, p, v, js in rows:
    if kind == "acq": py = T.acquisition(p, bool(v))["total"]
    elif kind == "gift": py = T.gift_tax(p, v)["tax_filed"]
    elif kind == "inh": py = T.inherit_tax(p, v >= 10, v % 10)["tax_filed"]
    elif kind == "cg":
        py = T.capgain_general(p, "lt1" if v == "lt1" else "lt2" if v == "lt2" else "basic", 0 if v in ("lt1", "lt2") else int(v[1:]))["total"]
    elif kind == "one":
        pr, h, l = v.split(":"); py = T.capgain_onehouse(float(pr), p, int(h), int(l))["total"]
    elif kind == "fl": py = T.freelancer(p * 5, v)["refund"]
    elif kind == "it": py = T.income_tax(p)["total"]
    elif kind == "vs": py = T.vat_from_supply(p)["total"]
    elif kind == "vt": py = T.vat_from_total(p)["supply"]
    else: py = T.prop_tax(p, bool(v))["total"]
    if int(py) != int(js):
        bad += 1
        if bad < 6: print("불일치", kind, p, v, py, js)
print("py vs js 불일치", bad, "/", len(rows))
