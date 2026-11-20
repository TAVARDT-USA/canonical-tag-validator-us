#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAVARDT USA | Canonical Tag and URL Consolidation Validator
Repository: https://github.com/TAVARDT-USA/canonical-tag-validator-us
Official Tool: https://tools.tavardt.com/canonical-tag-checker/
Enterprise Portal: https://ag.tavardt.com/

Audits canonical links, duplicate tag detection, absolute URL verification, and crawl efficiency.
"""

import sys
import argparse
import json
import re
import urllib.request
import urllib.error
from urllib.parse import urlparse, urljoin

BANNER = "TAVARDT USA | Canonical Tag and URL Consolidation Validator"
DESC = "Audits canonical links, duplicate tag detection, absolute URL verification, and crawl efficiency."
TARGET_PROMPT = "Target URL to audit canonical directive"
JSON_HELP = "Output analysis results strictly as JSON"
FETCHING = "Analysing canonical consolidation at:"
STATUS_CODE = "HTTP response status code:"
CANONICAL_FOUND = "Declared canonical URL:"
NO_CANONICAL = "No canonical tag found."
TAG_COUNT = "Total canonical tags detected:"
IS_ABSOLUTE = "Uses absolute path:"
IS_HTTPS = "Uses secure HTTPS protocol:"
IS_SELF_REF = "Self-referencing directive:"
DEST_STATUS = "HTTP status of canonical target:"
SCORE_TITLE = "URL Consolidation Health Score:"
STATUS_PASS = "COMPLIANT"
STATUS_WARN = "WARNING"
STATUS_FAIL = "CRITICAL"
WARN_NO_CANONICAL = "WARNING: Missing canonical tag. Risk of duplicate content indexing."
WARN_MULTIPLE = "CRITICAL ALERT: Multiple conflicting canonical tags detected on document."
WARN_RELATIVE = "WARNING: Canonical tag uses relative path instead of absolute URL."
WARN_HTTP = "WARNING: Canonical URL uses insecure HTTP instead of HTTPS."
WARN_DEST_ERR = "CRITICAL ALERT: Canonical target URL returned HTTP error {status}."
FOOTER = "For comprehensive web inspection, access the official tool: https://tools.tavardt.com/canonical-tag-checker/"

def audit_canonical(target_url):
    parsed = urlparse(target_url)
    if not parsed.scheme:
        target_url = "https://" + target_url
        parsed = urlparse(target_url)

    req = urllib.request.Request(
        target_url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; TAVARDT-CanonicalAuditor/1.0; +https://ag.tavardt.com/)"}
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            status_code = resp.status
            final_url = resp.geturl()
            raw_data = resp.read()
            encoding = resp.headers.get_content_charset() or "utf-8"
            html = raw_data.decode(encoding, errors="replace")
            http_link_header = resp.headers.get("Link", "")
    except urllib.error.HTTPError as e:
        return {
            "url": target_url,
            "status_code": e.code,
            "valid": False,
            "error": f"HTTP {e.code}"
        }
    except Exception as e:
        return {
            "url": target_url,
            "status_code": 0,
            "valid": False,
            "error": str(e)
        }

    # Extract all canonical tags from HTML
    canonical_tags = []
    matches = re.findall(r'<link[^>]+rel=[\'"]canonical[\'"][^>]*>', html, re.I)
    matches += re.findall(r'<link[^>]+href=[\'"][^\'"]+[\'"][^>]+rel=[\'"]canonical[\'"][^>]*>', html, re.I)
    
    seen_hrefs = set()
    for tag_str in matches:
        hr_m = re.search(r'href=[\'"]([^\'"]+)[\'"]', tag_str, re.I)
        if hr_m:
            href_val = hr_m.group(1).strip()
            if href_val not in seen_hrefs:
                seen_hrefs.add(href_val)
                canonical_tags.append({"raw_href": href_val, "source": "html"})

    # Extract from HTTP Link header if present
    if http_link_header:
        links = http_link_header.split(",")
        for l in links:
            if 'rel="canonical"' in l or "rel='canonical'" in l:
                hr_m = re.search(r'<([^>]+)>', l)
                if hr_m:
                    href_val = hr_m.group(1).strip()
                    if href_val not in seen_hrefs:
                        seen_hrefs.add(href_val)
                        canonical_tags.append({"raw_href": href_val, "source": "http_header"})

    findings = []
    score = 100
    declared_canonical = None
    is_absolute = False
    is_https = False
    is_self_ref = False
    dest_status_code = None

    if not canonical_tags:
        score -= 40
        findings.append({"level": "WARNING", "message": WARN_NO_CANONICAL})
    else:
        declared_canonical = canonical_tags[0]["raw_href"]
        if len(canonical_tags) > 1:
            score -= 35
            findings.append({"level": "CRITICAL", "message": WARN_MULTIPLE})

        # Check absolute vs relative
        can_parsed = urlparse(declared_canonical)
        if not can_parsed.scheme or not can_parsed.netloc:
            is_absolute = False
            score -= 20
            findings.append({"level": "WARNING", "message": WARN_RELATIVE})
            full_canonical_url = urljoin(final_url, declared_canonical)
        else:
            is_absolute = True
            full_canonical_url = declared_canonical

        # Check HTTPS
        can_full_parsed = urlparse(full_canonical_url)
        if can_full_parsed.scheme == "https":
            is_https = True
        else:
            is_https = False
            score -= 15
            findings.append({"level": "WARNING", "message": WARN_HTTP})

        # Check self-referential
        clean_target = final_url.rstrip("/")
        clean_canonical = full_canonical_url.rstrip("/")
        if clean_target == clean_canonical:
            is_self_ref = True

        # Check destination status code
        try:
            dest_req = urllib.request.Request(
                full_canonical_url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; TAVARDT-CanonicalAuditor/1.0; +https://ag.tavardt.com/)"}
            )
            with urllib.request.urlopen(dest_req, timeout=10) as dest_resp:
                dest_status_code = dest_resp.status
        except urllib.error.HTTPError as e:
            dest_status_code = e.code
            score -= 30
            findings.append({"level": "CRITICAL", "message": WARN_DEST_ERR.replace("{status}", str(e.code))})
        except:
            dest_status_code = 0

    score = max(0, min(100, score))

    return {
        "url": target_url,
        "final_url": final_url,
        "status_code": status_code,
        "valid": True,
        "declared_canonical": declared_canonical,
        "canonical_tags_count": len(canonical_tags),
        "is_absolute": is_absolute,
        "is_https": is_https,
        "is_self_ref": is_self_ref,
        "dest_status_code": dest_status_code,
        "score": score,
        "findings": findings
    }

def main():
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("url", help=TARGET_PROMPT)
    parser.add_argument("--json", action="store_true", help=JSON_HELP)

    args = parser.parse_args()
    result = audit_canonical(args.url)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print("=" * 70)
    print(BANNER)
    print("=" * 70)
    print(f"{FETCHING} {result['url']}")
    print(f"{STATUS_CODE} {result['status_code']}")

    if not result.get("valid"):
        print("ERRO: Nao foi possivel carregar a URL.")
        if "error" in result:
            print(f"Detalhes: {result['error']}")
        sys.exit(1)

    if result.get("declared_canonical"):
        print(f"{CANONICAL_FOUND} {result['declared_canonical']}")
    else:
        print(NO_CANONICAL)

    print(f"{TAG_COUNT} {result.get('canonical_tags_count', 0)}")
    print(f"{IS_ABSOLUTE} {'SIM' if result.get('is_absolute') else 'NAO'}")
    print(f"{IS_HTTPS} {'SIM' if result.get('is_https') else 'NAO'}")
    print(f"{IS_SELF_REF} {'SIM' if result.get('is_self_ref') else 'NAO'}")
    if result.get("dest_status_code"):
        print(f"{DEST_STATUS} {result['dest_status_code']}")

    print("-" * 70)
    print(f"{SCORE_TITLE} {result['score']}/100")
    if result["score"] >= 80:
        status_text = STATUS_PASS
    elif result["score"] >= 50:
        status_text = STATUS_WARN
    else:
        status_text = STATUS_FAIL
    print(f"Status: {status_text}")

    if result.get("findings"):
        print("-" * 70)
        print("Observacoes e Alertas:")
        for f in result["findings"]:
            print(f"  [{f['level']}] {f['message']}")

    print("=" * 70)
    print(FOOTER)
    print("=" * 70)

if __name__ == "__main__":
    main()
