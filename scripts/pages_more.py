# -*- coding: utf-8 -*-
"""우아세금 확장: 양도소득세(주택)·프리랜서 3.3% 정산·종합소득세·부가가치세 페이지. build_site.main() 에서 호출.
현행 세법 일반 규정(2026-10 기준) 참고용 추정. 다주택 중과·비교과세·감면은 반영하지 않는다."""
from common import *
import tax as T
import build_site as B

amt, aslug, pct, table, chips, near = B.amt, B.aslug, B.pct, B.table, B.chips, B.near
EOK, CHEON = B.EOK, B.CHEON
MAN = 10_000

def mslug(n):
    return ("%d억" % (n // EOK)) if n % EOK == 0 else ("%d만" % (n // MAN))

# ───────────────────────── 양도소득세 ─────────────────────────
GAINS = [10 * MAN * 100, 3 * CHEON, 5 * CHEON, 7 * CHEON, EOK, EOK * 3 // 2, 2 * EOK, 3 * EOK, 4 * EOK, 5 * EOK, 7 * EOK, 10 * EOK, 15 * EOK, 20 * EOK]
HOLDS = [("1년미만", "lt1", 0, "보유 1년 미만"), ("2년미만", "lt2", 1, "보유 1년 이상 2년 미만"), ("3년", "basic", 3, "보유 3년"), ("5년", "basic", 5, "보유 5년"), ("10년", "basic", 10, "보유 10년"), ("15년", "basic", 15, "보유 15년 이상")]
CG_NOTE = ("주택 양도 기준 일반 규정입니다. 1년 미만 보유 70%, 1~2년 60%, 2년 이상은 기본세율(6~45%)이며 3년 이상 보유하면 장기보유특별공제(연 2%, 최대 30%)가 적용됩니다. "
           "양도소득 기본공제 250만 원과 지방소득세 10%를 반영했고 조정대상지역 다주택 중과, 비사업용 토지, 1세대 1주택 비과세·감면은 반영하지 않았습니다.")

def cg(gain, mode, years): return T.capgain_general(gain, mode, years)

def cg_rows(g):
    rows = []
    for sl, mode, yrs, label in HOLDS:
        r = cg(g, mode, yrs)
        rows.append(['<a href="/capital-gains/%s/%s/">%s</a>' % (aslug(g), sl, label), pct(r["ltd"] * 100, 0) if r["ltd"] else "-", won(r["taxable"]) + "원", pct(r["rate"] * 100, 0) if r["taxable"] else "-", won(r["tax"]) + "원", won(r["local"]) + "원", "<b>%s원</b>" % won(r["total"]), pct(r["eff"])])
    return rows

def page_cg(g):
    path = "/capital-gains/%s/" % aslug(g)
    r2, r5, r10 = cg(g, "basic", 3), cg(g, "basic", 5), cg(g, "basic", 10)
    st1, st2 = cg(g, "lt1", 0), cg(g, "lt2", 0)
    lead = (f"<p class=\"lead\">주택 <b>양도차익 {amt(g)}</b>이면 보유 기간에 따라 양도소득세(지방소득세 포함)가 크게 달라집니다. 1년 미만 보유는 약 <b>{won(st1['total'])}원</b>(세율 70%), 1~2년은 약 {won(st2['total'])}원(60%), "
            f"3년 보유하면 약 <b>{won(r2['total'])}원</b>, 5년이면 약 {won(r5['total'])}원, 10년이면 약 {won(r10['total'])}원입니다. 1세대 1주택 비과세와 다주택 중과는 반영하지 않은 추정입니다.</p>")
    t = table(["보유 기간", "장기보유공제", "과세표준", "세율", "양도세", "지방소득세", "합계", "실효세율"], cg_rows(g), (1, 2, 3, 4, 5, 6, 7))
    nb = table(["양도차익", "1년 미만", "3년 보유", "10년 보유"], [['<a href="/capital-gains/%s/">%s</a>' % (aslug(v), amt(v)) if v != g else "<b>%s</b>" % amt(v), won(cg(v, "lt1", 0)["total"]) + "원", won(cg(v, "basic", 3)["total"]) + "원", won(cg(v, "basic", 10)["total"]) + "원"] for v in near(GAINS, g)], (1, 2, 3))
    body = f"""
<div class="page-head"><h1>양도차익 {amt(g)} 양도소득세 — 3년 보유 {won(r2['total'])}원 (주택)</h1><p>보유 기간별 · 장기보유특별공제 · 지방소득세 포함 (2026)</p></div>
{lead}
{ad()}
{t}
<h2 class="group-title">📈 비슷한 양도차익</h2>
{nb}
<h2 class="group-title">📌 알아두기</h2>
<ul class="lead" style="margin-left:20px"><li>양도차익 = 양도가액 − 취득가액 − 필요경비(취득세·중개수수료·자본적 지출 등)입니다.</li><li>{CG_NOTE}</li><li>양도일이 속한 달의 말일부터 2개월 이내에 예정신고·납부해야 하고, 다음 해 5월에 확정신고(다른 양도소득이 있을 때)를 합니다.</li><li>1세대 1주택(2년 이상 보유)은 양도가 12억 이하면 비과세이므로 <a href="/capital-gains/one-house/">1세대 1주택 양도세</a> 표를 확인하세요.</li></ul>
{chips([("양도세 전체 표", "/capital-gains/"), ("1세대 1주택 양도세", "/capital-gains/one-house/"), ("양도세 계산기", "/calculator/"), ("취득세", "/acquisition/")])}
"""
    faq = [(f"양도차익 {amt(g)}이면 양도소득세는 얼마인가요?", f"3년 보유 시 약 {won(r2['total'])}원, 5년 보유 시 약 {won(r5['total'])}원, 10년 보유 시 약 {won(r10['total'])}원입니다(지방소득세 포함, 비과세·중과 제외 추정). 1년 미만 보유는 {won(st1['total'])}원입니다."),
           ("장기보유특별공제는 얼마인가요?", "일반 주택은 3년 이상 보유하면 6%에서 시작해 매년 2%p씩 늘어 15년 이상 30%까지 공제됩니다."),
           ("양도세 신고는 언제 하나요?", "양도일이 속한 달의 말일부터 2개월 이내에 예정신고·납부해야 합니다.")]
    write(path, layout(path, f"양도차익 {amt(g)} 양도소득세 — 3년 보유 {won(r2['total'])}원, 10년 {won(r10['total'])}원", f"주택 양도차익 {amt(g)}의 양도소득세. 1년 미만 {won(st1['total'])}원, 3년 보유 {won(r2['total'])}원, 10년 보유 {won(r10['total'])}원(지방소득세 포함). 장기보유특별공제·세율.", body, faq,
          [("홈", "/"), ("양도소득세", "/capital-gains/"), (amt(g), path)], coupang=(g in (EOK, 2 * EOK, 3 * EOK, 5 * EOK))), "0.8" if g % EOK == 0 else "0.6")

def page_cg_hold(g, sl, mode, yrs, label):
    path = "/capital-gains/%s/%s/" % (aslug(g), sl)
    r = cg(g, mode, yrs)
    how = {"lt1": "1년 미만 보유한 주택은 세율 70%를 적용합니다.", "lt2": "1년 이상 2년 미만 보유한 주택은 세율 60%를 적용합니다."}.get(mode, f"2년 이상 보유한 주택은 기본세율(6~45%)을 적용하며 장기보유특별공제는 {pct(r['ltd'] * 100, 0) if r['ltd'] else '없음(3년 미만)'}입니다.")
    lead = (f"<p class=\"lead\"><b>{label}</b> 주택을 <b>양도차익 {amt(g)}</b>에 팔면 양도소득세는 약 <b>{won(r['tax'])}원</b>, 지방소득세 {won(r['local'])}원을 더해 <b>{won(r['total'])}원</b>(양도차익의 {pct(r['eff'])})입니다. {how} 실제로 손에 남는 차익은 약 {won(g - r['total'])}원입니다.</p>")
    rows = [["양도차익", won(g) + "원"], ["장기보유특별공제", (pct(r["ltd"] * 100, 0) + " (%s원)" % won(g * r["ltd"])) if r["ltd"] else "없음"], ["양도소득 기본공제", "2,500,000원"], ["과세표준", won(r["taxable"]) + "원"],
            ["세율", pct(r["rate"] * 100, 0) if r["taxable"] else "-"], ["양도소득세", won(r["tax"]) + "원"], ["지방소득세(10%)", won(r["local"]) + "원"], ["<b>합계</b>", "<b>%s원</b>" % won(r["total"])]]
    t = table(["항목", "금액"], rows, (1,))
    body = f"""
<div class="page-head"><h1>양도차익 {amt(g)} · {label} 양도세 — {won(r['total'])}원</h1><p>주택 양도 · 기본공제 250만 원 · 지방소득세 포함</p></div>
{lead}
{ad()}
{t}
<p class="note">{CG_NOTE}</p>
{chips([(f"양도차익 {amt(g)} 보유 기간별 비교", "/capital-gains/%s/" % aslug(g)), ("양도세 전체 표", "/capital-gains/"), ("1세대 1주택 양도세", "/capital-gains/one-house/")])}
"""
    faq = [(f"{label} 양도차익 {amt(g)}의 양도세는?", f"지방소득세 포함 약 {won(r['total'])}원입니다."), ("보유 기간이 길면 왜 세금이 줄어드나요?", "3년 이상 보유하면 장기보유특별공제(연 2%p, 최대 30%)가 적용되고, 2년 미만 단기 양도는 60~70%의 높은 세율이 붙습니다.")]
    write(path, layout(path, f"{label} 양도차익 {amt(g)} 양도소득세 — {won(r['total'])}원", f"{label} 주택을 양도차익 {amt(g)}에 팔면 양도소득세 {won(r['tax'])}원, 지방소득세 포함 {won(r['total'])}원(실효세율 {pct(r['eff'])}). 계산 과정 표.", body, faq,
          [("홈", "/"), ("양도소득세", "/capital-gains/"), (amt(g), "/capital-gains/%s/" % aslug(g)), (label, path)]), "0.5")

def hub_cg():
    rows = [['<a href="/capital-gains/%s/">%s</a>' % (aslug(g), amt(g)), won(cg(g, "lt1", 0)["total"]) + "원", won(cg(g, "lt2", 0)["total"]) + "원", won(cg(g, "basic", 3)["total"]) + "원", won(cg(g, "basic", 10)["total"]) + "원"] for g in GAINS]
    body = f"""
<div class="page-head"><h1>양도소득세 계산 — 양도차익별 보유 기간 세금표 (주택, 2026)</h1><p>1년 미만 70% · 2년 미만 60% · 기본세율 · 장기보유특별공제</p></div>
<p class="lead">주택을 팔 때 내는 <b>양도소득세</b>는 양도차익, 보유 기간, 1세대 1주택 여부에 따라 달라집니다. 보유 1년 미만은 70%, 1~2년은 60%, 2년 이상은 기본세율(6~45%)이며 3년 이상 보유하면 장기보유특별공제(최대 30%)가 적용됩니다. 양도차익을 눌러 보유 기간별 세금을 확인하세요(지방소득세 포함).</p>
{ad()}
{table(['양도차익', '1년 미만', '1~2년', '3년 보유', '10년 보유'], rows, (1, 2, 3, 4))}
<p class="note">{CG_NOTE}</p>
{chips([("1세대 1주택 양도세(12억 초과)", "/capital-gains/one-house/"), ("양도세 계산기", "/calculator/"), ("취득세", "/acquisition/")])}
"""
    faq = [("양도소득세는 어떻게 계산하나요?", "양도차익에서 장기보유특별공제와 기본공제 250만 원을 뺀 과세표준에 기본세율(6~45%)을 곱하고 지방소득세 10%를 더합니다."), ("1년 미만 보유하고 팔면 세율이 얼마인가요?", "주택은 70%, 1년 이상 2년 미만은 60%입니다(조정대상지역 다주택은 별도 중과)."),
           ("양도차익이란?", "양도가액에서 취득가액과 필요경비(취득세·중개수수료·자본적 지출 등)를 뺀 금액입니다.")]
    write("/capital-gains/", layout("/capital-gains/", "양도소득세 계산 — 양도차익별 보유 기간 세금표 (주택 2026)", "주택 양도소득세를 양도차익·보유 기간별로 정리. 1년 미만 70%, 2년 미만 60%, 기본세율과 장기보유특별공제, 지방소득세 포함.", body, faq, [("홈", "/"), ("양도소득세", "/capital-gains/")], coupang=True), "0.9")

# 1세대 1주택
OH_PRICES = [12 * EOK, 13 * EOK, 14 * EOK, 15 * EOK, 16 * EOK, 17 * EOK, 18 * EOK, 19 * EOK, 20 * EOK, 22 * EOK, 25 * EOK, 28 * EOK, 30 * EOK]
OH_GAINS = [2 * EOK, 3 * EOK, 5 * EOK, 7 * EOK, 10 * EOK]
OH_HOLD = [(3, 3), (5, 5), (10, 10), (10, 2)]
OH_NOTE = ("1세대 1주택(보유 2년 이상, 조정대상지역 취득은 거주 2년 요건 별도)이 양도가 12억 원을 넘으면 12억 초과분에 해당하는 양도차익에만 과세합니다. "
           "장기보유특별공제는 3년 이상 보유 시 보유 연 4%(최대 40%)와 거주 연 4%(최대 40%)를 합산해 최대 80%입니다. 기본공제 250만 원·지방소득세 10%를 반영했고 일시적 2주택·상생임대 등 특례는 반영하지 않았습니다.")

def page_oh(p):
    path = "/capital-gains/one-house/%s/" % aslug(p)
    if p == 12 * EOK:
        lead = f"<p class=\"lead\">1세대 1주택(보유 2년 이상) 양도가액이 <b>12억 원 이하면 양도소득세가 비과세</b>입니다. 12억 원 정확히 팔면 세금이 없고, 12억 원을 넘으면 초과분에 대해서만 과세합니다. 아래 가격별 표에서 12억 초과 시 세금을 확인하세요.</p>"
        rows = [[amt(v), "비과세" if v <= 12 * EOK else '<a href="/capital-gains/one-house/%s/">보기</a>' % aslug(v)] for v in OH_PRICES]
        t = table(["양도가액", "양도세"], rows)
    else:
        lead = (f"<p class=\"lead\">1세대 1주택을 <b>{amt(p)}</b>에 팔면 12억 원 초과분({amt(p - 12 * EOK)})에 해당하는 양도차익만 과세됩니다. 예를 들어 양도차익 5억 원에 10년 보유·10년 거주라면 약 <b>{won(T.capgain_onehouse(p, 5 * EOK, 10, 10)['total'])}원</b>, "
                f"보유 3년·거주 3년이면 약 {won(T.capgain_onehouse(p, 5 * EOK, 3, 3)['total'])}원입니다(지방소득세 포함). 보유·거주 기간이 길수록 장기보유특별공제(최대 80%)로 세금이 크게 줄어듭니다.</p>")
        rows = []
        for gn in OH_GAINS:
            if gn >= p: continue
            for h, l in OH_HOLD:
                r = T.capgain_onehouse(p, gn, h, l)
                rows.append([amt(gn), "보유 %d년·거주 %d년" % (h, l), won(r["tg"]) + "원", pct(r["ltd"] * 100, 0) if r["ltd"] else "-", won(r["taxable"]) + "원", pct(r["rate"] * 100, 0) if r["taxable"] else "-", "<b>%s원</b>" % won(r["total"])])
        t = table(["양도차익", "보유·거주", "과세 양도차익", "장특공제", "과세표준", "세율", "합계(지방세 포함)"], rows, (2, 3, 4, 5, 6))
    nb = ""
    body = f"""
<div class="page-head"><h1>1세대 1주택 {amt(p)} 양도세 — 12억 초과분 과세</h1><p>비과세 12억 · 보유·거주 장기보유특별공제 최대 80% · 지방소득세 포함</p></div>
{lead}
{ad()}
{t}
<p class="note">{OH_NOTE}</p>
{chips([("1세대 1주택 양도세 표", "/capital-gains/one-house/"), ("양도세 전체 표", "/capital-gains/"), ("양도세 계산기", "/calculator/")])}
"""
    faq = [("1세대 1주택 양도세 비과세 기준은?", "2년 이상 보유(조정대상지역은 거주 2년 포함)한 1세대 1주택을 양도가 12억 원 이하로 팔면 비과세입니다."), ("12억 원을 넘으면 전체에 과세되나요?", "아닙니다. 12억 초과분에 해당하는 양도차익만 과세하며 양도차익 × (양도가 − 12억) ÷ 양도가로 계산합니다."), ("장기보유특별공제는 얼마까지?", "보유 연 4%(최대 40%) + 거주 연 4%(최대 40%)로 최대 80%입니다.")]
    write(path, layout(path, f"1세대 1주택 {amt(p)} 양도세 — 12억 초과분 과세 계산" if p > 12 * EOK else "1세대 1주택 12억 양도세 — 비과세 기준", f"1세대 1주택을 {amt(p)}에 양도할 때 양도소득세. 12억 초과분 과세, 보유·거주 장기보유특별공제 최대 80%, 양도차익·기간별 세액표." if p > 12 * EOK else "1세대 1주택 양도가 12억 이하 비과세 기준과 12억 초과 시 양도세 계산.", body, faq,
          [("홈", "/"), ("양도소득세", "/capital-gains/"), ("1세대 1주택", "/capital-gains/one-house/"), (amt(p), path)], coupang=(p in (15 * EOK, 20 * EOK))), "0.7")

def hub_oh():
    rows = []
    for p in OH_PRICES:
        r = T.capgain_onehouse(p, 5 * EOK, 10, 10)
        rows.append(['<a href="/capital-gains/one-house/%s/">%s</a>' % (aslug(p), amt(p)), "비과세" if r["exempt"] else won(r["total"]) + "원", "비과세" if r["exempt"] else won(T.capgain_onehouse(p, 5 * EOK, 3, 3)["total"]) + "원"])
    body = f"""
<div class="page-head"><h1>1세대 1주택 양도세 — 12억 초과 시 세금표 (2026)</h1><p>양도차익 5억 가정 · 보유·거주 기간별</p></div>
<p class="lead">1세대 1주택자가 2년 이상 보유한 집을 팔 때 <b>양도가 12억 원 이하는 비과세</b>입니다. 12억을 넘으면 초과분의 양도차익에만 세금이 붙고, 보유·거주 기간이 길수록 장기보유특별공제(최대 80%)로 줄어듭니다. 양도가를 눌러 양도차익·기간별 세액을 확인하세요(아래 표는 양도차익 5억 원 가정).</p>
{ad()}
{table(['양도가액', '10년 보유·거주', '3년 보유·거주'], rows, (1, 2))}
<p class="note">{OH_NOTE}</p>
{chips([("양도세 전체 표", "/capital-gains/"), ("양도세 계산기", "/calculator/")])}
"""
    faq = [("1세대 1주택 비과세 12억은 세법 개정으로 바뀌나요?", "2021년 12월부터 12억 원 기준이 적용되고 있으며 개정되면 이 사이트의 계산 모듈에서 갱신합니다."), ("양도가 15억 아파트 양도세는?", f"양도차익 5억·10년 보유·거주 기준 약 {won(T.capgain_onehouse(15 * EOK, 5 * EOK, 10, 10)['total'])}원입니다(추정).")]
    write("/capital-gains/one-house/", layout("/capital-gains/one-house/", "1세대 1주택 양도세 — 12억 비과세·초과분 세금표 (2026)", "1세대 1주택 양도가 12억 이하 비과세, 12억 초과 시 양도세를 양도가·양도차익·보유거주 기간별로 계산한 표.", body, faq, [("홈", "/"), ("양도소득세", "/capital-gains/"), ("1세대 1주택", "/capital-gains/one-house/")], coupang=True), "0.9")

# ───────────────────────── 프리랜서 3.3% ─────────────────────────
FREE = [10 * MAN * 10, 15 * MAN * 100 // 10, 2 * CHEON, 25 * MAN * 100, 3 * CHEON, 4 * CHEON, 5 * CHEON, 6 * CHEON, 7 * CHEON, 8 * CHEON, EOK, 12 * CHEON, 15 * CHEON, 2 * EOK]
FREE = [1000 * MAN, 1500 * MAN, 2000 * MAN, 2500 * MAN, 3000 * MAN, 4000 * MAN, 5000 * MAN, 6000 * MAN, 7000 * MAN, 8000 * MAN, 10000 * MAN, 12000 * MAN, 15000 * MAN, 20000 * MAN]
EXPS = [0.3, 0.5, 0.7]
FREE_NOTE = ("프리랜서(사업소득)가 3.3%(소득세 3% + 지방소득세 0.3%)를 떼고 받은 뒤 5월 종합소득세 확정신고로 정산하는 상황의 추정입니다. 경비율(30%·50%·70%)은 가정이며 실제 단순경비율·기준경비율은 업종마다 다릅니다. "
             "본인 기본공제 150만 원과 표준세액공제 7만 원만 반영했고 국민연금·건강보험료 소득공제, 부양가족, 기장세액공제는 반영하지 않아 실제 환급액은 이보다 클 수 있습니다.")

def page_free(v):
    path = "/freelancer/%s/" % aslug(v)
    rs = {e: T.freelancer(v, e) for e in EXPS}
    r5 = rs[0.5]
    wh = r5["withheld"]
    def phr(r): return ("환급 약 %s원" % won(r["refund"])) if r["refund"] >= 0 else ("추가 납부 약 %s원" % won(-r["refund"]))
    lead = (f"<p class=\"lead\">연 수입 <b>{amt(v)}</b>의 프리랜서는 3.3%로 <b>{won(wh)}원</b>을 미리 냅니다(월 평균 {won(v / 12)}원 수입). 경비율을 30%로 보면 {phr(rs[0.3])}, 50%면 <b>{phr(rs[0.5])}</b>, 70%면 {phr(rs[0.7])}입니다. 국민연금·건강보험료 공제를 더 받으면 환급액은 커집니다.</p>")
    rows = []
    for e in EXPS:
        r = rs[e]
        rows.append([pct(e * 100, 0), won(r["bi"]) + "원", won(r["tb"]) + "원", won(r["total"]) + "원", won(r["withheld"]) + "원", ("<b>환급 %s원</b>" % won(r["refund"])) if r["refund"] >= 0 else ("<b>추가 %s원</b>" % won(-r["refund"]))])
    t = table(["경비율(가정)", "사업소득금액", "과세표준", "종합소득세(지방세 포함)", "이미 낸 3.3%", "정산 결과"], rows, (1, 2, 3, 4, 5))
    nb = table(["연 수입", "3.3% 원천징수", "경비율 50% 정산"], [['<a href="/freelancer/%s/">%s</a>' % (aslug(x), amt(x)) if x != v else "<b>%s</b>" % amt(x), won(T.freelancer(x, 0.5)["withheld"]) + "원", (("환급 %s원" % won(T.freelancer(x, 0.5)["refund"])) if T.freelancer(x, 0.5)["refund"] >= 0 else ("추가 %s원" % won(-T.freelancer(x, 0.5)["refund"])))] for x in near(FREE, v)], (1, 2))
    body = f"""
<div class="page-head"><h1>프리랜서 연 수입 {amt(v)} 3.3% 환급 — 경비율 50% 시 {phr(r5)}</h1><p>종합소득세 확정신고 정산 · 경비율 30·50·70% 가정</p></div>
{lead}
{ad()}
{t}
<h2 class="group-title">📈 비슷한 연 수입</h2>
{nb}
<h2 class="group-title">📌 알아두기</h2>
<ul class="lead" style="margin-left:20px"><li>{FREE_NOTE}</li><li>종합소득세 확정신고는 다음 해 5월 1~31일(성실신고확인 대상은 6월 30일)에 홈택스에서 합니다.</li><li>연 수입이 일정액 이하이고 단순경비율 대상이면 신고 절차가 간단해 3.3%의 대부분이 환급되는 경우가 많습니다.</li></ul>
{chips([("프리랜서 3.3% 전체 표", "/freelancer/"), ("종합소득세 세율표", "/income-tax/"), ("세금 계산기", "/calculator/")])}
"""
    faq = [(f"연 수입 {amt(v)} 프리랜서의 3.3% 환급은?", f"경비율 50% 가정 시 {phr(r5)}입니다(국민연금·건보료 공제 미반영). 경비율 30%는 {phr(rs[0.3])}, 70%는 {phr(rs[0.7])}입니다."),
           ("프리랜서 3.3%는 무엇인가요?", "사업소득세 3%와 지방소득세 0.3%를 합친 원천징수세율입니다. 5월 종합소득세 신고에서 실제 세금과 정산해 환급받거나 추가 납부합니다."),
           ("경비율은 어떻게 정해지나요?", "업종별로 국세청이 고시하는 단순경비율·기준경비율이 있으며 장부를 쓰면 실제 경비를 인정받습니다. 이 페이지는 30·50·70%를 가정해 비교합니다.")]
    write(path, layout(path, f"프리랜서 연 수입 {amt(v)} 3.3% 환급 — {phr(r5)} (경비율 50%)", f"프리랜서 연 수입 {amt(v)}의 3.3% 원천징수 {won(wh)}원과 종합소득세 정산. 경비율 30·50·70% 가정별 환급·추가 납부액.", body, faq, [("홈", "/"), ("프리랜서 세금", "/freelancer/"), (amt(v), path)], coupang=(v in (3000 * MAN, 5000 * MAN))), "0.7")

def hub_free():
    rows = []
    for x in FREE:
        r = T.freelancer(x, 0.5)
        rows.append(['<a href="/freelancer/%s/">%s</a>' % (aslug(x), amt(x)), won(r["withheld"]) + "원", ("환급 %s원" % won(r["refund"])) if r["refund"] >= 0 else ("추가 %s원" % won(-r["refund"]))])
    body = f"""
<div class="page-head"><h1>프리랜서 3.3% 환급 계산 — 연 수입별 종합소득세 정산표 (2026)</h1><p>경비율 50% 가정 · 연 수입 1천만~2억 원</p></div>
<p class="lead">프리랜서가 3.3%를 떼고 받은 뒤 5월 종합소득세 확정신고에서 정산하면 연 수입과 경비율에 따라 <b>환급</b>받거나 <b>추가 납부</b>합니다. 연 수입을 눌러 경비율 30·50·70% 가정별 결과를 확인하세요. 아래 표는 경비율 50% 가정입니다.</p>
{ad()}
{table(['연 수입', '3.3% 원천징수', '정산(경비율 50%)'], rows, (1, 2))}
<p class="note">{FREE_NOTE}</p>
{chips([("종합소득세 세율표", "/income-tax/"), ("세금 계산기", "/calculator/"), ("우아연봉 연말정산", "https://wooayeonbong.wooahouse.com/yearend/")])}
"""
    faq = [("3.3% 환급은 언제 받나요?", "다음 해 5월 종합소득세 확정신고를 마치면 6~7월에 환급금이 지급됩니다."), ("신고하지 않으면 어떻게 되나요?", "환급받을 수 있는 3.3%를 돌려받지 못하고 무신고 가산세가 붙을 수 있습니다(추가 납부 대상인 경우).")]
    write("/freelancer/", layout("/freelancer/", "프리랜서 3.3% 환급 계산 — 연 수입별 종합소득세 정산표 (2026)", "프리랜서 3.3% 원천징수 환급·추가 납부를 연 수입 1천만~2억 원별로 계산. 경비율 30·50·70% 가정 종합소득세 정산표.", body, faq, [("홈", "/"), ("프리랜서 세금", "/freelancer/")], coupang=True), "0.9")

# ───────────────────────── 종합소득세 ─────────────────────────
TBS = [500 * MAN, 1000 * MAN, 1400 * MAN, 2000 * MAN, 2500 * MAN, 3000 * MAN, 4000 * MAN, 5000 * MAN, 6000 * MAN, 7000 * MAN, 8000 * MAN, 8800 * MAN, 10000 * MAN, 12000 * MAN, 15000 * MAN, 20000 * MAN, 30000 * MAN, 50000 * MAN, 100000 * MAN]

def page_it(tb):
    path = "/income-tax/%s/" % aslug(tb)
    r = T.income_tax(tb)
    lead = (f"<p class=\"lead\">종합소득세 <b>과세표준 {amt(tb)}</b>이면 산출세액은 <b>{won(r['tax'])}원</b>, 지방소득세 {won(r['local'])}원을 더해 <b>{won(r['total'])}원</b>입니다(최고 세율 {int(round(r['rate'] * 100))}%, 실효세율 {pct(r['eff'])}). 세액공제·감면은 반영하지 않은 값입니다.</p>")
    rows = [["과세표준", won(tb) + "원"], ["적용 세율(한계)", "%d%%" % round(r["rate"] * 100)], ["산출세액", won(r["tax"]) + "원"], ["지방소득세(10%)", won(r["local"]) + "원"], ["<b>합계</b>", "<b>%s원</b>" % won(r["total"])], ["실효세율", pct(r["eff"])]]
    nb = table(["과세표준", "세율", "소득세+지방세", "실효세율"], [['<a href="/income-tax/%s/">%s</a>' % (aslug(x), amt(x)) if x != tb else "<b>%s</b>" % amt(x), "%d%%" % round(T.income_tax(x)["rate"] * 100), won(T.income_tax(x)["total"]) + "원", pct(T.income_tax(x)["eff"])] for x in near(TBS, tb)], (1, 2, 3))
    body = f"""
<div class="page-head"><h1>종합소득세 과세표준 {amt(tb)} — 세금 {won(r['total'])}원</h1><p>2026 소득세 기본세율 6~45% · 지방소득세 10% 포함</p></div>
{lead}
{ad()}
{table(['항목', '금액'], rows, (1,))}
<h2 class="group-title">📈 비슷한 과세표준</h2>
{nb}
<h2 class="group-title">📌 세율표</h2>
{table(['과세표준 구간', '세율', '누진공제'], [['1,400만 원 이하', '6%', '-'], ['5,000만 원 이하', '15%', '126만 원'], ['8,800만 원 이하', '24%', '576만 원'], ['1.5억 원 이하', '35%', '1,544만 원'], ['3억 원 이하', '38%', '1,994만 원'], ['5억 원 이하', '40%', '2,594만 원'], ['10억 원 이하', '42%', '3,594만 원'], ['10억 원 초과', '45%', '6,594만 원']], (1, 2))}
<p class="note">과세표준은 총수입에서 필요경비(또는 근로소득공제)와 각종 소득공제를 뺀 금액입니다. 자녀·연금계좌 등 세액공제와 감면은 이 표에 반영되지 않았습니다.</p>
{chips([("종합소득세 전체 표", "/income-tax/"), ("프리랜서 3.3% 정산", "/freelancer/"), ("세금 계산기", "/calculator/")])}
"""
    faq = [(f"과세표준 {amt(tb)}의 종합소득세는?", f"산출세액 {won(r['tax'])}원에 지방소득세를 더해 약 {won(r['total'])}원입니다(세액공제 전)."), ("과세표준이란?", "총수입에서 필요경비·공제를 뺀 세금 부과 기준 금액입니다."), ("지방소득세는 얼마인가요?", "소득세액의 10%입니다.")]
    write(path, layout(path, f"종합소득세 과세표준 {amt(tb)} — 세금 {won(r['total'])}원 (지방세 포함)", f"종합소득세 과세표준 {amt(tb)}의 소득세 {won(r['tax'])}원, 지방소득세 포함 {won(r['total'])}원. 2026 세율표와 실효세율.", body, faq, [("홈", "/"), ("종합소득세", "/income-tax/"), (amt(tb), path)]), "0.7")

def hub_it():
    rows = [['<a href="/income-tax/%s/">%s</a>' % (aslug(x), amt(x)), "%d%%" % round(T.income_tax(x)["rate"] * 100), won(T.income_tax(x)["total"]) + "원", pct(T.income_tax(x)["eff"])] for x in TBS]
    body = f"""
<div class="page-head"><h1>종합소득세 세율표 — 과세표준별 세금 계산 (2026)</h1><p>기본세율 6~45% · 지방소득세 포함</p></div>
<p class="lead">종합소득세는 <b>과세표준에 6~45%의 누진세율</b>을 적용합니다. 과세표준을 눌러 소득세와 지방소득세, 실효세율을 확인하세요. 사업·프리랜서·근로소득을 합산한 종합소득금액에서 소득공제를 뺀 금액이 과세표준입니다.</p>
{ad()}
{table(['과세표준', '세율', '소득세+지방세', '실효세율'], rows, (1, 2, 3))}
{chips([("프리랜서 3.3% 정산", "/freelancer/"), ("양도소득세", "/capital-gains/"), ("세금 계산기", "/calculator/")])}
"""
    faq = [("종합소득세율은 얼마인가요?", "과세표준 1,400만 원 이하 6%, 5천만 원 이하 15%, 8,800만 원 이하 24%, 1.5억 이하 35%, 3억 이하 38%, 5억 이하 40%, 10억 이하 42%, 10억 초과 45%입니다."), ("과세표준 5천만 원이면 세금은?", f"소득세 {won(T.income_tax(5000 * MAN)['tax'])}원, 지방소득세 포함 {won(T.income_tax(5000 * MAN)['total'])}원입니다.")]
    write("/income-tax/", layout("/income-tax/", "종합소득세 세율표 — 과세표준별 세금 계산 (2026)", "종합소득세 기본세율 6~45%와 과세표준별 소득세·지방소득세·실효세율 표. 5천만·1억 원 과세표준 세금.", body, faq, [("홈", "/"), ("종합소득세", "/income-tax/")], coupang=True), "0.9")

# ───────────────────────── 부가가치세 ─────────────────────────
VAT_AMTS = [1 * MAN, 3 * MAN, 5 * MAN, 10 * MAN, 20 * MAN, 30 * MAN, 50 * MAN, 100 * MAN, 200 * MAN, 300 * MAN, 500 * MAN, 1000 * MAN, 2000 * MAN, 3000 * MAN, 5000 * MAN, EOK, 2 * EOK]

def page_vat(a):
    path = "/vat/%s/" % mslug(a)
    s = T.vat_from_supply(a); t = T.vat_from_total(a)
    lead = (f"<p class=\"lead\"><b>공급가액 {amt(a)}</b>의 부가가치세(10%)는 <b>{won(s['vat'])}원</b>이고 합계 금액은 {won(s['total'])}원입니다. 반대로 부가세가 포함된 <b>합계 {amt(a)}</b>라면 공급가액은 <b>{won(t['supply'])}원</b>, 부가세는 {won(t['vat'])}원입니다.</p>")
    rows = [["공급가액 → 합계", won(a) + "원", won(s["vat"]) + "원", won(s["total"]) + "원"], ["합계 → 공급가액(역산)", won(t["supply"]) + "원", won(t["vat"]) + "원", won(a) + "원"]]
    tb = table(["계산", "공급가액", "부가세(10%)", "합계(VAT 포함)"], rows, (1, 2, 3))
    nb = table(["금액", "공급가액 기준 부가세", "합계 기준 공급가액"], [['<a href="/vat/%s/">%s</a>' % (mslug(x), amt(x)) if x != a else "<b>%s</b>" % amt(x), won(T.vat_from_supply(x)["vat"]) + "원", won(T.vat_from_total(x)["supply"]) + "원"] for x in near(VAT_AMTS, a)], (1, 2))
    body = f"""
<div class="page-head"><h1>부가세 계산 {amt(a)} — 공급가액 기준 {won(s['vat'])}원, 합계 기준 {won(t['vat'])}원</h1><p>부가가치세 10% · 공급가액↔합계 역산</p></div>
{lead}
{ad()}
{tb}
<h2 class="group-title">📈 비슷한 금액</h2>
{nb}
<h2 class="group-title">📌 알아두기</h2>
<ul class="lead" style="margin-left:20px"><li>일반과세자의 부가가치세율은 10%입니다. 합계 ÷ 1.1이 공급가액이고 합계 − 공급가액이 부가세입니다.</li><li>간이과세자(연 매출 1억 400만 원 미만)는 업종별 부가가치율(15~40%)을 곱한 낮은 세율로 납부하며 연 4,800만 원 미만은 납부가 면제됩니다.</li><li>일반과세자는 1월·7월(예정고지는 4월·10월)에 신고·납부합니다.</li></ul>
{chips([("부가세 전체 표", "/vat/"), ("종합소득세", "/income-tax/"), ("프리랜서 3.3%", "/freelancer/")])}
"""
    faq = [(f"{amt(a)}의 부가세는 얼마인가요?", f"공급가액이 {amt(a)}이면 부가세 {won(s['vat'])}원(합계 {won(s['total'])}원), 부가세 포함 {amt(a)}이면 공급가액 {won(t['supply'])}원·부가세 {won(t['vat'])}원입니다."), ("부가세 포함 금액에서 공급가액은 어떻게 구하나요?", "합계 금액을 1.1로 나누면 공급가액입니다."), ("간이과세자도 부가세 10%를 받나요?", "세금계산서 발행 여부에 따라 다르며 납부세액은 업종별 부가가치율을 적용해 계산합니다.")]
    write(path, layout(path, f"부가세 계산 {amt(a)} — 공급가액 기준 {won(s['vat'])}원 (10%)", f"{amt(a)}의 부가가치세 10% 계산. 공급가액 기준 부가세 {won(s['vat'])}원, 부가세 포함 {amt(a)}의 공급가액 {won(t['supply'])}원.", body, faq, [("홈", "/"), ("부가세", "/vat/"), (amt(a), path)]), "0.5")

def hub_vat():
    rows = [['<a href="/vat/%s/">%s</a>' % (mslug(x), amt(x)), won(T.vat_from_supply(x)["vat"]) + "원", won(T.vat_from_supply(x)["total"]) + "원", won(T.vat_from_total(x)["supply"]) + "원"] for x in VAT_AMTS]
    body = f"""
<div class="page-head"><h1>부가세 계산기 — 공급가액·합계 금액별 부가가치세 (10%)</h1><p>부가세 포함·별도 금액 역산</p></div>
<p class="lead">부가가치세는 공급가액의 <b>10%</b>입니다. 공급가액에 1.1을 곱하면 합계, 합계를 1.1로 나누면 공급가액입니다. 금액을 눌러 공급가액 기준과 합계 기준 부가세를 확인하세요.</p>
<div class="tool-box"><div class="tool-row"><div><label for="v-a">금액(원)</label><input id="v-a" type="number" value="1000000" style="width:170px"></div><div><label for="v-m">기준</label><select id="v-m"><option value="s">공급가액(부가세 별도)</option><option value="t">합계(부가세 포함)</option></select></div><button class="btn-p" id="v-go">계산</button></div><div class="tool-out" id="v-out">계산 결과가 여기에 표시됩니다.</div></div>
{ad()}
{table(['금액', '공급가액 기준 부가세', '합계(VAT 포함)', '합계 기준 공급가액'], rows, (1, 2, 3))}
{chips([("종합소득세", "/income-tax/"), ("프리랜서 3.3%", "/freelancer/")])}
<script src="/assets/js/calc.js"></script>
"""
    faq = [("부가세는 몇 %인가요?", "일반과세자 기준 10%입니다."), ("110만 원에서 부가세를 빼면?", f"공급가액 {won(T.vat_from_total(1_100_000)['supply'])}원, 부가세 {won(T.vat_from_total(1_100_000)['vat'])}원입니다.")]
    write("/vat/", layout("/vat/", "부가세 계산기 — 공급가액·합계 금액별 부가가치세 10%", "부가가치세 10% 계산기와 금액별 표. 공급가액에서 합계, 부가세 포함 금액에서 공급가액 역산.", body, faq, [("홈", "/"), ("부가세", "/vat/")], coupang=True), "0.9")

def calc_boxes():
    return """
<div class="tool-box"><h3 style="margin-top:0">🏷️ 양도소득세 (주택 일반 보유 기간)</h3>
<div class="tool-row"><div><label for="c-g">양도차익(원)</label><input id="c-g" type="number" value="300000000" style="width:170px"></div><div><label for="c-y">보유 기간</label><select id="c-y"><option value="lt1">1년 미만</option><option value="lt2">1~2년</option><option value="3">3년</option><option value="5">5년</option><option value="10" selected>10년</option><option value="15">15년 이상</option></select></div><button class="btn-p" id="c-go">계산</button></div><div class="tool-out" id="c-out">계산 결과가 여기에 표시됩니다.</div></div>
<div class="tool-box"><h3 style="margin-top:0">🧑‍💻 프리랜서 3.3% 정산</h3>
<div class="tool-row"><div><label for="f-i">연 수입(원)</label><input id="f-i" type="number" value="30000000" style="width:170px"></div><div><label for="f-e">경비율</label><select id="f-e"><option value="0.3">30%</option><option value="0.5" selected>50%</option><option value="0.7">70%</option></select></div><button class="btn-p" id="f-go">계산</button></div><div class="tool-out" id="f-out">계산 결과가 여기에 표시됩니다.</div></div>
<div class="tool-box"><h3 style="margin-top:0">🧾 종합소득세 (과세표준)</h3>
<div class="tool-row"><div><label for="t-b">과세표준(원)</label><input id="t-b" type="number" value="50000000" style="width:170px"></div><button class="btn-p" id="t-go">계산</button></div><div class="tool-out" id="t-out">계산 결과가 여기에 표시됩니다.</div></div>
"""

def all_pages():
    n0 = len(WRITTEN)
    for g in GAINS:
        page_cg(g)
        for sl, mode, yrs, label in HOLDS: page_cg_hold(g, sl, mode, yrs, label)
    hub_cg()
    for p in OH_PRICES: page_oh(p)
    hub_oh()
    for v in FREE: page_free(v)
    hub_free()
    for tb in TBS: page_it(tb)
    hub_it()
    for a in VAT_AMTS: page_vat(a)
    hub_vat()
    return len(WRITTEN) - n0
