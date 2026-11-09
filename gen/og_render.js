const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await p.goto('file://' + __dirname + '/og_template.html'); await p.waitForTimeout(500);
  await p.screenshot({ path: __dirname + '/../assets/img/og.png' }); await b.close();
})();
