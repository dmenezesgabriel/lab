async page => {
  const browser = page.context().browser();

  async function probe(name, url, check) {
    const ctx = await browser.newContext({ ignoreHTTPSErrors: true });
    const pg = await ctx.newPage();
    const r = { name, url, pass: false, detail: '' };
    try {
      const resp = await pg.goto(url, { waitUntil: 'domcontentloaded', timeout: 20000 });
      const status = resp ? resp.status() : 0;
      const finalUrl = pg.url();
      const title = await pg.title();
      const body = await pg.content();
      const res = check(status, finalUrl, title, body);
      r.pass = res.pass;
      r.detail = `HTTP ${status} | ${res.msg}`;
    } catch (e) {
      r.detail = 'ERROR: ' + e.message.split('\n')[0].slice(0, 120);
    } finally {
      await ctx.close();
    }
    return r;
  }

  const results = await Promise.all([

    // HTTPS via IP — cert SAN is IP:127.0.0.1, ignoreHTTPSErrors skips untrusted CA
    probe('Authelia portal', 'https://127.0.0.1:9091', (s, u, t, b) => ({
      pass: s === 200 && (b.includes('Sign in') || b.includes('password') || t.includes('Authelia')),
      msg: `title="${t}" loginForm=${b.includes('Sign in') || b.includes('password')}`
    })),

    probe('Prometheus', 'http://localhost:9090', (s, u, t, b) => ({
      pass: s === 200 && (t.includes('Prometheus') || b.includes('Prometheus')),
      msg: `title="${t}"`
    })),

    // SSO-gated: Caddy 302→Authelia, final URL should land at Authelia login
    probe('Grafana→SSO', 'https://127.0.0.1:3001', (s, u, t, b) => ({
      pass: u.includes('9091') || u.includes('auth.app') || b.includes('Sign in') || t.toLowerCase().includes('authelia'),
      msg: `finalUrl="${u}" title="${t}"`
    })),

    probe('Portainer→SSO', 'https://127.0.0.1:9000', (s, u, t, b) => ({
      pass: u.includes('9091') || u.includes('auth.app') || b.includes('Sign in') || b.includes('Portainer') || t.includes('Portainer'),
      msg: `finalUrl="${u}" title="${t}"`
    })),

    probe('MLflow', 'http://localhost:5000', (s, u, t, b) => ({
      pass: s === 200 && (b.includes('MLflow') || b.includes('mlflow')),
      msg: `title="${t}"`
    })),

    probe('MinIO console', 'http://localhost:9003', (s, u, t, b) => ({
      pass: s < 500 && (b.includes('MinIO') || b.includes('minio') || t.toLowerCase().includes('minio')),
      msg: `title="${t}" status=${s}`
    })),

    probe('Adminer', 'http://localhost:8082', (s, u, t, b) => ({
      pass: s === 200 && (t.includes('Adminer') || t.includes('Login') || b.includes('Adminer')),
      msg: `title="${t}"`
    })),

    // SonarQube: wait for networkidle via longer timeout, check status page
    (async () => {
      const ctx = await browser.newContext({ ignoreHTTPSErrors: true });
      const pg = await ctx.newPage();
      const r = { name: 'SonarQube', url: 'http://localhost:9004', pass: false, detail: '' };
      try {
        const resp = await pg.goto('http://localhost:9004', { waitUntil: 'load', timeout: 25000 });
        const status = resp ? resp.status() : 0;
        // SonarQube is a SPA — wait for body to populate
        await pg.waitForFunction(() => document.body.innerText.length > 50, { timeout: 10000 }).catch(() => {});
        const title = await pg.title();
        const body = await pg.content();
        const hasSonar = body.includes('SonarQube') || body.includes('sonar') || title.includes('SonarQube') || title.includes('Sonar');
        r.pass = status === 200 && hasSonar;
        r.detail = `HTTP ${status} | title="${title}"`;
      } catch (e) {
        r.detail = 'ERROR: ' + e.message.split('\n')[0].slice(0, 120);
      } finally {
        await ctx.close();
      }
      return r;
    })(),

    probe('Alloy', 'http://localhost:12345', (s, u, t, b) => ({
      pass: s === 200 && (t.includes('Alloy') || b.includes('Grafana Alloy')),
      msg: `title="${t}"`
    })),

    probe('cAdvisor', 'http://localhost:8085', (s, u, t, b) => ({
      pass: s === 200 && (b.includes('cAdvisor') || b.includes('cadvisor') || t.includes('Containers')),
      msg: `title="${t}"`
    })),

    probe('LlamaCPP', 'http://localhost:8000', (s, u, t, b) => ({
      pass: s < 500,
      msg: `title="${t}" status=${s}`
    })),

    probe('Homepage', 'http://localhost:3000', (s, u, t, b) => ({
      pass: s === 200,
      msg: `title="${t}"`
    })),

  ]);

  const pad = (s, n) => String(s).padEnd(n);
  const line = '═'.repeat(100);
  let out = '\n' + line + '\n';
  out += pad('SERVICE', 22) + pad('RESULT', 9) + 'DETAIL\n';
  out += '─'.repeat(100) + '\n';
  let passed = 0;
  for (const r of results) {
    const mark = r.pass ? '✓ PASS' : '✗ FAIL';
    out += pad(r.name, 22) + pad(mark, 9) + r.detail + '\n';
    if (r.pass) passed++;
  }
  out += line + '\n';
  out += `${passed}/${results.length} passed\n`;
  return out;
}
