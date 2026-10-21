# -*- coding: utf-8 -*-
"""우아세금 정적 사이트 생성기 → _site/.  사용: python scripts/build_site.py"""
import sys, json, re, shutil, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from common import *
import tax as T

def table(heads, rows, num=()):
    th = "".join('<th%s>%s</th>' % (' class="num"' if i in num else "", h) for i, h in enumerate(heads))
    body = "".join("<tr>%s</tr>" % "".join('<td%s>%s</td>' % (' class="num"' if i in num else "", v) for i, v in enumerate(r)) for r in rows)
    return '<div class="tbl-wrap"><table class="tbl"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, body)

def chips(items): return '<div class="chips">%s</div>' % "".join('<a class="chip" href="%s">%s</a>' % (u, esc(t)) for t, u in items)

def amt(n):
    """원 → '6억 5천만원' 식 표기"""
    n = int(round(n))
    eok, rest = divmod(n, 100_000_000)
    man = rest // 10_000
    parts = []
    if eok: parts.append("%d억" % eok)
    if man:
        ch, mn = divmod(man, 1000)
        s = ("%d천" % ch) if ch else ""
        if mn: s += ("%d" % mn)
        parts.append(s + "만원" if (ch or mn) else "")
    out = " ".join(p for p in parts if p)
    if eok and not man: out += "원" if False else ""
    return out or "0원"

def aslug(n):
    return amt(n).replace(" ", "").replace("만원", "")

def pct(x, d=2): return ("%." + str(d) + "f%%") % x

def near(lst, v, k=4):
    i = lst.index(v)
    return lst[max(0, i - k): i + k + 1]

