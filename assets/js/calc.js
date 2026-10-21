/* 우아세금 계산기 — scripts/tax.py 와 같은 식 */
var YT = (function () {
  function f10(x) { return Math.floor(x / 10) * 10; }
  var BR = [[1e8, 0.10, 0], [5e8, 0.20, 1e7], [10e8, 0.30, 6e7], [30e8, 0.40, 1.6e8], [Infinity, 0.50, 4.6e8]];
  function prog(base) {
    if (base <= 0) return [0, 0, 0];
    for (var i = 0; i < BR.length; i++) if (base <= BR[i][0]) return [base * BR[i][1] - BR[i][2], BR[i][1], BR[i][2]];
  }
  function acqRate(price) { var p = price / 1e8; return p <= 6 ? 1.0 : p <= 9 ? p * 2 / 3 - 3 : 3.0; }
  function acquisition(price, over85) {
    var r = acqRate(price), tax = f10(price * r / 100), edu = f10(tax * 0.1), nong = over85 ? f10(price * 0.002) : 0;
    return { rate: r, tax: tax, edu: edu, nong: nong, total: tax + edu + nong };
  }
  var GIFT = { spouse: 6e8, adult_child: 5e7, adult_child_marry: 1.5e8, minor_child: 2e7, relative: 1e7, none: 0 };
  function gift(amount, rel) {
    var ded = GIFT[rel], base = Math.max(0, amount - ded), t = f10(prog(base)[0]);
    return { ded: ded, base: base, rate: prog(base)[1], tax: t, filed: f10(t * 0.97) };
  }
  function inherit(estate, spouse, kids) {
    var lump = Math.max(5e8, 2e8 + 5e7 * kids), ds = 0;
    if (spouse) { ds = Math.min(Math.max(estate * (1.5 / (1.5 + kids)), 5e8), 30e8); ds = Math.min(ds, estate); }
    var base = Math.max(0, estate - lump - ds), t = f10(prog(base)[0]);
    return { lump: lump, spouse: ds, base: base, rate: prog(base)[1], tax: t, filed: f10(t * 0.97) };
  }
  function prop(official, one) {
    var ratio = one ? (official <= 3e8 ? 0.43 : official <= 6e8 ? 0.44 : 0.45) : 0.60, base = official * ratio, special = one && official <= 9e8, pt;
    if (special) { pt = base <= 6e7 ? base * 0.0005 : base <= 1.5e8 ? 30000 + (base - 6e7) * 0.001 : base <= 3e8 ? 120000 + (base - 1.5e8) * 0.002 : 420000 + (base - 3e8) * 0.0035; }
    else { pt = base <= 6e7 ? base * 0.001 : base <= 1.5e8 ? 60000 + (base - 6e7) * 0.0015 : base <= 3e8 ? 195000 + (base - 1.5e8) * 0.0025 : 570000 + (base - 3e8) * 0.004; }
    pt = f10(pt); var urban = f10(base * 0.0014), edu = f10(pt * 0.2);
    return { ratio: ratio, base: base, special: special, pt: pt, urban: urban, edu: edu, total: pt + urban + edu };
  }
  return { acquisition: acquisition, gift: gift, inherit: inherit, prop: prop, acqRate: acqRate };
})();

(function () {
  if (typeof document === 'undefined' || !document.getElementById('a-go')) return;
  function w(x) { return Math.round(x).toLocaleString('ko-KR'); }
  document.getElementById('a-go').onclick = function () {
    var p = +document.getElementById('a-p').value, o = document.getElementById('a-o').value === '1', r = YT.acquisition(p, o);
    document.getElementById('a-out').innerHTML = '<b>취득세 등 합계 약 ' + w(r.total) + '원</b> (취득세율 ' + r.rate.toFixed(2) + '%)<br>취득세 ' + w(r.tax) + ' · 지방교육세 ' + w(r.edu) + ' · 농어촌특별세 ' + w(r.nong) + ' (원)';
  };
  document.getElementById('g-go').onclick = function () {
    var p = +document.getElementById('g-p').value, r = YT.gift(p, document.getElementById('g-r').value);
    document.getElementById('g-out').innerHTML = '<b>증여세 약 ' + w(r.filed) + '원</b> (기한 내 신고, 3% 공제 반영)<br>공제 ' + w(r.ded) + ' · 과세표준 ' + w(r.base) + ' · 세율 ' + (r.base ? Math.round(r.rate * 100) + '%' : '-') + ' · 산출세액 ' + w(r.tax) + ' (원)';
  };
  document.getElementById('i-go').onclick = function () {
    var p = +document.getElementById('i-p').value, r = YT.inherit(p, document.getElementById('i-s').value === '1', +document.getElementById('i-k').value);
    document.getElementById('i-out').innerHTML = '<b>상속세 약 ' + w(r.filed) + '원</b> (신고세액공제 3% 반영)<br>일괄공제 ' + w(r.lump) + ' · 배우자공제 ' + w(r.spouse) + ' · 과세표준 ' + w(r.base) + ' · 세율 ' + (r.base ? Math.round(r.rate * 100) + '%' : '-') + ' (원)';
  };
  document.getElementById('p-go').onclick = function () {
    var p = +document.getElementById('p-p').value, r = YT.prop(p, document.getElementById('p-h').value === '1');
    document.getElementById('p-out').innerHTML = '<b>연 재산세 약 ' + w(r.total) + '원</b> (7월·9월 각 ' + w(r.total / 2) + '원)<br>공정시장가액비율 ' + Math.round(r.ratio * 100) + '% · 재산세 ' + w(r.pt) + ' · 도시지역분 ' + w(r.urban) + ' · 지방교육세 ' + w(r.edu) + ' (원)' + (r.special ? '<br>1세대 1주택 특례세율 적용' : '');
  };
})();
if (typeof module !== 'undefined') module.exports = YT;
