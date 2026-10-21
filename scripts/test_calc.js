const fs = require('fs'), path = require('path');
const YT = require(path.join(__dirname, '..', 'assets', 'js', 'calc.js'));
const out = [];
for (const p of [8e7, 3e8, 5e8, 6e8, 6.5e8, 7.4e8, 9e8, 1.2e9, 2.5e9, 5e9]) {
  for (const o of [false, true]) { const r = YT.acquisition(p, o); out.push(['acq', p, o ? 1 : 0, r.total]); }
  for (const rel of ['spouse', 'adult_child', 'adult_child_marry', 'minor_child', 'relative', 'none']) out.push(['gift', p, rel, YT.gift(p, rel).filed]);
  for (const sp of [false, true]) for (const k of [1, 2, 3]) out.push(['inh', p, (sp ? 1 : 0) * 10 + k, YT.inherit(p, sp, k).filed]);
  for (const one of [false, true]) out.push(['prop', p, one ? 1 : 0, YT.prop(p, one).total]);
}
fs.writeFileSync(path.join(__dirname, '_calc_js.json'), JSON.stringify(out));
console.log('cases', out.length);
