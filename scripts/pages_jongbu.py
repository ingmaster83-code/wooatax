# -*- coding: utf-8 -*-
"""우아세금 확장 3: 종합부동산세(주택분) 공시가격별 페이지. build_site.main() 에서 호출.
2026년 납부분 현행법 기준: 공제 9억(1세대 1주택 12억), 공정시장가액비율 60%, 세율 2주택 이하 0.5~2.7%·3주택 이상 0.5~5.0%,
1세대 1주택 연령·보유 공제 최대 80%, 농어촌특별세 20%. 2026년 세제개편안(공정시장가액비율 인상 등)은 2027년 이후 적용 논의라 반영하지 않았다.
재산세 중복 공제는 근사, 세부담 상한(150%)·조정대상지역 특례·합산배제는 반영하지 않는다."""
from common import *
import tax as T
import build_site as B

table, chips, near = B.table, B.chips, B.near
EOK = B.EOK
def k(x): return "{:,}".format(int(round(x)))
def eok(n): return ("%d억" % n) if float(n).is_integer() else "%s억" % n

P = "/comprehensive-property-tax/"
ONE = [13, 14, 15, 16, 17, 18, 19, 20, 22, 25, 30, 35, 40, 50, 60, 80, 100]
MULTI = [10, 12, 15, 18, 20, 25, 30, 35, 40, 50, 60, 80, 100]
JOINT = [13, 14, 15, 16, 17, 18, 20, 22, 25, 30, 35, 40]
AGES = [("60세 미만", 0), ("60~64세", 60), ("65~69세", 65), ("70세 이상", 70)]
HOLDS = [("5년 미만", 0), ("5~9년", 5), ("10~14년", 10), ("15년 이상", 15)]

NOTE = ("2026년 납부분(12월 1~15일) 현행법 기준의 참고용 추정입니다. 주택 공시가격 합계에서 공제액(일반 9억원, 1세대 1주택 12억원)을 뺀 금액에 공정시장가액비율 60%를 곱해 과세표준을 구하고 "
        "누진세율(2주택 이하 0.5~2.7%, 3주택 이상 0.5~5.0%)을 적용한 뒤 재산세 중복분과 1세대 1주택 연령·보유 공제(최대 80%)를 빼고 농어촌특별세 20%를 더했습니다. "
        "재산세 중복 공제는 비례 근사이며 세부담 상한, 합산배제, 일시적 2주택 등은 반영하지 않았습니다. 2026년 세제개편안의 공정시장가액비율 인상 등은 2027년 이후 적용이 논의 중이어서 이 표에 포함하지 않았습니다. 실제 세액은 국세청 홈택스 고지서와 모의계산으로 확인하세요.")

def steps(r, nongtxt=True):
    rows = [["공제 후 과세표준(공시가격-공제)×60%", won(r["tb"]) + "원"], ["산출세액(누진세율)", won(r["gross"]) + "원"], ["재산세 중복분 공제(근사)", "-" + won(r["dup"]) + "원"]]
    if r["credit"]: rows.append(["연령·보유 세액공제 %d%%" % round(r["credit"] * 100), "-" + won(f10((r["gross"] - r["dup"]) * r["credit"])) + "원"])
    rows += [["종합부동산세", "<b>%s원</b>" % won(r["final"])], ["농어촌특별세(20%)", won(r["nong"]) + "원"], ["<b>종부세+농특세 합계</b>", "<b>%s원</b>" % won(r["total"])], ["참고: 재산세(별도, 근사)", won(r["prop"]) + "원"], ["보유세 합계(종부세+재산세)", won(r["holding"]) + "원"]]
    return table(["항목", "금액"], rows, (1,))

