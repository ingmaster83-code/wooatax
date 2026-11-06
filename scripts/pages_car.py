# -*- coding: utf-8 -*-
"""우아세금 확장 2: 자동차세(비영업용 승용자동차, 소유분) 배기량별·차령별 페이지. build_site.main() 에서 호출.
기준(지방세법 제127조·제151조, 서울시 세목별 안내로 확인): 배기량 1,000cc 이하 cc당 80원 / 1,600cc 이하 140원 / 1,600cc 초과 200원,
차령 3년차 5% 경감부터 매년 5%p씩 늘어 12년 이상 50% 경감, 지방교육세 자동차세액의 30%, 6월·12월 반기 납부.
(서울시 예시: 1,998cc 2016년식 → 2023년 차령 8년차 30% 경감 → 279,720원 = 계산식과 일치)
전기차·하이브리드 특례, 영업용·화물차, 연납 공제, 지자체별 감면은 반영하지 않는다(참고용 추정)."""
from common import *
import build_site as B

table, chips, near = B.table, B.chips, B.near

def k(x): return "{:,}".format(x)

CC_LIST = [800, 900, 998, 1000, 1100, 1200, 1300, 1400, 1500, 1591, 1598, 1600, 1700, 1800, 1900, 1950, 1991, 1999, 2000, 2100, 2199, 2200, 2359, 2400,
           2497, 2500, 2700, 2999, 3000, 3342, 3470, 3500, 3800, 4000, 4500, 5000, 6000]
HUB_CC = [998, 1000, 1200, 1400, 1598, 1600, 1800, 1999, 2000, 2199, 2497, 2999, 3000, 3470, 3500, 4000]
AGE_PAGES = list(range(3, 13))
EDU = 0.30

