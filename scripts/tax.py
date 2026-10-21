# -*- coding: utf-8 -*-
"""우아세금 계산 모듈 (현행 세법 일반 규정, 2026-10 기준 참고용 추정).
 - 취득세: 주택 유상취득 1주택 세율(6억 이하 1%, 6~9억 누진, 9억 초과 3%) + 지방교육세(취득세율×10%) + 농어촌특별세(전용 85㎡ 초과 0.2%). 다주택·법인 중과·감면 제외.
 - 증여세: 증여재산공제(배우자 6억·성년 자녀 5천만·미성년 자녀 2천만·기타친족 1천만, 혼인·출산 1억) + 5단계 누진세율, 자진신고 세액공제 3%.
 - 상속세: 일괄공제 5억 vs (기초 2억+자녀 5천/인) 중 큰 값, 배우자공제(법정상속분, 최소 5억~최대 30억), 5단계 누진세율, 신고세액공제 3%. 금융재산·동거주택 등 공제 제외.
 - 재산세: 주택, 공정시장가액비율(일반 60%, 1세대1주택 43~45%) + 표준세율·1세대1주택 특례세율(공시가 9억 이하) + 도시지역분 0.14% + 지방교육세 20%.
세법은 개정될 수 있으므로 상수는 이 파일 한 곳에서만 관리한다."""
import math

def f10(x): return int(x // 10 * 10)

# ── 취득세 ──
def acq_rate_pct(price):
    p = price / 1e8
    if p <= 6: return 1.0
    if p <= 9: return p * 2 / 3 - 3
    return 3.0

def acquisition(price, over85):
    r = acq_rate_pct(price)
    tax = f10(price * r / 100)
    edu = f10(tax * 0.1)
    nong = f10(price * 0.002) if over85 else 0
    return dict(rate=r, tax=tax, edu=edu, nong=nong, total=tax + edu + nong, eff=(tax + edu + nong) / price * 100 if price else 0)

# ── 누진세율(증여·상속 공통) ──
BR = [(1e8, 0.10, 0), (5e8, 0.20, 1e7), (10e8, 0.30, 6e7), (30e8, 0.40, 1.6e8), (math.inf, 0.50, 4.6e8)]

def prog_tax(base):
    if base <= 0: return 0.0, 0.0, 0
    for lim, r, d in BR:
        if base <= lim: return base * r - d, r, d

# ── 증여세 ──
GIFT_REL = {
    "spouse": ("배우자", 600_000_000),
    "adult_child": ("성년 자녀(부모→자녀)", 50_000_000),
    "adult_child_marry": ("성년 자녀 + 혼인·출산 공제", 150_000_000),
    "minor_child": ("미성년 자녀", 20_000_000),
    "relative": ("기타 친족(형제·조부모 등)", 10_000_000),
    "none": ("공제 없음(타인 등)", 0),
}

def gift_tax(amount, rel):
    ded = GIFT_REL[rel][1]
    base = max(0, amount - ded)
    t, r, d = prog_tax(base)
    t = f10(t)
    after = f10(t * 0.97)          # 자진신고 세액공제 3%
    return dict(ded=ded, base=base, rate=r, tax=t, tax_filed=after, eff=(after / amount * 100) if amount else 0)

# ── 상속세 ──
def inherit_tax(estate, spouse, kids):
    lump = 500_000_000
    basic = 200_000_000 + 50_000_000 * kids
    d_lump = max(lump, basic)
    d_spouse = 0
    if spouse:
        ratio = 1.5 / (1.5 + kids)
        d_spouse = min(max(estate * ratio, 500_000_000), 3_000_000_000)
        d_spouse = min(d_spouse, estate)
    base = max(0, estate - d_lump - d_spouse)
    t, r, d = prog_tax(base)
    t = f10(t)
    after = f10(t * 0.97)
    return dict(d_lump=d_lump, d_spouse=d_spouse, base=base, rate=r, tax=t, tax_filed=after, eff=(after / estate * 100) if estate else 0)

# ── 재산세(주택) ──
def prop_tax(official, one_house):
    if one_house:
        ratio = 0.43 if official <= 3e8 else 0.44 if official <= 6e8 else 0.45
    else:
        ratio = 0.60
    base = official * ratio
    special = one_house and official <= 9e8
    if special:
        if base <= 6e7: pt = base * 0.0005
        elif base <= 1.5e8: pt = 30_000 + (base - 6e7) * 0.001
        elif base <= 3e8: pt = 120_000 + (base - 1.5e8) * 0.002
        else: pt = 420_000 + (base - 3e8) * 0.0035
    else:
        if base <= 6e7: pt = base * 0.001
        elif base <= 1.5e8: pt = 60_000 + (base - 6e7) * 0.0015
        elif base <= 3e8: pt = 195_000 + (base - 1.5e8) * 0.0025
        else: pt = 570_000 + (base - 3e8) * 0.004
    pt = f10(pt)
    urban = f10(base * 0.0014)
    edu = f10(pt * 0.2)
    total = pt + urban + edu
    return dict(ratio=ratio, base=base, special=special, pt=pt, urban=urban, edu=edu, total=total, eff=(total / official * 100) if official else 0)

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(acquisition(800_000_000, True))
    print(acquisition(500_000_000, False))
    print(gift_tax(300_000_000, "adult_child"), gift_tax(1_000_000_000, "spouse"))
    print(inherit_tax(1_000_000_000, False, 2), inherit_tax(2_000_000_000, True, 2))
    print(prop_tax(500_000_000, True), prop_tax(1_200_000_000, False))
