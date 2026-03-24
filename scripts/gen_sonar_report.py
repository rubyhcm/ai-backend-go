#!/usr/bin/env python3
"""
SonarCloud Report Generator
Usage: python3 ~/.claude/scripts/gen_sonar_report.py
       Reads SONAR_TOKEN and SONAR_PROJECT_KEY from env or .env.local
       Writes report to reports/<timestamp>_sonarcloud_report.md
"""

import json, datetime, os, urllib.request, urllib.parse, base64, sys

# ── Config ────────────────────────────────────────────────────────────────────

def load_env_local():
    for path in [".env.local", ".env"]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, _, v = line.partition("=")
                        os.environ.setdefault(k.strip(), v.strip())

load_env_local()

token   = os.environ.get("SONAR_TOKEN", "")
project = os.environ.get("SONAR_PROJECT_KEY", "")
host    = os.environ.get("SONAR_HOST_URL", "https://sonarcloud.io")

# fallback: read sonar-project.properties
if not project and os.path.exists("sonar-project.properties"):
    with open("sonar-project.properties") as f:
        for line in f:
            line = line.strip()
            if line.startswith("sonar.projectKey="):
                project = line.split("=", 1)[1].strip()
            if line.startswith("sonar.host.url="):
                host = line.split("=", 1)[1].strip()

if not token:
    print("ERROR: SONAR_TOKEN not set. Add it to .env.local or export SONAR_TOKEN=...")
    sys.exit(1)
if not project:
    print("ERROR: SONAR_PROJECT_KEY not set. Add to .env.local or sonar-project.properties")
    sys.exit(1)

base = f"{host}/api"
auth = base64.b64encode(f"{token}:".encode()).decode()
headers = {"Authorization": f"Basic {auth}"}

# ── API helpers ───────────────────────────────────────────────────────────────

def get(path, params={}):
    url = f"{base}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} on {path}: {e.read().decode()}")
        sys.exit(1)

def fetch_all_issues(extra_params={}):
    issues, page = [], 1
    while True:
        params = {"componentKeys": project, "ps": 500, "p": page, **extra_params}
        d = get("issues/search", params)
        issues += d["issues"]
        if len(issues) >= d["total"] or page * 500 >= 10000:
            break
        page += 1
    return issues

def fetch_all_hotspots():
    hs, page = [], 1
    while True:
        d = get("hotspots/search", {"projectKey": project, "ps": 500, "p": page})
        hs += d["hotspots"]
        if len(hs) >= d["paging"]["total"]:
            break
        page += 1
    return hs

# ── Fetch data ────────────────────────────────────────────────────────────────

print(f"[sonar-report] Fetching data from {host} (project: {project})...")

m = get("measures/component", {
    "component": project,
    "metricKeys": "bugs,vulnerabilities,code_smells,security_hotspots,coverage,duplicated_lines_density,ncloc,reliability_rating,security_rating,sqale_index"
})
measures = {x["metric"]: x["value"] for x in m["component"]["measures"]}

vulns    = fetch_all_issues({"types": "VULNERABILITY"})
smells   = fetch_all_issues({"types": "CODE_SMELL"})
bugs     = fetch_all_issues({"types": "BUG"})
hotspots = fetch_all_hotspots()

print(f"[sonar-report] Fetched: {len(vulns)} vulnerabilities, {len(smells)} code smells, {len(bugs)} bugs, {len(hotspots)} hotspots")

# ── Helpers ───────────────────────────────────────────────────────────────────

def clean(key):
    return key.replace(f"{project}:", "")

def sev_icon(s):
    return {"BLOCKER": "🔴", "CRITICAL": "🟠", "MAJOR": "🟡", "MINOR": "🔵", "INFO": "⚪"}.get(s, "")