def f10(x): return int(x // 10 * 10)

def page_one(n):
    h = n * EOK; path = P + "one/%d억/" % n
    a = T.jongbu(h, "one"); best = T.jongbu(h, "one", 70, 15)
    mat = table(["연령 \\ 보유기간"] + [x for x, _ in HOLDS], [[lab] + [won(T.jongbu(h, "one", ag, 0 if hv == 0 and False else hv)["total"]) + "원" for _, hv in HOLDS] for lab, ag in AGES], (1, 2, 3, 4))
    nb = table(["공시가격", "공제 없음", "70세·15년 보유"], [[('<a href="%s">%s억</a>' % (P + "one/%d억/" % v, v)) if v != n else "<b>%d억</b>" % v, won(T.jongbu(v * EOK, "one")["total"]) + "원", won(T.jongbu(v * EOK, "one", 70, 15)["total"]) + "원"] for v in near(ONE, n, 3)], (1, 2))
    body = f"""
<div class="page-head"><h1>공시가격 {n}억 1세대 1주택 종부세 — {won(a['total'])}원 (2026)</h1><p>연령·보유기간 공제별 종합부동산세와 농어촌특별세</p></div>
<p class="lead">공시가격 <b>{n}억 원</b> 주택 1채만 가진 1세대 1주택자의 종합부동산세는 연령·보유 공제가 없으면 종부세 {won(a['final'])}원에 농어촌특별세 {won(a['nong'])}원을 더한 <b>약 {won(a['total'])}원</b>입니다. 70세 이상이고 15년 이상 보유해 공제를 최대(80%)로 받으면 <b>약 {won(best['total'])}원</b>으로 줄어듭니다. 과세표준은 ({n}억 − 12억) × 60% = {won(a['tb'])}원입니다.</p>
<div class="stat-row"><div class="stat"><small>종부세+농특세</small><b>{won(a['total'])}원</b></div><div class="stat"><small>최대 공제 시</small><b>{won(best['total'])}원</b></div><div class="stat"><small>재산세(별도)</small><b>{won(a['prop'])}원</b></div></div>
{ad()}
<h2 class="group-title">🧮 계산 과정 (공제 없음)</h2>
{steps(a)}
<h2 class="group-title">👴 연령·보유기간별 종부세+농특세</h2>
{mat}
<p class="note">{NOTE}</p>
<h2 class="group-title">📈 비슷한 공시가격</h2>
{nb}
{chips([("종부세 계산 표", P), ("%d억 다주택" % n if n in MULTI else "다주택 종부세", P + "multi/%d억/" % (n if n in MULTI else 20)), ("재산세 계산", "/property-tax/"), ("양도세 계산", "/capital-gains/")])}
"""
    faq = [(f"공시가격 {n}억 1주택 종부세는 얼마인가요?", f"연령·보유 공제가 없으면 종부세와 농어촌특별세를 합쳐 약 {won(a['total'])}원입니다. 최대 공제(70세 이상·15년 이상)는 약 {won(best['total'])}원입니다."),
           ("1세대 1주택 종부세 공제액은 얼마인가요?", "공시가격 12억원까지는 종부세가 없고, 12억원을 넘는 금액에 공정시장가액비율 60%를 곱한 금액이 과세표준입니다."),
           ("고령자·장기보유 공제는 어떻게 되나요?", "60세 20%, 65세 30%, 70세 40%와 5년 20%, 10년 40%, 15년 50% 공제를 합산하며 최대 80%입니다.")]
    write(path, layout(path, f"공시가격 {n}억 1세대 1주택 종부세 {won(a['total'])}원 (2026)", f"공시가격 {n}억 1세대 1주택 종합부동산세는 약 {won(a['total'])}원, 70세 이상·15년 보유 공제 시 {won(best['total'])}원. 연령·보유기간별 표와 계산 과정.", body, faq,
                       [("홈", "/"), ("종부세", P), ("1주택", P + "one/"), ("%d억" % n, path)]), "0.6")

def page_multi(n, mode):
    h = n * EOK; slug = "multi" if mode == "multi2" else "multi3"; label = "2주택(일반)" if mode == "multi2" else "3주택 이상(중과)"
    path = P + "%s/%d억/" % (slug, n)
    a = T.jongbu(h, mode); o = T.jongbu(h, "multi3" if mode == "multi2" else "multi2")
    lst = MULTI
    nb = table(["공시가격 합계", "2주택 이하", "3주택 이상"], [[('<a href="%s">%d억</a>' % (P + "%s/%d억/" % (slug, v), v)) if v != n else "<b>%d억</b>" % v, won(T.jongbu(v * EOK, "multi2")["total"]) + "원", won(T.jongbu(v * EOK, "multi3")["total"]) + "원"] for v in near(lst, n, 3)], (1, 2))
    num = 2 if mode == "multi2" else 3
    body = f"""
<div class="page-head"><h1>공시가격 합계 {n}억 {label} 종부세 — {won(a['total'])}원 (2026)</h1><p>다주택자 종합부동산세와 농어촌특별세 · 공제 9억원</p></div>
<p class="lead">보유 주택의 공시가격 합계가 <b>{n}억 원</b>인 {label} 소유자의 종합부동산세는 공제액 9억원을 적용해 종부세 {won(a['final'])}원, 농어촌특별세 {won(a['nong'])}원, 합계 <b>약 {won(a['total'])}원</b>입니다(과세표준 {won(a['tb'])}원). {'같은 금액을 3주택 이상 중과세율로 계산하면 약 %s원입니다.' % won(o['total']) if mode == 'multi2' else '2주택 이하 일반세율이라면 약 %s원입니다.' % won(o['total'])} 재산세(별도) 약 {won(a['prop'])}원을 더한 보유세 합계는 약 {won(a['holding'])}원입니다.</p>
<div class="stat-row"><div class="stat"><small>종부세+농특세</small><b>{won(a['total'])}원</b></div><div class="stat"><small>재산세(별도, 근사)</small><b>{won(a['prop'])}원</b></div><div class="stat"><small>보유세 합계</small><b>{won(a['holding'])}원</b></div></div>
{ad()}
<h2 class="group-title">🧮 계산 과정</h2>
{steps(a)}
<p class="note">재산세는 주택 {num}채의 공시가격이 같다고 가정해 계산했습니다. 주택별 공시가격이 다르면 재산세와 중복 공제가 달라집니다. {NOTE}</p>
<h2 class="group-title">📈 비슷한 공시가격 합계</h2>
{nb}
{chips([("종부세 계산 표", P), ("1세대 1주택 종부세", P + "one/"), ("재산세 계산", "/property-tax/"), ("취득세 계산", "/acquisition/")])}
"""
    faq = [(f"공시가격 합계 {n}억 {label} 종부세는 얼마인가요?", f"약 {won(a['total'])}원(종부세 {won(a['final'])}원 + 농어촌특별세 {won(a['nong'])}원)입니다."), ("다주택자 종부세 공제액은?", "공시가격 합계에서 9억원을 공제합니다(1세대 1주택만 12억원)."), ("3주택 이상은 세율이 어떻게 다른가요?", "과세표준 12억원 초과분부터 3주택 이상은 2.0~5.0%의 중과세율이, 2주택 이하는 1.3~2.7%가 적용됩니다.")]
    write(path, layout(path, f"공시가격 {n}억 {label} 종부세 {won(a['total'])}원 (2026)", f"공시가격 합계 {n}억 {label} 종합부동산세는 약 {won(a['total'])}원(농어촌특별세 포함). 계산 과정과 재산세를 더한 보유세 합계.", body, faq,
                       [("홈", "/"), ("종부세", P), ("다주택", P + "multi/"), ("%d억" % n, path)]), "0.6")

def page_joint(n):
    h = n * EOK; path = P + "joint/%d억/" % n
    j = T.jongbu_joint(h, 65, 10)
    rows = [["공동명의(부부 50:50, 각자 6억 공제)", won(j["a_total"]) + "원"]] + [["단독명의 특례 선택 — %s·%s 보유" % (al, hl), won(T.jongbu(h, "one", ag, hv)["total"]) + "원"] for (al, ag), (hl, hv) in ((AGES[0], HOLDS[0]), (AGES[2], HOLDS[2]), (AGES[3], HOLDS[3]))]
    nb = table(["공시가격", "공동명의", "단독 특례(65세·10년)"], [[('<a href="%s">%d억</a>' % (P + "joint/%d억/" % v, v)) if v != n else "<b>%d억</b>" % v, won(T.jongbu_joint(v * EOK, 65, 10)["a_total"]) + "원", won(T.jongbu(v * EOK, "one", 65, 10)["total"]) + "원"] for v in near(JOINT, n, 3)], (1, 2))
    best = "공동명의" if j["a_total"] <= j["b"]["total"] else "단독 특례(65세·10년 보유 가정)"
    body = f"""
<div class="page-head"><h1>공시가격 {n}억 1주택 공동명의 종부세 — {won(j['a_total'])}원 (2026)</h1><p>부부 공동명의 vs 단독명의 특례 선택 비교</p></div>
<p class="lead">공시가격 <b>{n}억 원</b> 주택을 부부가 절반씩 가진 1주택 공동명의는 각자 6억원을 공제받아 종부세와 농어촌특별세를 합쳐 <b>약 {won(j['a_total'])}원</b>입니다. 1세대 1주택 특례(12억원 공제와 연령·보유 공제)를 신청하면 주 소유자가 65세이고 10년 보유한 경우 <b>약 {won(j['b']['total'])}원</b>으로 계산됩니다. 이 가정에서는 <b>{best}</b> 쪽이 유리합니다.</p>
{ad()}
<h2 class="group-title">⚖️ 공동명의 vs 단독명의 특례</h2>
{table(['방식', '종부세+농특세'], rows, (1,))}
<p class="note">공동명의 1주택자는 9월 16일~30일에 관할 세무서에 신청하면 1세대 1주택 특례(12억원 공제와 연령·보유 공제)를 적용받을 수 있습니다. 어느 쪽이 유리한지는 공시가격과 연령·보유기간에 따라 달라지므로 위 표에서 비교하세요. {NOTE}</p>
<h2 class="group-title">📈 비슷한 공시가격</h2>
{nb}
{chips([("종부세 계산 표", P), ("1세대 1주택 종부세", P + "one/"), ("재산세 계산", "/property-tax/")])}
"""
    faq = [(f"공시가격 {n}억 공동명의 종부세는 얼마인가요?", f"각자 6억원 공제 기준 부부 합산 약 {won(j['a_total'])}원입니다(농어촌특별세 포함)."), ("공동명의가 단독명의보다 유리한가요?", "공시가격이 낮고 고령·장기보유 공제를 받기 어려우면 공동명의가, 고령·장기보유 공제를 크게 받으면 단독 특례가 유리한 경우가 많습니다."), ("특례 신청은 언제 하나요?", "매년 9월 16일부터 9월 30일까지 관할 세무서에 신청합니다(신청하지 않으면 공동명의 방식이 적용됩니다).")]
    write(path, layout(path, f"공시가격 {n}억 1주택 공동명의 종부세 {won(j['a_total'])}원 (2026)", f"공시가격 {n}억 1주택 부부 공동명의 종합부동산세는 약 {won(j['a_total'])}원. 단독명의 1세대 1주택 특례와 비교한 표.", body, faq,
                       [("홈", "/"), ("종부세", P), ("공동명의", P + "joint/"), ("%d억" % n, path)]), "0.6")

def hub_sub(slug, title_h, sub, lead, lst, mode, label, desc_title):
    path = P + slug + "/"
    if mode == "joint":
        rows = [['<a href="%s%d억/">%d억</a>' % (path, v, v), won(T.jongbu_joint(v * EOK, 65, 10)["a_total"]) + "원", won(T.jongbu(v * EOK, "one", 65, 10)["total"]) + "원", won(T.jongbu(v * EOK, "one")["total"]) + "원"] for v in lst]
        t = table(["공시가격", "공동명의(각자 6억 공제)", "단독 특례(65세·10년)", "단독 특례(공제 없음)"], rows, (1, 2, 3))
    elif mode == "one":
        rows = [['<a href="%s%d억/">%d억</a>' % (path, v, v), won(T.jongbu(v * EOK, "one")["total"]) + "원", won(T.jongbu(v * EOK, "one", 65, 10)["total"]) + "원", won(T.jongbu(v * EOK, "one", 70, 15)["total"]) + "원"] for v in lst]
        t = table(["공시가격", "공제 없음", "65세·10년 보유", "70세·15년 보유"], rows, (1, 2, 3))
    else:
        rows = [['<a href="%s%d억/">%d억</a>' % (path, v, v), won(T.jongbu(v * EOK, mode)["total"]) + "원", won(T.jongbu(v * EOK, mode)["holding"]) + "원"] for v in lst]
        t = table(["공시가격 합계", "종부세+농특세", "재산세 포함 보유세"], rows, (1, 2))
    body = f"""
<div class="page-head"><h1>{title_h}</h1><p>{sub}</p></div>
<p class="lead">{lead}</p>
{ad()}
{t}
<p class="note">{NOTE}</p>
{chips([("종부세 계산 전체", P), ("재산세 계산", "/property-tax/"), ("양도세 계산", "/capital-gains/")])}
"""
    write(path, layout(path, desc_title, sub, body, [(label + " 종부세는 어떻게 계산하나요?", "공시가격 합계에서 공제액을 뺀 금액에 공정시장가액비율 60%를 곱해 과세표준을 구하고 누진세율을 적용합니다.")], [("홈", "/"), ("종부세", P), (label, path)]), "0.8")

def page_hub():
    one = [13, 15, 18, 20, 25, 30, 40, 50]
    rows = [['<a href="%sone/%d억/">%d억</a>' % (P, v, v), won(T.jongbu(v * EOK, "one")["total"]) + "원", won(T.jongbu(v * EOK, "multi2")["total"]) + "원" if v >= 10 else "-", won(T.jongbu(v * EOK, "multi3")["total"]) + "원"] for v in one]
    body = f"""
<div class="page-head"><h1>종합부동산세(종부세) 계산 — 공시가격별 세액표 (2026)</h1><p>1세대 1주택 · 다주택 · 공동명의 · 12월 납부</p></div>
<p class="lead"><b>종합부동산세</b>는 주택 공시가격 합계가 공제액(일반 <b>9억원</b>, 1세대 1주택 <b>12억원</b>)을 넘을 때 내는 세금으로 매년 12월 1일~15일에 납부합니다. 과세표준은 (공시가격 합계 − 공제액) × 공정시장가액비율 60%이고 세율은 2주택 이하 0.5~2.7%, 3주택 이상 0.5~5.0%입니다. 공시가격 15억원 1세대 1주택은 연령·보유 공제가 없으면 약 {won(T.jongbu(15 * EOK, 'one')['total'])}원(농어촌특별세 포함)입니다. 공시가격을 눌러 계산 과정을 확인하세요.</p>
{ad()}
<h2 class="group-title">📊 공시가격별 종부세+농특세 비교</h2>
{table(['공시가격(합계)', '1세대 1주택', '2주택 이하', '3주택 이상'], rows, (1, 2, 3))}
{chips([("1세대 1주택", P + "one/"), ("다주택 2주택 이하", P + "multi/"), ("3주택 이상 중과", P + "multi3/"), ("1주택 공동명의", P + "joint/")])}
<p class="note">{NOTE}</p>
"""
    faq = [("종부세는 언제 내나요?", "매년 12월 1일부터 15일까지 납부하며 고지서는 11월 말에 발송됩니다. 납부 세액이 250만원을 넘으면 분납할 수 있습니다."), ("종부세 공제액은 얼마인가요?", "공시가격 합계에서 일반은 9억원, 1세대 1주택은 12억원을 공제합니다."), ("종부세에 농어촌특별세도 붙나요?", "네. 종부세액의 20%가 농어촌특별세로 함께 부과됩니다.")]
    write(P, layout(P, "종합부동산세(종부세) 계산 — 공시가격별 세액표 (2026)", "종부세 계산: 공시가격별 1세대 1주택·다주택·공동명의 종합부동산세와 농어촌특별세. 공제 9억(1주택 12억), 12월 납부.", body, faq, [("홈", "/"), ("종부세", P)], coupang=True), "0.9")

def all_pages():
    n0 = len(WRITTEN)
    for n in ONE: page_one(n)
    for n in MULTI: page_multi(n, "multi2"); page_multi(n, "multi3")
    for n in JOINT: page_joint(n)
    hub_sub("one", "1세대 1주택 종부세 계산 — 공시가격별 (2026)", "공시가격 12억원 공제 · 연령·보유기간 공제", "1세대 1주택자의 종합부동산세를 공시가격별로 정리했습니다. 공시가격 12억원까지는 종부세가 없고 초과분에 대해 연령·보유기간 공제(최대 80%)가 적용됩니다.", ONE, "one", "1세대 1주택", "1세대 1주택 종부세 계산 — 공시가격별 세액표 (2026)")
    hub_sub("multi", "다주택자(2주택 이하) 종부세 계산 — 공시가격 합계별 (2026)", "공제 9억원 · 일반세율 0.5~2.7%", "2주택 이하 일반세율을 적용받는 소유자의 종합부동산세를 공시가격 합계별로 정리했습니다.", MULTI, "multi2", "2주택 이하", "다주택 2주택 종부세 계산 — 공시가격 합계별 세액표 (2026)")
    hub_sub("multi3", "3주택 이상 종부세 중과 계산 — 공시가격 합계별 (2026)", "공제 9억원 · 중과세율 0.5~5.0%", "3주택 이상 중과세율을 적용받는 소유자의 종합부동산세를 공시가격 합계별로 정리했습니다.", MULTI, "multi3", "3주택 이상", "3주택 이상 종부세 중과 계산 — 공시가격 합계별 세액표 (2026)")
    hub_sub("joint", "1주택 공동명의 종부세 계산 — 공동명의 vs 단독 특례 (2026)", "부부 50:50 · 각자 6억원 공제 · 특례 선택 비교", "부부 공동명의 1주택자의 종합부동산세를 공시가격별로 계산하고 1세대 1주택 특례(단독명의)를 선택했을 때와 비교했습니다.", JOINT, "joint", "공동명의", "1주택 공동명의 종부세 — 공동명의 vs 단독 특례 비교 (2026)")
    page_hub()
    return len(WRITTEN) - n0