EOK = 100_000_000
CHEON = 10_000_000
ACQ = [i * EOK // 2 for i in range(2, 31)] + [i * EOK for i in range(16, 31)]
GIFT = [i * CHEON for i in range(1, 10)] + [i * EOK // 2 for i in range(2, 21)] + [i * EOK for i in range(11, 21)] + [25 * EOK, 30 * EOK, 40 * EOK, 50 * EOK, 100 * EOK]
INH = [i * EOK for i in range(5, 31)] + [35 * EOK, 40 * EOK, 50 * EOK, 60 * EOK, 70 * EOK, 80 * EOK, 100 * EOK]
PROP = [i * EOK // 2 for i in range(2, 21)] + [i * EOK for i in range(11, 21)] + [25 * EOK, 30 * EOK]
GREL = [("배우자", "spouse"), ("성년자녀", "adult_child"), ("혼인출산", "adult_child_marry"), ("미성년자녀", "minor_child"), ("기타친족", "relative")]
GREL_NAME = {"spouse": "배우자에게", "adult_child": "성년 자녀에게", "adult_child_marry": "혼인·출산한 성년 자녀에게", "minor_child": "미성년 자녀에게", "relative": "기타 친족에게"}
ISC = [(False, 1), (False, 2), (False, 3), (True, 1), (True, 2), (True, 3)]

def isc_slug(sp, k): return ("배우자있음" if sp else "배우자없음") + "-자녀%d명" % k
def isc_name(sp, k): return ("배우자 있고 " if sp else "배우자 없이 ") + "자녀 %d명" % k

# ───────────────────────── 취득세 ─────────────────────────
def page_acq(p):
    path = "/acquisition/%s/" % aslug(p)
    a1 = T.acquisition(p, False); a2 = T.acquisition(p, True)
    r = a1["rate"]
    lead = (f"<p class=\"lead\"><b>주택 {amt(p)}</b>을 유상으로 사면(1주택자·일반 세율) 취득세율은 <b>{pct(r)}</b>입니다. 전용면적 85㎡ 이하면 취득세 {won(a1['tax'])}원과 지방교육세 {won(a1['edu'])}원을 합쳐 약 <b>{won(a1['total'])}원</b>({pct(a1['eff'])}), "
            f"85㎡를 넘으면 농어촌특별세 {won(a2['nong'])}원이 더해져 약 <b>{won(a2['total'])}원</b>({pct(a2['eff'])})입니다. 다주택자·법인 중과, 생애최초 감면은 반영하지 않은 추정입니다.</p>")
    t = table(["구분", "85㎡ 이하", "85㎡ 초과"], [["취득세 (%s)" % pct(a1["rate"]), won(a1["tax"]) + "원", won(a2["tax"]) + "원"], ["지방교육세 (취득세율의 10%)", won(a1["edu"]) + "원", won(a2["edu"]) + "원"],
                                                  ["농어촌특별세 (0.2%)", "면제", won(a2["nong"]) + "원"], ["<b>합계</b>", "<b>%s원</b>" % won(a1["total"]), "<b>%s원</b>" % won(a2["total"])], ["실효세율", pct(a1["eff"]), pct(a2["eff"])]], (1, 2))
    nb = table(["취득가액", "취득세율", "85㎡ 이하 합계", "85㎡ 초과 합계"], [['<a href="/acquisition/%s/">%s</a>' % (aslug(v), amt(v)) if v != p else "<b>%s</b>" % amt(v), pct(T.acq_rate_pct(v)), won(T.acquisition(v, False)["total"]) + "원", won(T.acquisition(v, True)["total"]) + "원"] for v in near(ACQ, p)], (1, 2, 3))
    body = f"""
<div class="page-head"><h1>{amt(p)} 아파트 취득세 — {won(a1['total'])}원 (85㎡ 이하 기준)</h1><p>주택 유상취득 · 1주택자 일반 세율 · 지방교육세·농특세 포함</p></div>
{lead}
{ad()}
{t}
<h2 class="group-title">📈 비슷한 가격의 취득세</h2>
{nb}
<h2 class="group-title">📌 알아두기</h2>
<ul class="lead" style="margin-left:20px"><li>주택 유상취득 세율은 6억 이하 1%, 6억 초과~9억 이하는 (취득가액×2/3억−3)%로 1~3%까지 올라가고, 9억 초과는 3%입니다.</li><li>지방교육세는 취득세율의 10%(0.1~0.3%), 농어촌특별세는 전용 85㎡ 초과 시 0.2%입니다.</li><li>취득일부터 60일 이내에 신고·납부해야 합니다(유상 취득 기준).</li><li>2주택 이상·법인 취득은 중과 규정이 달라 이 표와 다를 수 있습니다. 생애최초 구입 감면도 별도입니다.</li></ul>
{chips([("취득세 계산 전체표", "/acquisition/"), ("취득세 계산기", "/calculator/"), ("재산세 %s" % amt(p), "/property-tax/%s/" % aslug(p)) if p in PROP else ("재산세", "/property-tax/")])}
"""
    faq = [(f"{amt(p)} 아파트 취득세는 얼마인가요?", f"1주택자 일반 세율 기준 취득세율 {pct(r)}로 취득세 {won(a1['tax'])}원, 지방교육세 {won(a1['edu'])}원, 합계 약 {won(a1['total'])}원입니다(85㎡ 초과면 농어촌특별세 {won(a2['nong'])}원 추가)."),
           ("취득세는 언제까지 내나요?", "유상 취득은 취득일(잔금 지급일 또는 등기일 중 빠른 날)부터 60일 이내에 신고·납부합니다."),
           ("취득세 중과는 적용했나요?", "아닙니다. 다주택자·법인 중과와 감면은 반영하지 않은 일반 세율 추정치입니다.")]
    write(path, layout(path, f"{amt(p)} 아파트 취득세 — {won(a1['total'])}원 (취득세율 {pct(r)})", f"주택 {amt(p)} 취득 시 취득세율 {pct(r)}. 85㎡ 이하 합계 {won(a1['total'])}원, 85㎡ 초과 {won(a2['total'])}원(지방교육세·농특세 포함) 계산표.",
          body, faq, [("홈", "/"), ("취득세", "/acquisition/"), (amt(p), path)], coupang=(p % EOK == 0 and p <= 15 * EOK)), "0.8" if p % EOK == 0 else "0.6")

def hub_acq():
    rows = [['<a href="/acquisition/%s/">%s</a>' % (aslug(v), amt(v)), pct(T.acq_rate_pct(v)), won(T.acquisition(v, False)["total"]) + "원", won(T.acquisition(v, True)["total"]) + "원"] for v in ACQ if v % EOK == 0]
    body = f"""
<div class="page-head"><h1>주택 취득세 계산 — 가격별 취득세 표 (2026)</h1><p>1주택자 일반 세율 · 지방교육세·농어촌특별세 포함</p></div>
<p class="lead">주택을 유상으로 살 때 취득세는 <b>6억 원 이하 1%, 9억 원 초과 3%</b>이고 6억~9억은 가격에 따라 1~3%로 올라갑니다. 여기에 지방교육세(취득세율의 10%)와 전용 85㎡ 초과 시 농어촌특별세 0.2%가 붙습니다. 가격을 눌러 85㎡ 이하·초과별 세액을 확인하세요. 다주택자·법인 중과와 생애최초 감면은 반영하지 않았습니다.</p>
{ad()}
{table(['취득가액', '취득세율', '85㎡ 이하 합계', '85㎡ 초과 합계'], rows, (1, 2, 3))}
{chips([("취득세 계산기", "/calculator/"), ("증여세", "/gift/"), ("상속세", "/inheritance/"), ("재산세", "/property-tax/")])}
"""
    faq = [("주택 취득세율은 얼마인가요?", "유상 취득 1주택 기준 6억 원 이하 1%, 6억 초과~9억 이하 1~3%(누진), 9억 초과 3%입니다."), ("지방교육세와 농어촌특별세는 얼마인가요?", "지방교육세는 취득세율의 10%이고 농어촌특별세는 전용 85㎡ 초과 주택에 0.2%가 붙습니다."),
           ("6억 5천만 원짜리 집의 취득세율은?", f"{pct(T.acq_rate_pct(650_000_000))}입니다(6억 초과 구간 누진식 적용).")]
    write("/acquisition/", layout("/acquisition/", "주택 취득세 계산 — 가격별 취득세 표 (6억 1% · 9억 3%)", "아파트 취득세율과 금액별 취득세 계산표. 6억 이하 1%, 9억 초과 3%, 지방교육세·농어촌특별세 포함 합계를 85㎡ 기준으로 비교.", body, faq, [("홈", "/"), ("취득세", "/acquisition/")], coupang=True), "0.9")

# ───────────────────────── 증여세 ─────────────────────────
def gift_rows(a):
    rows = []
    for nm, key in [("배우자", "spouse"), ("성년 자녀", "adult_child"), ("성년 자녀(혼인·출산 공제)", "adult_child_marry"), ("미성년 자녀", "minor_child"), ("기타 친족", "relative"), ("공제 없음", "none")]:
        g = T.gift_tax(a, key)
        rows.append([nm, won(g["ded"]) + "원", won(g["base"]) + "원", pct(g["rate"] * 100, 0) if g["base"] else "-", won(g["tax"]) + "원", won(g["tax_filed"]) + "원"])
    return rows

def page_gift(a):
    path = "/gift/%s/" % aslug(a)
    g = {k: T.gift_tax(a, k) for k in ("spouse", "adult_child", "adult_child_marry", "minor_child", "relative", "none")}
    lead = (f"<p class=\"lead\"><b>{amt(a)}</b>을 증여하면 증여세는 받는 사람에 따라 달라집니다. <b>배우자</b>는 6억 원 공제로 {('세금이 없고' if g['spouse']['tax'] == 0 else '약 ' + won(g['spouse']['tax_filed']) + '원이며')}, <b>성년 자녀</b>는 5천만 원 공제 후 약 <b>{won(g['adult_child']['tax_filed'])}원</b>, 혼인·출산 공제 1억을 더 받으면 약 {won(g['adult_child_marry']['tax_filed'])}원, <b>미성년 자녀</b>는 약 {won(g['minor_child']['tax_filed'])}원입니다(기한 내 자진신고 3% 공제 반영). 10년 이내 같은 사람에게 받은 증여는 합산됩니다.</p>")
    t = table(["받는 사람", "공제", "과세표준", "세율", "산출세액", "자진신고 시(3% 공제)"], gift_rows(a), (1, 2, 3, 4, 5))
    nb = table(["증여 금액", "성년 자녀", "배우자", "미성년 자녀"], [['<a href="/gift/%s/">%s</a>' % (aslug(v), amt(v)) if v != a else "<b>%s</b>" % amt(v), won(T.gift_tax(v, "adult_child")["tax_filed"]) + "원", won(T.gift_tax(v, "spouse")["tax_filed"]) + "원", won(T.gift_tax(v, "minor_child")["tax_filed"]) + "원"] for v in near(GIFT, a)], (1, 2, 3))
    rel_chips = chips([(f"{amt(a)} {lb} 증여세", f"/gift/{aslug(a)}/{sl}/") for sl, lb in [("배우자", "배우자"), ("성년자녀", "성년 자녀"), ("혼인출산", "혼인·출산 자녀"), ("미성년자녀", "미성년 자녀"), ("기타친족", "기타 친족")]])
    body = f"""
<div class="page-head"><h1>{amt(a)} 증여세 — 성년 자녀 {won(g['adult_child']['tax_filed'])}원 · 배우자 {won(g['spouse']['tax_filed'])}원</h1><p>증여재산공제 · 세율 · 자진신고 공제 반영 (2026)</p></div>
{lead}
{ad()}
{t}
<h2 class="group-title">👪 받는 사람별 자세히</h2>
{rel_chips}
<h2 class="group-title">📈 비슷한 금액의 증여세</h2>
{nb}
<h2 class="group-title">📌 알아두기</h2>
<ul class="lead" style="margin-left:20px"><li>증여재산공제는 10년 합산 한도입니다: 배우자 6억, 직계존속→성년 자녀 5천만(미성년 2천만), 기타 친족 1천만 원. 혼인·출산 시 1억 원이 추가됩니다.</li><li>세율은 과세표준 1억 이하 10%, 5억 이하 20%, 10억 이하 30%, 30억 이하 40%, 30억 초과 50%입니다.</li><li>증여일이 속한 달의 말일부터 3개월 이내에 신고하면 산출세액의 3%를 공제받습니다.</li><li>부동산·주식은 시가(또는 보충적 평가액)로 평가하고, 대출을 함께 넘기는 부담부증여는 계산이 달라집니다.</li></ul>
{chips([("증여세 금액별 표", "/gift/"), ("증여재산공제 총정리", "/gift/deduction/"), ("증여세 계산기", "/calculator/")])}
"""
    faq = [(f"{amt(a)}을 자녀에게 증여하면 증여세는?", f"성년 자녀 기준 공제 5천만 원 후 약 {won(g['adult_child']['tax_filed'])}원(자진신고 3% 공제 반영)입니다. 혼인·출산 공제를 받으면 약 {won(g['adult_child_marry']['tax_filed'])}원입니다."),
           (f"{amt(a)}을 배우자에게 증여하면?", f"배우자 공제 6억 원이 적용되어 {('증여세가 없습니다' if g['spouse']['tax'] == 0 else '약 ' + won(g['spouse']['tax_filed']) + '원입니다')}."),
           ("증여세 신고 기한은 언제인가요?", "증여일이 속하는 달의 말일부터 3개월 이내입니다. 기한 내 신고하면 3% 세액공제를 받습니다.")]
    write(path, layout(path, f"{amt(a)} 증여세 — 성년 자녀 {won(g['adult_child']['tax_filed'])}원, 배우자 {won(g['spouse']['tax_filed'])}원", f"{amt(a)} 증여 시 증여세. 성년 자녀 {won(g['adult_child']['tax_filed'])}원, 미성년 자녀 {won(g['minor_child']['tax_filed'])}원, 배우자 {won(g['spouse']['tax_filed'])}원(자진신고 3% 공제). 공제·세율·신고 기한.", body, faq,
          [("홈", "/"), ("증여세", "/gift/"), (amt(a), path)], coupang=(a % EOK == 0 and a <= 10 * EOK)), "0.8" if a % EOK == 0 else "0.6")

def page_gift_rel(a, sl, key):
    path = "/gift/%s/%s/" % (aslug(a), sl)
    g = T.gift_tax(a, key); nm = T.GIFT_REL[key][0]
    lead = (f"<p class=\"lead\"><b>{amt(a)}을 {GREL_NAME[key]} 증여</b>하면 증여재산공제 {won(g['ded'])}원을 빼고 과세표준 {won(g['base'])}원에 {pct(g['rate'] * 100, 0) if g['base'] else '세율 없음'} 세율을 적용해 산출세액 {won(g['tax'])}원, 기한 내 신고하면 <b>약 {won(g['tax_filed'])}원</b>입니다(실효세율 {pct(g['eff'])}).</p>")
    t = table(["항목", "금액"], [["증여 금액", won(a) + "원"], ["증여재산공제(%s)" % esc(nm), "-" + won(g["ded"]) + "원"], ["과세표준", won(g["base"]) + "원"], ["세율", pct(g["rate"] * 100, 0) if g["base"] else "-"], ["산출세액", won(g["tax"]) + "원"], ["자진신고 세액공제(3%)", "-" + won(g["tax"] - g["tax_filed"]) + "원"], ["<b>납부세액</b>", "<b>%s원</b>" % won(g["tax_filed"])]], (1,))
    body = f"""
<div class="page-head"><h1>{amt(a)} {nm} 증여세 — {won(g['tax_filed'])}원</h1><p>{esc(nm)}에게 증여 · 공제 {won(g['ded'])}원</p></div>
{lead}
{ad()}
{t}
{chips([(f"{amt(a)} 증여세(받는 사람별)", f"/gift/{aslug(a)}/"), ("증여재산공제 총정리", "/gift/deduction/"), ("증여세 금액별 표", "/gift/")])}
<div class="note-box">10년 이내 같은 증여자(직계존속은 부모·조부모 합산)에게 받은 증여재산은 합산해 계산합니다. 실제 세액은 재산 평가와 개인 사정에 따라 달라집니다.</div>
"""
    faq = [(f"{amt(a)}을 {GREL_NAME[key]} 증여하면 증여세는?", f"공제 {won(g['ded'])}원을 빼고 계산한 납부세액은 약 {won(g['tax_filed'])}원입니다."), ("증여세 공제는 10년마다 새로 받나요?", "네. 증여재산공제는 10년간 합산한 금액에 대해 한도가 적용되고 10년이 지나면 다시 공제받을 수 있습니다.")]
    write(path, layout(path, f"{amt(a)} {nm} 증여세 — {won(g['tax_filed'])}원 (공제 {amt(g['ded']) if g['ded'] else '없음'})", f"{amt(a)}을 {GREL_NAME[key]} 증여할 때 증여세 {won(g['tax_filed'])}원. 공제 {won(g['ded'])}원, 과세표준·세율·자진신고 공제 계산.", body, faq, [("홈", "/"), ("증여세", "/gift/"), (amt(a), "/gift/%s/" % aslug(a)), (nm, path)]), "0.5")

def hub_gift():
    rows = [['<a href="/gift/%s/">%s</a>' % (aslug(v), amt(v)), won(T.gift_tax(v, "adult_child")["tax_filed"]) + "원", won(T.gift_tax(v, "spouse")["tax_filed"]) + "원", won(T.gift_tax(v, "minor_child")["tax_filed"]) + "원"] for v in GIFT if v >= 3 * CHEON and (v % EOK == 0 or v < EOK)]
    body = f"""
<div class="page-head"><h1>증여세 계산 — 금액별·받는 사람별 증여세 표 (2026)</h1><p>증여재산공제 · 누진세율 · 자진신고 공제 반영</p></div>
<p class="lead">증여세는 증여재산공제(배우자 6억, 성년 자녀 5천만, 미성년 자녀 2천만, 기타 친족 1천만 원, 혼인·출산 1억 추가)를 뺀 과세표준에 10~50% 누진세율을 적용합니다. 금액을 눌러 받는 사람별 세액을 확인하세요.</p>
{ad()}
{table(['증여 금액', '성년 자녀', '배우자', '미성년 자녀'], rows, (1, 2, 3))}
{chips([("증여재산공제 총정리", "/gift/deduction/"), ("상속세", "/inheritance/"), ("증여세 계산기", "/calculator/")])}
"""
    faq = [("증여세 공제는 얼마인가요?", "10년 합산 기준 배우자 6억, 직계존속→성년 자녀 5천만(미성년 2천만), 기타 친족 1천만 원이며 혼인·출산 시 1억 원이 추가됩니다."), ("자녀에게 1억 증여하면 증여세는?", f"성년 자녀 기준 약 {won(T.gift_tax(EOK, 'adult_child')['tax_filed'])}원입니다(자진신고 3% 공제 반영).")]
    write("/gift/", layout("/gift/", "증여세 계산 — 금액별·받는 사람별 증여세 표 (배우자 6억 공제)", "증여세 금액별 계산표. 배우자 6억·성년 자녀 5천만·미성년 자녀 2천만 공제 후 세액과 신고 기한, 혼인·출산 1억 추가공제.", body, faq, [("홈", "/"), ("증여세", "/gift/")], coupang=True), "0.9")
    rows2 = [[nm, won(T.GIFT_REL[k][1]) + "원", note] for nm, k, note in [("배우자", "spouse", "10년 합산"), ("성년 자녀 (직계존속→직계비속)", "adult_child", "부모·조부모 합산 한도"), ("미성년 자녀", "minor_child", "10년 합산"), ("기타 친족(6촌 이내 혈족·4촌 이내 인척)", "relative", "10년 합산"), ("혼인·출산 추가공제", "adult_child_marry", "기본 5천만 + 1억 = 1.5억(합계 한도 1억)")]]
    body = f"""
<div class="page-head"><h1>증여재산공제 총정리 — 배우자 6억·성년 자녀 5천만·혼인출산 1억</h1><p>10년 합산 한도</p></div>
<p class="lead">증여재산공제는 같은 증여자로부터 <b>10년 동안 받은 증여를 합산</b>해 한도까지 공제합니다. 직계존속(부모·조부모)은 한 사람으로 보아 합산하고, 혼인신고일 전후 2년(총 4년) 이내 또는 자녀 출생일로부터 2년 이내에 증여받으면 최대 1억 원이 추가 공제됩니다.</p>
{ad()}
{table(['받는 사람', '공제 한도', '비고'], rows2, (1,))}
{chips([("증여세 금액별 표", "/gift/"), ("증여세 계산기", "/calculator/")])}
<div class="note-box">공제 한도는 현행 세법 기준이며 개정될 수 있습니다. 증여세 신고 전 국세청 안내와 세무 전문가 확인이 필요합니다.</div>
"""
    write("/gift/deduction/", layout("/gift/deduction/", "증여재산공제 한도 총정리 — 배우자 6억, 자녀 5천만, 혼인·출산 1억", "증여재산공제 한도: 배우자 6억, 성년 자녀 5천만, 미성년 자녀 2천만, 기타 친족 1천만, 혼인·출산 추가 1억. 10년 합산 규정.", body,
          [("증여재산공제는 10년마다 새로 받나요?", "네. 10년 합산 기준이라 10년이 지나면 다시 공제받을 수 있습니다.")], [("홈", "/"), ("증여세", "/gift/"), ("증여재산공제", "/gift/deduction/")]), "0.7")

# ───────────────────────── 상속세 ─────────────────────────
def page_inh(e):
    path = "/inheritance/%s/" % aslug(e)
    rs = {(sp, k): T.inherit_tax(e, sp, k) for sp, k in ISC}
    r1, r2, r3 = rs[(False, 2)], rs[(True, 2)], rs[(False, 1)]
    lead = (f"<p class=\"lead\"><b>상속재산 {amt(e)}</b>의 상속세는 배우자 유무와 자녀 수에 따라 달라집니다. 배우자 없이 자녀 2명이 상속하면 일괄공제 5억 원을 빼고 약 <b>{won(r1['tax_filed'])}원</b>, 배우자가 있고 자녀가 2명이면 배우자공제 {won(r2['d_spouse'])}원까지 더해져 약 <b>{won(r2['tax_filed'])}원</b>입니다(신고세액공제 3% 반영, 금융재산·동거주택 공제 등은 제외한 추정).</p>")
    rows = []
    for sp, k in ISC:
        r = rs[(sp, k)]
        rows.append(['<a href="/inheritance/%s/%s/">%s</a>' % (aslug(e), isc_slug(sp, k), isc_name(sp, k)), won(r["d_lump"]) + "원", won(r["d_spouse"]) + "원" if sp else "-", won(r["base"]) + "원", won(r["tax_filed"]) + "원", pct(r["eff"])])
    t = table(["상속인", "일괄공제", "배우자공제", "과세표준", "납부 상속세(3% 공제)", "실효세율"], rows, (1, 2, 3, 4, 5))
    nb = table(["상속재산", "배우자 없음·자녀 2명", "배우자 있음·자녀 2명"], [['<a href="/inheritance/%s/">%s</a>' % (aslug(v), amt(v)) if v != e else "<b>%s</b>" % amt(v), won(T.inherit_tax(v, False, 2)["tax_filed"]) + "원", won(T.inherit_tax(v, True, 2)["tax_filed"]) + "원"] for v in near(INH, e)], (1, 2))
    body = f"""
<div class="page-head"><h1>상속재산 {amt(e)} 상속세 — 배우자·자녀 수별 (2026)</h1><p>일괄공제 5억 · 배우자공제 · 누진세율 10~50%</p></div>
{lead}
{ad()}
{t}
<h2 class="group-title">📈 비슷한 재산의 상속세</h2>
{nb}
<h2 class="group-title">📌 알아두기</h2>
<ul class="lead" style="margin-left:20px"><li>상속공제는 일괄공제 5억 원(또는 기초공제 2억+자녀공제 1인당 5천만 원 중 큰 금액)이며 배우자가 있으면 배우자 상속공제(최소 5억~최대 30억 원)가 더해집니다.</li><li>배우자공제는 법정상속분(배우자 1.5 : 자녀 1 비율)만큼 상속받는다고 가정해 계산했습니다.</li><li>순금융재산 상속공제(최대 2억), 동거주택 상속공제, 사전증여 합산(10년·5년), 재산 평가 방식에 따라 세액이 크게 달라집니다.</li><li>상속개시일(사망일)이 속한 달의 말일부터 6개월 이내에 신고하면 3% 세액공제를 받습니다.</li></ul>
{chips([("상속세 금액별 표", "/inheritance/"), ("증여세", "/gift/"), ("상속세 계산기", "/calculator/")])}
<div class="note-box">상속세 제도는 개편 논의가 진행 중입니다(공제 상향·과세 방식 변경 등). 이 페이지는 현행 세법 기준이며 개정되면 달라집니다.</div>
"""
    faq = [(f"{amt(e)} 상속세는 얼마인가요?", f"배우자 없이 자녀 2명이 상속하면 약 {won(r1['tax_filed'])}원, 배우자가 있고 자녀가 2명이면 약 {won(r2['tax_filed'])}원입니다(현행 공제 기준 추정)."),
           ("상속세가 없는 재산은 얼마까지인가요?", "일괄공제 5억 원 기준 배우자 없이는 5억 원 이하, 배우자가 있으면 배우자공제 최소 5억 원이 더해져 보통 10억 원까지 상속세가 없습니다(금융재산공제 등 제외)."),
           ("상속세 신고 기한은 언제인가요?", "상속개시일이 속하는 달의 말일부터 6개월 이내입니다(해외 거주자 9개월).")]
    write(path, layout(path, f"상속재산 {amt(e)} 상속세 — 자녀 2명 {won(r1['tax_filed'])}원, 배우자 있으면 {won(r2['tax_filed'])}원", f"상속재산 {amt(e)}의 상속세 계산. 배우자·자녀 수별 일괄공제·배우자공제 후 세액과 실효세율, 신고 기한.", body, faq, [("홈", "/"), ("상속세", "/inheritance/"), (amt(e), path)], coupang=(e % EOK == 0 and e <= 20 * EOK)), "0.8" if e % EOK == 0 else "0.6")

def page_inh_sc(e, sp, k):
    path = "/inheritance/%s/%s/" % (aslug(e), isc_slug(sp, k))
    r = T.inherit_tax(e, sp, k)
    lead = (f"<p class=\"lead\"><b>상속재산 {amt(e)}</b>을 {isc_name(sp, k)}이(가) 상속하면 일괄공제 {won(r['d_lump'])}원{('과 배우자공제 ' + won(r['d_spouse']) + '원') if sp else ''}을 빼 과세표준 {won(r['base'])}원, 산출세액 {won(r['tax'])}원이고 기한 내 신고하면 <b>약 {won(r['tax_filed'])}원</b>(실효세율 {pct(r['eff'])})입니다.</p>")
    t = table(["항목", "금액"], [["상속재산", won(e) + "원"], ["일괄공제", "-" + won(r["d_lump"]) + "원"]] + ([["배우자 상속공제", "-" + won(r["d_spouse"]) + "원"]] if sp else []) +
              [["과세표준", won(r["base"]) + "원"], ["세율", pct(r["rate"] * 100, 0) if r["base"] else "-"], ["산출세액", won(r["tax"]) + "원"], ["신고세액공제(3%)", "-" + won(r["tax"] - r["tax_filed"]) + "원"], ["<b>납부세액</b>", "<b>%s원</b>" % won(r["tax_filed"])]], (1,))
    body = f"""
<div class="page-head"><h1>상속재산 {amt(e)} 상속세 — {isc_name(sp, k)}: {won(r['tax_filed'])}원</h1><p>현행 공제 기준 추정</p></div>
{lead}
{ad()}
{t}
{chips([(f"{amt(e)} 상속세(전체 경우)", f"/inheritance/{aslug(e)}/"), ("상속세 금액별 표", "/inheritance/"), ("상속세 계산기", "/calculator/")])}
<div class="note-box">금융재산·동거주택 공제와 사전증여 합산 등은 반영하지 않은 단순 추정입니다. 상속세는 개편 논의 중이므로 신고 전 최신 세법을 확인하세요.</div>
"""
    faq = [(f"{amt(e)} 상속세 {isc_name(sp, k)}는?", f"약 {won(r['tax_filed'])}원입니다(일괄공제{'·배우자공제' if sp else ''} 후, 신고세액공제 3% 반영)."), ("배우자공제는 어떻게 계산했나요?", "법정상속분(배우자 1.5 : 자녀 각 1)만큼 상속받는다고 가정하고 최소 5억~최대 30억 원 범위로 계산했습니다." if sp else "배우자가 없는 경우라 배우자공제는 적용하지 않았습니다.")]
    write(path, layout(path, f"{amt(e)} 상속세 — {isc_name(sp, k)} {won(r['tax_filed'])}원", f"상속재산 {amt(e)}을 {isc_name(sp, k)}이(가) 상속할 때 상속세 {won(r['tax_filed'])}원. 일괄공제·배우자공제·세율 계산.", body, faq, [("홈", "/"), ("상속세", "/inheritance/"), (amt(e), "/inheritance/%s/" % aslug(e)), (isc_name(sp, k), path)]), "0.5")

def hub_inh():
    rows = [['<a href="/inheritance/%s/">%s</a>' % (aslug(v), amt(v)), won(T.inherit_tax(v, False, 2)["tax_filed"]) + "원", won(T.inherit_tax(v, True, 2)["tax_filed"]) + "원"] for v in INH]
    body = f"""
<div class="page-head"><h1>상속세 계산 — 상속재산별 상속세 표 (2026)</h1><p>일괄공제 5억 · 배우자공제 · 신고세액공제 3%</p></div>
<p class="lead">상속세는 상속재산에서 일괄공제(5억 원)와 배우자 상속공제 등을 뺀 과세표준에 10~50% 누진세율을 적용합니다. 배우자가 있으면 보통 <b>10억 원까지</b> 상속세가 없습니다. 재산 금액을 눌러 배우자·자녀 수별 세액을 확인하세요. 현행 세법 기준이며 공제 확대 개편이 논의 중입니다.</p>
{ad()}
{table(['상속재산', '배우자 없음·자녀 2명', '배우자 있음·자녀 2명'], rows, (1, 2))}
{chips([("증여세", "/gift/"), ("상속세 계산기", "/calculator/")])}
"""
    faq = [("상속세 면세 한도는?", "배우자와 자녀가 모두 있으면 일괄공제 5억+배우자공제 최소 5억으로 보통 10억 원까지 상속세가 없습니다."), ("20억 상속세는 얼마인가요?", f"배우자 없이 자녀 2명이면 약 {won(T.inherit_tax(20 * EOK, False, 2)['tax_filed'])}원, 배우자가 있으면 약 {won(T.inherit_tax(20 * EOK, True, 2)['tax_filed'])}원입니다.")]
    write("/inheritance/", layout("/inheritance/", "상속세 계산 — 상속재산별 상속세 표 (일괄공제 5억·배우자공제)", "상속재산 금액별 상속세 계산표. 일괄공제 5억·배우자공제 반영, 배우자 유무·자녀 수에 따른 세액과 신고 기한.", body, faq, [("홈", "/"), ("상속세", "/inheritance/")], coupang=True), "0.9")

# ───────────────────────── 재산세 ─────────────────────────
def page_prop(p):
    path = "/property-tax/%s/" % aslug(p)
    a = T.prop_tax(p, False); b = T.prop_tax(p, True)
    lead = (f"<p class=\"lead\">공시가격 <b>{amt(p)}</b> 주택의 연간 재산세(도시지역분·지방교육세 포함)는 <b>1세대 1주택</b>이면 약 <b>{won(b['total'])}원</b>(공정시장가액비율 {int(b['ratio'] * 100)}%{', 특례세율 적용' if b['special'] else ', 공시가 9억 초과라 특례세율 미적용'}), "
            f"다주택 등 일반이면 약 <b>{won(a['total'])}원</b>(공정시장가액비율 60%)입니다. 7월과 9월에 절반씩 냅니다. 종합부동산세는 포함하지 않습니다.</p>")
    t = table(["항목", "1세대 1주택", "일반(다주택 등)"], [["공정시장가액비율", f"{int(b['ratio'] * 100)}%", "60%"], ["과세표준", won(b["base"]) + "원", won(a["base"]) + "원"], ["재산세", won(b["pt"]) + "원", won(a["pt"]) + "원"], ["도시지역분(0.14%)", won(b["urban"]) + "원", won(a["urban"]) + "원"],
                                              ["지방교육세(재산세의 20%)", won(b["edu"]) + "원", won(a["edu"]) + "원"], ["<b>연 합계</b>", "<b>%s원</b>" % won(b["total"]), "<b>%s원</b>" % won(a["total"])], ["7월·9월 각각", won(b["total"] / 2) + "원", won(a["total"] / 2) + "원"], ["공시가 대비", pct(b["eff"], 3), pct(a["eff"], 3)]], (1, 2))
    nb = table(["공시가격", "1세대 1주택", "일반"], [['<a href="/property-tax/%s/">%s</a>' % (aslug(v), amt(v)) if v != p else "<b>%s</b>" % amt(v), won(T.prop_tax(v, True)["total"]) + "원", won(T.prop_tax(v, False)["total"]) + "원"] for v in near(PROP, p)], (1, 2))
    body = f"""
<div class="page-head"><h1>공시가격 {amt(p)} 재산세 — 1주택 {won(b['total'])}원 (2026)</h1><p>공정시장가액비율 · 특례세율 · 도시지역분·지방교육세 포함</p></div>
{lead}
{ad()}
{t}
<h2 class="group-title">📈 비슷한 공시가격의 재산세</h2>
{nb}
<h2 class="group-title">📌 알아두기</h2>
<ul class="lead" style="margin-left:20px"><li>재산세 과세기준일은 6월 1일이며 주택분은 7월(7/16~7/31)과 9월(9/16~9/30)에 절반씩 납부합니다. 세액이 20만 원 이하면 7월에 한 번에 냅니다.</li><li>1세대 1주택(공시가 9억 이하)은 특례세율(0.05~0.35%)과 낮은 공정시장가액비율(43~45%)이 적용됩니다. 특례세율은 2026년 12월 31일까지 한시 적용으로 알려져 있어 이후에는 달라질 수 있습니다.</li><li>도시지역분(과세표준 0.14%)은 도시지역 주택에 부과되고 지방교육세는 재산세의 20%입니다. 건물분 지역자원시설세(소방분)는 별도입니다.</li><li>공시가 합계가 일정 금액을 넘으면 종합부동산세가 따로 부과됩니다.</li></ul>
{chips([("재산세 금액별 표", "/property-tax/"), ("재산세 계산기", "/calculator/"), ("취득세", "/acquisition/")])}
"""
    faq = [(f"공시가 {amt(p)} 재산세는 얼마인가요?", f"1세대 1주택이면 연 약 {won(b['total'])}원, 일반(다주택 등)이면 연 약 {won(a['total'])}원입니다(도시지역분·지방교육세 포함 추정)."), ("재산세는 언제 내나요?", "주택분은 7월과 9월에 절반씩 냅니다. 세액이 20만 원 이하이면 7월에 한꺼번에 냅니다."),
           ("1세대 1주택 특례는 무엇인가요?", "공시가 9억 원 이하 1주택에는 낮은 세율(0.05~0.35%)이, 1주택자에게는 공정시장가액비율 43~45%가 적용됩니다.")]
    write(path, layout(path, f"공시가격 {amt(p)} 재산세 — 1주택 {won(b['total'])}원, 일반 {won(a['total'])}원", f"공시가격 {amt(p)} 주택 재산세. 1세대 1주택 {won(b['total'])}원, 일반 {won(a['total'])}원(도시지역분·지방교육세 포함), 납부 시기와 특례세율.", body, faq, [("홈", "/"), ("재산세", "/property-tax/"), (amt(p), path)], coupang=(p % EOK == 0 and p <= 15 * EOK)), "0.8" if p % EOK == 0 else "0.6")

def hub_prop():
    rows = [['<a href="/property-tax/%s/">%s</a>' % (aslug(v), amt(v)), won(T.prop_tax(v, True)["total"]) + "원", won(T.prop_tax(v, False)["total"]) + "원"] for v in PROP if v % EOK == 0]
    body = f"""
<div class="page-head"><h1>재산세 계산 — 공시가격별 주택 재산세 표 (2026)</h1><p>1세대 1주택 특례 · 일반 · 도시지역분·지방교육세 포함</p></div>
<p class="lead">주택 재산세는 공시가격에 공정시장가액비율(일반 60%, 1세대 1주택 43~45%)을 곱한 과세표준에 0.1~0.4%(1주택 특례 0.05~0.35%) 누진세율을 적용하고 도시지역분과 지방교육세를 더해 계산합니다. 공시가격을 눌러 확인하세요. 종합부동산세는 포함하지 않습니다.</p>
{ad()}
{table(['공시가격', '1세대 1주택', '일반(다주택 등)'], rows, (1, 2))}
{chips([("재산세 계산기", "/calculator/"), ("취득세", "/acquisition/"), ("증여세", "/gift/")])}
"""
    faq = [("재산세는 어떻게 계산하나요?", "공시가격×공정시장가액비율=과세표준에 누진세율을 적용하고 도시지역분(0.14%)과 지방교육세(재산세의 20%)를 더합니다."), ("공시가 5억 아파트 재산세는?", f"1세대 1주택이면 연 약 {won(T.prop_tax(5 * EOK, True)['total'])}원입니다(추정).")]
    write("/property-tax/", layout("/property-tax/", "주택 재산세 계산 — 공시가격별 재산세 표 (1세대 1주택 특례)", "공시가격별 주택 재산세. 1세대 1주택 특례세율·공정시장가액비율, 도시지역분·지방교육세 포함 연간 세액과 7월·9월 납부.", body, faq, [("홈", "/"), ("재산세", "/property-tax/")], coupang=True), "0.9")

# ───────────────────────── 계산기·기타 ─────────────────────────
def page_calc():
    body = """
<div class="page-head"><h1>부동산 세금 계산기 — 취득세·증여세·상속세·재산세</h1><p>입력한 값은 서버로 전송되지 않습니다</p></div>
<p class="lead">현행 세법의 일반 규정으로 계산한 참고용 추정치입니다. 금액은 <b>원 단위</b>로 입력하세요(예: 6억 5천만 원 → 650000000).</p>
<div class="tool-box"><h3 style="margin-top:0">🏠 취득세 (주택 유상취득)</h3>
<div class="tool-row"><div><label for="a-p">취득가액(원)</label><input id="a-p" type="number" value="650000000" style="width:170px"></div><div><label for="a-o">전용면적</label><select id="a-o"><option value="0">85㎡ 이하</option><option value="1">85㎡ 초과</option></select></div><button class="btn-p" id="a-go">계산</button></div><div class="tool-out" id="a-out">계산 결과가 여기에 표시됩니다.</div></div>
<div class="tool-box"><h3 style="margin-top:0">🎁 증여세</h3>
<div class="tool-row"><div><label for="g-p">증여 금액(원)</label><input id="g-p" type="number" value="300000000" style="width:170px"></div><div><label for="g-r">받는 사람</label><select id="g-r"><option value="spouse">배우자</option><option value="adult_child" selected>성년 자녀</option><option value="adult_child_marry">성년 자녀(혼인·출산)</option><option value="minor_child">미성년 자녀</option><option value="relative">기타 친족</option><option value="none">공제 없음</option></select></div><button class="btn-p" id="g-go">계산</button></div><div class="tool-out" id="g-out">계산 결과가 여기에 표시됩니다.</div></div>
<div class="tool-box"><h3 style="margin-top:0">📜 상속세</h3>
<div class="tool-row"><div><label for="i-p">상속재산(원)</label><input id="i-p" type="number" value="1500000000" style="width:170px"></div><div><label for="i-s">배우자</label><select id="i-s"><option value="0">없음</option><option value="1" selected>있음</option></select></div><div><label for="i-k">자녀 수</label><select id="i-k"><option>1</option><option selected>2</option><option>3</option><option>4</option></select></div><button class="btn-p" id="i-go">계산</button></div><div class="tool-out" id="i-out">계산 결과가 여기에 표시됩니다.</div></div>
<div class="tool-box"><h3 style="margin-top:0">🏢 재산세 (주택)</h3>
<div class="tool-row"><div><label for="p-p">공시가격(원)</label><input id="p-p" type="number" value="500000000" style="width:170px"></div><div><label for="p-h">구분</label><select id="p-h"><option value="1">1세대 1주택</option><option value="0">일반(다주택 등)</option></select></div><button class="btn-p" id="p-go">계산</button></div><div class="tool-out" id="p-out">계산 결과가 여기에 표시됩니다.</div></div>
""" + ad() + """
<script src="/assets/js/calc.js"></script>
"""
    faq = [("계산 결과는 정확한가요?", "현행 세법의 일반 규정으로 계산한 참고용 추정치입니다. 감면·중과·재산 평가 등에 따라 실제 세액은 달라질 수 있습니다."), ("입력한 금액은 저장되나요?", "아니요. 모든 계산은 브라우저 안에서만 이루어지고 서버로 전송되지 않습니다.")]
    write("/calculator/", layout("/calculator/", "부동산 세금 계산기 — 취득세·증여세·상속세·재산세 (2026)", "취득세, 증여세, 상속세, 재산세를 한 곳에서 계산합니다. 현행 세법 기준 참고용 추정, 입력값은 서버로 전송되지 않습니다.", body, faq, [("홈", "/"), ("계산기", "/calculator/")]), "0.9")

def page_home():
    body = f"""
<div class="hero"><h1>🧾 부동산 세금 계산 — 취득세·증여세·상속세·재산세</h1><p>금액별 세액을 표로 바로 확인하세요. 현행 세법 기준 참고용 추정치입니다.</p></div>
{ad()}
<div class="card-grid">
<a class="card" href="/acquisition/"><b>🏠 취득세</b><span>주택 가격별 취득세 — 6억 1%, 9억 3%</span></a>
<a class="card" href="/gift/"><b>🎁 증여세</b><span>금액·받는 사람별 — 배우자 6억 공제</span></a>
<a class="card" href="/inheritance/"><b>📜 상속세</b><span>일괄공제 5억·배우자공제 반영</span></a>
<a class="card" href="/property-tax/"><b>🏢 재산세</b><span>공시가격별 — 1세대 1주택 특례</span></a>
<a class="card" href="/calculator/"><b>🧮 세금 계산기</b><span>직접 금액 입력</span></a>
</div>
<h2 class="group-title">🔥 많이 찾는 계산</h2>
{chips([("취득세 6억", "/acquisition/6억/"), ("취득세 9억", "/acquisition/9억/"), ("증여세 1억", "/gift/1억/"), ("증여세 5억", "/gift/5억/"), ("상속세 10억", "/inheritance/10억/"), ("상속세 20억", "/inheritance/20억/"), ("재산세 공시가 5억", "/property-tax/5억/"), ("재산세 공시가 10억", "/property-tax/10억/")])}
<p class="lead">우아세금은 현행 세법의 일반 규정(공제·세율)을 적용해 금액별 부동산 세금을 계산해 두었습니다. 감면·중과·개인 사정은 반영하지 않으니 신고·납부 전에는 홈택스·위택스 모의계산과 세무 전문가 확인이 필요합니다. 자세한 기준은 <a href="/about/">계산 기준</a>을 참고하세요. 연봉 실수령액과 연말정산은 <a href="https://wooayeonbong.wooahouse.com">우아연봉</a>에서 확인하세요.</p>
"""
    faq = [("세금 계산 결과를 믿어도 되나요?", "현행 세법의 일반 규정으로 계산한 참고용 추정치입니다. 실제 세액은 감면·중과·재산 평가 등에 따라 달라질 수 있어 신고 전 확인이 필요합니다."), ("세법이 바뀌면 어떻게 되나요?", "세율·공제는 이 사이트의 계산 모듈 한 곳에서 관리하며 개정 시 갱신합니다. 다만 반영 시차가 있을 수 있습니다.")]
    write("/", layout("/", "우아세금 — 취득세·증여세·상속세·재산세 금액별 계산 (2026)", "취득세, 증여세, 상속세, 재산세를 금액별로 계산해 둔 부동산 세금 계산 사이트. 현행 세법 기준 참고용 추정, 계산기 제공.", body, faq), "1.0")

def page_about():
    body = """
<div class="page-head"><h1>계산 기준</h1><p>어떤 규정을 적용했는지 공개합니다 (2026년 10월 기준)</p></div>
<h2 class="group-title">🏠 취득세</h2><p class="lead">주택 유상취득 1주택 일반 세율: 6억 이하 1%, 6억 초과~9억 이하 (취득가액×2/3억−3)%, 9억 초과 3%. 지방교육세는 취득세율의 10%, 농어촌특별세는 전용 85㎡ 초과 시 0.2%. 다주택자·법인 중과, 생애최초·출산 감면, 원시취득·증여취득은 반영하지 않았습니다.</p>
<h2 class="group-title">🎁 증여세</h2><p class="lead">증여재산공제(10년 합산): 배우자 6억, 직계존속→성년 자녀 5천만(미성년 2천만), 기타 친족 1천만, 혼인·출산 1억 추가. 과세표준 1억 이하 10%, 5억 이하 20%(누진공제 1천만), 10억 이하 30%(6천만), 30억 이하 40%(1억 6천만), 30억 초과 50%(4억 6천만). 기한 내 신고 시 산출세액 3% 공제. 재산 평가·부담부증여·합산과세는 반영하지 않았습니다.</p>
<h2 class="group-title">📜 상속세</h2><p class="lead">일괄공제 5억 원과 (기초공제 2억+자녀공제 1인당 5천만 원) 중 큰 금액을 공제하고, 배우자가 있으면 법정상속분(배우자 1.5 : 자녀 1)만큼 상속받는다고 가정해 배우자공제(최소 5억~최대 30억)를 적용했습니다. 세율은 증여세와 같은 5단계 누진세율이며 신고세액공제 3%를 반영했습니다. 금융재산·동거주택 상속공제, 사전증여 합산은 제외했습니다. 상속세 개편(공제 상향 등)이 논의 중이어서 개정되면 결과가 달라집니다.</p>
<h2 class="group-title">🏢 재산세</h2><p class="lead">주택 재산세: 공정시장가액비율 일반 60%, 1세대 1주택 43%(공시가 3억 이하)·44%(6억 이하)·45%(초과). 표준세율 6천만 원 이하 0.1%, 1.5억 이하 0.15%, 3억 이하 0.25%, 3억 초과 0.4%(누진공제 방식), 1세대 1주택 공시가 9억 이하 특례세율 0.05·0.1·0.2·0.35%. 도시지역분 과세표준의 0.14%, 지방교육세 재산세의 20%. 소방분 지역자원시설세와 종합부동산세는 포함하지 않았습니다.</p>
<h2 class="group-title">⚠️ 한계</h2><p class="lead">이 사이트의 계산은 일반 규정에 따른 참고용 추정입니다. 개인별 감면·중과·비과세, 재산 평가, 가산세, 지방자치단체 조례 등에 따라 실제 세액은 달라지며 세법은 수시로 개정됩니다. 신고·납부 전에 국세청 홈택스, 위택스 모의계산과 세무 전문가 상담으로 확인하세요.</p>
<h2 class="group-title">📬 문의·정정</h2><p class="lead">오류 제보는 <a href="mailto:ingmaster83@gmail.com">ingmaster83@gmail.com</a> 으로 보내 주세요.</p>
"""
    write("/about/", layout("/about/", "계산 기준 — 적용한 세율·공제와 한계", "우아세금이 적용한 취득세·증여세·상속세·재산세 세율과 공제, 계산의 한계를 공개합니다.", body, None, [("홈", "/"), ("계산 기준", "/about/")]), "0.5")

def page_privacy():
    body = """
<div class="page-head"><h1>개인정보처리방침</h1></div>
<p class="lead">우아세금(wooatax.wooahouse.com, 이하 “서비스”)은 회원가입·로그인을 요구하지 않으며 이용자의 개인정보를 직접 수집하지 않습니다. 계산기에 입력한 값은 브라우저 안에서만 처리되고 서버로 전송되지 않습니다.</p>
<h3>자동 수집 정보</h3><p class="lead">서비스 개선을 위해 Google Analytics로 방문자 수·페이지뷰 등 익명 통계를 수집하며, Google AdSense와 쿠팡 파트너스는 맞춤 광고를 위해 쿠키를 사용할 수 있습니다. 쿠키는 브라우저 설정에서 비활성화할 수 있습니다. (<a href="https://policies.google.com/privacy">Google 개인정보처리방침</a>, <a href="https://policies.google.com/technologies/ads">Google 광고 정책</a>)</p>
<h3>쿠팡 파트너스</h3><p class="lead">일부 페이지에는 쿠팡 파트너스 활동의 일환으로 광고가 포함되어 있으며 이에 따른 수수료를 제공받을 수 있습니다.</p>
<h3>문의</h3><p class="lead"><a href="mailto:ingmaster83@gmail.com">ingmaster83@gmail.com</a></p>
<p class="note">최종 수정일: 2026년 10월 21일</p>
"""
    write("/privacy/", layout("/privacy/", "개인정보처리방침", "우아세금 개인정보처리방침", body, None, [("홈", "/"), ("개인정보처리방침", "/privacy/")]), sitemap=False)

def make_og():
    f = ROOT / "assets" / "og-image.png"
    if f.exists(): return
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return
    im = Image.new("RGB", (1200, 630), (22, 101, 52)); dr = ImageDraw.Draw(im)
    def font(sz):
        for n in ("malgunbd.ttf", "malgun.ttf", "NanumGothicBold.ttf"):
            try: return ImageFont.truetype(n, sz)
            except Exception: pass
        return ImageFont.load_default()
    dr.rounded_rectangle((90, 90, 1110, 540), 40, fill=(255, 255, 255))
    dr.text((150, 150), "우아세금", font=font(110), fill=(21, 83, 45))
    dr.text((150, 300), "취득세 · 증여세 · 상속세 · 재산세", font=font(54), fill=(31, 41, 55))
    dr.text((150, 380), "금액별 계산 (2026)", font=font(54), fill=(31, 41, 55))
    dr.text((150, 470), "wooatax.wooahouse.com", font=font(34), fill=(107, 114, 128))
    im.save(f)

def main():
    t0 = time.time(); make_og()
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets", dirs_exist_ok=True)
    for nf in ROOT.glob("naver*.html"): shutil.copy(nf, OUT / nf.name)
    for p in ACQ: page_acq(p)
    for a in GIFT:
        page_gift(a)
        for sl, key in GREL: page_gift_rel(a, sl, key)
    for e in INH:
        page_inh(e)
        for sp, k in ISC: page_inh_sc(e, sp, k)
    for p in PROP: page_prop(p)
    hub_acq(); hub_gift(); hub_inh(); hub_prop(); page_calc(); page_home(); page_about(); page_privacy()
    today = time.strftime("%Y-%m-%d")
    urls = "".join("<url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>" % (BASE, q(p), today, pr) for p, pr in WRITTEN)
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>\n' % urls, encoding="utf-8")
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % BASE, encoding="utf-8")
    (OUT / "CNAME").write_text("wooatax.wooahouse.com\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    nf = layout("/404.html", "페이지를 찾을 수 없습니다", "요청한 페이지를 찾을 수 없습니다.", '<div class="page-head"><h1>페이지를 찾을 수 없습니다</h1></div><div class="chips"><a class="chip" href="/">홈</a><a class="chip" href="/calculator/">계산기</a></div>', None, None, noindex=True)
    (OUT / "404.html").write_text(nf, encoding="utf-8")
    print("pages", len(WRITTEN), "elapsed", round(time.time() - t0), "s")

if __name__ == "__main__":
    main()
