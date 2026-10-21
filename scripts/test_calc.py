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
    else: py = T.prop_tax(p, bool(v))["total"]
    if int(py) != int(js):
        bad += 1
        if bad < 6: print("불일치", kind, p, v, py, js)
print("py vs js 불일치", bad, "/", len(rows))