def floor10(x): return int(x // 10 * 10)
def unit(cc): return 80 if cc <= 1000 else (140 if cc <= 1600 else 200)
def reduction(age): return 0 if age < 3 else min(50, 5 * (age - 2))        # 차령(등록 연도를 1년차로 센 햇수)

def car_tax(cc, age=1):
    base = cc * unit(cc)
    tax = floor10(base * (100 - reduction(age)) / 100.0)
    edu = floor10(tax * EDU)
    return dict(base=base, tax=tax, edu=edu, total=tax + edu, half=(tax + edu) // 2, red=reduction(age), unit=unit(cc))

CAR_NOTE = ("비영업용 승용자동차(소유분) 기준입니다. 배기량 × cc당 세율(1,000cc 이하 80원·1,600cc 이하 140원·1,600cc 초과 200원)에 차령 경감(3년차 5%, 매년 5%p씩 늘어 12년 이상 50%)을 적용하고 지방교육세 30%를 더했으며 "
            "6월·12월 두 번에 나누어 냅니다. 전기차·하이브리드 등 정액·감면 대상, 영업용·화물·이륜차, 연납 공제와 지자체별 감면은 반영하지 않은 참고용 추정입니다. 차령은 최초 등록 연도를 1년차로 셉니다.")

AGE_LABELS = [("1~2년차", 1)] + [("%d년차" % a, a) for a in range(3, 12)] + [("12년 이상", 12)]

def page_cc(cc):
    path = "/car-tax/%d/" % cc
    n, o = car_tax(cc, 1), car_tax(cc, 12)
    rows = []
    for lab, a in AGE_LABELS:
        r = car_tax(cc, a)
        rows.append([lab, ("%d%%" % r["red"]) if r["red"] else "-", won(r["tax"]) + "원", won(r["edu"]) + "원", "<b>%s원</b>" % won(r["total"]), won(r["half"]) + "원"])
    t = table(["차령", "경감", "자동차세(연)", "지방교육세(30%)", "합계(연)", "6월·12월 각각"], rows, (1, 2, 3, 4, 5))
    ccs = near(CC_LIST, cc, 4)
    nt = table(["배기량", "cc당 세율", "자동차세(연)", "지방교육세 포함 합계", "12년 이상 합계"], [[('<a href="/car-tax/%d/">%scc</a>' % (v, k(v))) if v != cc else "<b>%scc</b>" % k(v), "%d원" % unit(v), won(car_tax(v, 1)["tax"]) + "원", won(car_tax(v, 1)["total"]) + "원", won(car_tax(v, 12)["total"]) + "원"] for v in ccs], (1, 2, 3, 4))
    lead = (f"<p class=\"lead\"><b>배기량 {k(cc)}cc</b> 승용차(비영업용)의 자동차세는 신차 기준 연 <b>{won(n['tax'])}원</b>이고 지방교육세 30% {won(n['edu'])}원을 더하면 연 <b>{won(n['total'])}원</b>입니다. "
            f"6월과 12월에 각각 {won(n['half'])}원씩 냅니다. 차령이 3년을 넘으면 해마다 5%p씩 깎여 12년 이상이면 50% 경감된 연 {won(o['total'])}원이 됩니다(cc당 세율 {n['unit']}원).</p>")
    body = f"""
<div class="page-head"><h1>{k(cc)}cc 자동차세 — 연 {won(n['total'])}원 (지방교육세 포함, 2026)</h1><p>배기량 {k(cc)}cc 승용차 · 차령별 경감 · 6월·12월 납부액</p></div>
{lead}
<div class="stat-row"><div class="stat"><small>자동차세(연)</small><b>{won(n['tax'])}원</b></div><div class="stat"><small>지방교육세 포함(연)</small><b>{won(n['total'])}원</b></div><div class="stat"><small>6월·12월 각각</small><b>{won(n['half'])}원</b></div></div>
{ad()}
<h2 class="group-title">📅 차령별 자동차세 ({k(cc)}cc)</h2>
{t}
<p class="note">{CAR_NOTE}</p>
<h2 class="group-title">📈 비슷한 배기량의 자동차세</h2>
{nt}
{chips([("자동차세 계산 표", "/car-tax/"), ("차령 8년 자동차세", "/car-tax/age/8/"), ("취득세 계산", "/acquisition/"), ("재산세 계산", "/property-tax/")])}
<div class="note-box">계산식: 자동차세 = 배기량 × cc당 세율 × (100 − 차령 경감률)%, 지방교육세 = 자동차세 × 30%. 10원 미만은 버렸습니다. 실제 고지 세액은 위택스·지자체 안내를 확인하세요.</div>
"""
    faq = [(f"{k(cc)}cc 자동차세는 얼마인가요?", f"차령 경감이 없는 신차 기준 연 {won(n['tax'])}원, 지방교육세 포함 연 {won(n['total'])}원입니다(6월·12월 각 {won(n['half'])}원)."),
           ("차가 오래되면 자동차세가 줄어드나요?", f"네. 차령 3년차부터 매년 5%p씩 경감되어 12년 이상이면 50%입니다. {k(cc)}cc는 12년 이상일 때 연 {won(o['total'])}원입니다."),
           ("지방교육세는 얼마나 붙나요?", "비영업용 승용자동차는 자동차세액의 30%가 지방교육세로 함께 부과됩니다.")]
    write(path, layout(path, f"{k(cc)}cc 자동차세 — 연 {won(n['total'])}원, 6월·12월 각 {won(n['half'])}원 (2026)",
        f"배기량 {k(cc)}cc 승용차의 자동차세. 신차 연 {won(n['tax'])}원(지방교육세 포함 {won(n['total'])}원), 차령 12년 이상 {won(o['total'])}원. 차령별 경감 표.",
        body, faq, [("홈", "/"), ("자동차세", "/car-tax/"), ("%scc" % k(cc), path)]), "0.6")

def page_age(age):
    path = "/car-tax/age/%d/" % age
    red = reduction(age)
    ccs = [998, 1000, 1200, 1400, 1598, 1600, 1800, 1999, 2000, 2199, 2497, 2999, 3000, 3470, 3500, 4000]
    rows = [['<a href="/car-tax/%d/">%scc</a>' % (cc, k(cc)), won(car_tax(cc, 1)["total"]) + "원", won(car_tax(cc, age)["tax"]) + "원", won(car_tax(cc, age)["edu"]) + "원", "<b>%s원</b>" % won(car_tax(cc, age)["total"]), won(car_tax(cc, age)["half"]) + "원"] for cc in ccs]
    c2 = car_tax(2000, age)
    body = f"""
<div class="page-head"><h1>차령 {age}년 자동차세 — {red}% 경감, 배기량별 (2026)</h1><p>차령 {age}년차 승용차 · 경감 후 자동차세와 지방교육세</p></div>
<p class="lead"><b>차령 {age}년차</b> 승용차는 자동차세가 <b>{red}% 경감</b>됩니다. 2,000cc라면 경감 전 연 {won(car_tax(2000, 1)['total'])}원(지방교육세 포함)에서 <b>{won(c2['total'])}원</b>으로 줄고 6월·12월에 각각 {won(c2['half'])}원을 냅니다. 차령은 최초 등록 연도를 1년차로 세며 3년차부터 5%, 이후 해마다 5%p씩 늘어 12년 이상은 50%입니다.</p>
{ad()}
{table(['배기량', '경감 전 합계(연)', '자동차세(연)', '지방교육세(30%)', '합계(연)', '6월·12월 각각'], rows, (1, 2, 3, 4, 5))}
<p class="note">{CAR_NOTE}</p>
{chips([("차령 %d년" % a, "/car-tax/age/%d/" % a) for a in AGE_PAGES if a != age] + [("자동차세 계산 표", "/car-tax/")])}
"""
    faq = [(f"차령 {age}년이면 자동차세가 얼마나 줄어드나요?", f"{red}% 경감됩니다. 2,000cc 기준 지방교육세 포함 연 {won(car_tax(2000, 1)['total'])}원에서 {won(c2['total'])}원이 됩니다."),
           ("차령은 어떻게 세나요?", "최초 등록한 해를 1년차로 셉니다. 3년차부터 5%, 이후 해마다 5%p씩 늘어 12년 이상이면 50%가 경감됩니다.")]
    write(path, layout(path, f"차령 {age}년 자동차세 — {red}% 경감, 2000cc 연 {won(c2['total'])}원 (2026)",
        f"차령 {age}년차 승용차 자동차세 {red}% 경감. 2,000cc 연 {won(c2['total'])}원(지방교육세 포함)을 비롯한 배기량별 금액표.", body, faq,
        [("홈", "/"), ("자동차세", "/car-tax/"), ("차령 %d년" % age, path)]), "0.5")

def page_hub():
    rows = [['<a href="/car-tax/%d/">%scc</a>' % (cc, k(cc)), "%d원" % unit(cc), won(car_tax(cc, 1)["tax"]) + "원", won(car_tax(cc, 1)["total"]) + "원", won(car_tax(cc, 1)["half"]) + "원", won(car_tax(cc, 12)["total"]) + "원"] for cc in HUB_CC]
    cut = table(["차령", "경감률"], [[lab, ("%d%%" % reduction(a)) if reduction(a) else "-"] for lab, a in AGE_LABELS], (1,))
    body = f"""
<div class="page-head"><h1>자동차세 계산 — 배기량·차령별 표 (2026)</h1><p>비영업용 승용차 · cc당 80·140·200원 · 지방교육세 30% · 6월·12월 납부</p></div>
<p class="lead"><b>자동차세</b>는 배기량에 cc당 세율을 곱해 정합니다. 1,000cc 이하는 cc당 80원, 1,600cc 이하는 140원, 1,600cc를 넘으면 200원이고 지방교육세 30%가 더해집니다. 2,000cc 신차는 연 {won(car_tax(2000)['tax'])}원(교육세 포함 {won(car_tax(2000)['total'])}원), 1,598cc(아반떼급)는 연 {won(car_tax(1598)['total'])}원입니다. 차령이 오래되면 3년차 5%부터 최대 50%까지 경감됩니다.</p>
{ad()}
{table(['배기량', 'cc당 세율', '자동차세(연)', '교육세 포함(연)', '6월·12월 각각', '12년 이상 합계'], rows, (1, 2, 3, 4, 5))}
<h2 class="group-title">📆 차령별 경감률</h2>
{cut}
<p class="note">{CAR_NOTE}</p>
{chips([("차령 %d년" % a, "/car-tax/age/%d/" % a) for a in AGE_PAGES] + [("취득세", "/acquisition/"), ("재산세", "/property-tax/")])}
"""
    faq = [("자동차세는 어떻게 계산하나요?", "배기량 × cc당 세율(1,000cc 이하 80원, 1,600cc 이하 140원, 초과 200원)에 차령 경감을 적용하고 지방교육세 30%를 더합니다."), ("2000cc 자동차세는 얼마인가요?", f"신차 기준 연 {won(car_tax(2000)['tax'])}원, 지방교육세 포함 연 {won(car_tax(2000)['total'])}원이며 6월·12월에 각 {won(car_tax(2000)['half'])}원씩 냅니다."),
           ("자동차세는 언제 내나요?", "6월과 12월 두 번 나누어 내며 연납을 신청하면 세액 일부를 공제받을 수 있습니다(공제율은 위택스에서 확인).")]
    write("/car-tax/", layout("/car-tax/", "자동차세 계산 — 배기량·차령별 표 (2026)", "배기량별 자동차세 표. 2000cc 연 52만원, 1600cc 연 29만원 등 지방교육세 포함 금액과 차령 3~12년 경감 계산.", body, faq,
        [("홈", "/"), ("자동차세", "/car-tax/")], coupang=True), "0.9")

def all_pages():
    n0 = len(WRITTEN)
    for cc in CC_LIST: page_cc(cc)
    for a in AGE_PAGES: page_age(a)
    page_hub()
    return len(WRITTEN) - n0