def risk_icon(r):
    return {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🔵"}.get(r, "")

def count_by(items, key="severity"):
    c = {}
    for i in items:
        v = i.get(key, "")
        c[v] = c.get(v, 0) + 1
    return c

rating_map = {"1.0": "A ✅", "2.0": "B ⚠️", "3.0": "C ⚠️", "4.0": "D ❌", "5.0": "E ❌"}

sqale_min = int(measures.get("sqale_index", "0"))
debt_h, debt_m = divmod(sqale_min, 60)
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ── Build report ──────────────────────────────────────────────────────────────

L = []

L += [
    "# SonarCloud Security Report",
    "",
    f"**Project:** `{project}`",
    f"**Scan Date:** {now}",
    f"**Dashboard:** {host}/dashboard?id={project}",
    "",
    "---",
    "",
    "## Summary",
    "",
    "| Metric | Value | Status |",
    "|--------|-------|--------|",
    f"| Lines of Code | {int(measures['ncloc']):,} | — |",
    f"| Coverage | {measures['coverage']}% | {'✅' if float(measures['coverage']) >= 80 else '❌'} (required ≥ 80%) |",
    f"| Duplicated Lines | {measures['duplicated_lines_density']}% | {'✅' if float(measures['duplicated_lines_density']) < 3 else '⚠️'} |",
    f"| Bugs | {measures['bugs']} | {'✅' if measures['bugs'] == '0' else '❌'} |",
    f"| Vulnerabilities | {measures['vulnerabilities']} | {'✅' if measures['vulnerabilities'] == '0' else '❌'} |",
    f"| Security Hotspots | {measures['security_hotspots']} | {'✅' if measures['security_hotspots'] == '0' else '⚠️'} |",
    f"| Code Smells | {measures['code_smells']} | ⚠️ |",
    f"| Tech Debt | {debt_h}h {debt_m}m | ⚠️ |",
    f"| Reliability Rating | {rating_map.get(measures['reliability_rating'], '?')} | |",
    f"| Security Rating | {rating_map.get(measures['security_rating'], '?')} | |",
    "",
    "### Issue Breakdown",
    "",
    "| Type | 🔴 BLOCKER | 🟠 CRITICAL | 🟡 MAJOR | 🔵 MINOR | ⚪ INFO | Total |",
    "|------|-----------|------------|---------|---------|--------|-------|",
]

def breakdown_row(name, items):
    c = count_by(items)
    return f"| {name} | {c.get('BLOCKER',0)} | {c.get('CRITICAL',0)} | {c.get('MAJOR',0)} | {c.get('MINOR',0)} | {c.get('INFO',0)} | {len(items)} |"

c_hs = count_by(hotspots, "vulnerabilityProbability")
L.append(breakdown_row("Vulnerabilities", vulns))
L.append(breakdown_row("Bugs", bugs))
L.append(breakdown_row("Code Smells", smells))
L.append(f"| Security Hotspots | — | — | 🔴 {c_hs.get('HIGH',0)} HIGH | 🟠 {c_hs.get('MEDIUM',0)} MEDIUM | 🔵 {c_hs.get('LOW',0)} LOW | {len(hotspots)} |")
L.append("")

has_critical = int(measures['vulnerabilities']) > 0 or int(measures['bugs']) > 0
gate_status = "BLOCKED" if has_critical else "PASS"
L.append(f"**Gate Result: {gate_status}**")
L += ["", "---", ""]

# ── Vulnerabilities ────────────────────────────────────────────────────────────
if vulns:
    L += [f"## Vulnerabilities ({len(vulns)})", ""]
    for sev in ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]:
        items = [v for v in vulns if v["severity"] == sev]
        if not items:
            continue
        L += [f"### {sev_icon(sev)} {sev} ({len(items)})", "",
              "| # | File | Line | Rule | Description |",
              "|---|------|------|------|-------------|"]
        for idx, v in enumerate(items, 1):
            file = clean(v["component"])
            line = v.get("line", "—")
            msg  = v.get("message", "")[:120].replace("|", "\\|")
            L.append(f"| {idx} | `{file}` | {line} | `{v.get('rule','')}` | {msg} |")
        L.append("")
    L += ["---", ""]

# ── Bugs ──────────────────────────────────────────────────────────────────────
if bugs:
    L += [f"## Bugs ({len(bugs)})", "",
          "| # | Severity | File | Line | Rule | Description |",
          "|---|----------|------|------|------|-------------|"]
    for idx, b in enumerate(bugs, 1):
        file = clean(b["component"])
        line = b.get("line", "—")
        msg  = b.get("message", "")[:120].replace("|", "\\|")
        sev  = b["severity"]
        L.append(f"| {idx} | {sev_icon(sev)} {sev} | `{file}` | {line} | `{b.get('rule','')}` | {msg} |")
    L += ["", "---", ""]

# ── Security Hotspots ─────────────────────────────────────────────────────────
if hotspots:
    L += [f"## Security Hotspots ({len(hotspots)})", "",
          "| # | Risk | File | Line | Rule | Description |",
          "|---|------|------|------|------|-------------|"]
    risk_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    for idx, h in enumerate(sorted(hotspots, key=lambda x: risk_order.get(x["vulnerabilityProbability"], 3)), 1):
        file = clean(h["component"])
        line = h.get("line", "—")
        msg  = h.get("message", "")[:120].replace("|", "\\|")
        risk = h["vulnerabilityProbability"]
        L.append(f"| {idx} | {risk_icon(risk)} {risk} | `{file}` | {line} | `{h.get('ruleKey','')}` | {msg} |")
    L += ["", "---", ""]

# ── Code Smells ───────────────────────────────────────────────────────────────
if smells:
    L += [f"## Code Smells ({len(smells)})", ""]
    for sev in ["CRITICAL", "MAJOR", "MINOR", "INFO"]:
        items = [s for s in smells if s["severity"] == sev]
        if not items:
            continue
        L += [f"### {sev_icon(sev)} {sev} ({len(items)})", "",
              "| # | File | Line | Rule | Description |",
              "|---|------|------|------|-------------|"]
        for idx, s in enumerate(items, 1):
            file = clean(s["component"])
            line = s.get("line", "—")
            msg  = s.get("message", "")[:120].replace("|", "\\|")
            L.append(f"| {idx} | `{file}` | {line} | `{s.get('rule','')}` | {msg} |")
        L.append("")
    L += ["---", ""]

# ── Scan Details ──────────────────────────────────────────────────────────────
L += [
    "## Scan Details",
    "",
    "| Item | Value |",
    "|------|-------|",
    f"| Host | {host} |",
    f"| Project Key | {project} |",
    f"| Report Generated | {now} |",
    "",
]

# ── Write file ────────────────────────────────────────────────────────────────
os.makedirs("reports", exist_ok=True)
ts  = int(datetime.datetime.now().timestamp())
out = f"reports/{ts}_sonarcloud_report.md"

with open(out, "w") as f:
    f.write("\n".join(L))

print(f"[sonar-report] Report saved: {out}")
print(f"[sonar-report] Gate: {gate_status} | Vulns: {len(vulns)} | Bugs: {len(bugs)} | Hotspots: {len(hotspots)} | Smells: {len(smells)}")
