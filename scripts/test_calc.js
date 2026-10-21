const fs = require('fs'), path = require('path');
const YT = require(path.join(__dirname, '..', 'assets', 'js', 'calc.js'));
const out = [];
for (const p of [8e7, 3e8, 5e8, 6e8, 6.5e8, 7.4e8, 9e8, 1.2e9, 2.5e9, 5e9]) {
  for (const o of [false, true]) { const r = YT.acquisition(p, o); out.push(['acq', p, o ? 1 : 0, r.total]); }
  for (const rel of ['spouse', 'adult_child', 'adult_child_marry', 'minor_child', 'relative', 'none']) out.push(['gift', p, rel, YT.gift(p, rel).filed]);
  for (const sp of [false, true]) for (const k of [1, 2, 3]) out.push(['inh', p, (sp ? 1 : 0) * 10 + k, YT.inherit(p, sp, k).filed]);
  for (const one of [false, true]) out.push(['prop', p, one ? 1 : 0, YT.prop(p, one).total]);
}
for (const g of [3e6, 2e7, 5e7, 1e8, 3e8, 7e8, 1.5e9]) {
  for (const m of ['lt1', 'lt2']) out.push(['cg', g, m, YT.capgainGeneral(g, m, 0).total]);
  for (const y of [2, 3, 5, 10, 15, 20]) out.push(['cg', g, 'b' + y, YT.capgainGeneral(g, 'basic', y).total]);
  for (const pr of [1e9, 1.3e9, 2e9, 3e9]) for (const [h, l] of [[2, 2], [3, 3], [5, 5], [10, 10], [10, 2]]) out.push(['one', g, pr + ':' + h + ':' + l, YT.capgainOne(pr, g, h, l).total]);
  for (const e of [0.3, 0.5, 0.7]) out.push(['fl', g, e, YT.freelancer(g * 5, e).refund]);
  out.push(['it', g, 0, YT.incomeTax(g).total]);
  out.push(['vs', g, 0, YT.vatSupply(g).total]); out.push(['vt', g, 0, YT.vatTotal(g).supply]);
}
fs.writeFileSync(path.join(__dirname, '_calc_js.json'), JSON.stringify(out));
console.log('cases', out.length);
