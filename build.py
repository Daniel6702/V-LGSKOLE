#!/usr/bin/env python3
"""Build a static, GitHub Pages-ready VÆLGSKOLE pre-launch website.

No dependencies. The local configuration is not tracked in Git; the rendered
business contact details in docs/ are necessarily public.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"
DEFAULT_OUTPUT = ROOT / "docs"
DEFAULT_CONFIG = ROOT / "business.local.json"
FIELDS = {
    "business_name": "Registreret virksomhedsnavn (præcis som i CVR)",
    "cvr": "CVR-nummer (8 cifre)",
    "street": "Virksomhedens offentlige adresse (vej og nr.)",
    "postcode_city": "Postnummer og by",
    "email": "Kontakt-e-mail (skal kunne MODTAGE mails)",
    "phone": "Offentligt kontakttelefonnummer (fx +45 12 34 56 78)",
}
PAGES = ("index.html", "handelsbetingelser.html", "privatlivspolitik.html")


def read_config(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Kunne ikke læse konfigurationen {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("Konfigurationen skal være et JSON-objekt.")
    return {key: str(data.get(key, "")).strip() for key in FIELDS}


def interactive_config(path: Path) -> dict[str, str]:
    print("Opsæt virksomhedsoplysninger til VÆLGSKOLE.\n")
    values = {}
    for key, title in FIELDS.items():
        values[key] = input(f"{title}: ").strip()
    validate(values)
    path.write_text(json.dumps(values, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nGemte lokal konfiguration: {path.name} (udeladt fra Git)\n")
    return values


def validate(data: dict[str, str]) -> None:
    for key, label in FIELDS.items():
        value = data.get(key, "").strip()
        if not value or any(token in value.lower() for token in ("udfyld", "placeholder", "example.com")):
            raise SystemExit(f"Udfyld feltet: {label}")
        if "\n" in value or "\r" in value:
            raise SystemExit(f"Ugyldigt linjeskift i feltet: {label}")
    if not re.fullmatch(r"\d{8}", data["cvr"]):
        raise SystemExit("CVR-nummer skal bestå af præcis 8 cifre.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", data["email"], flags=re.ASCII):
        raise SystemExit("Kontakt-e-mail er ugyldig. Brug evt. domænets Punycode-form ved æ/ø/å.")
    if not re.fullmatch(r"\+?[\d ()-]{7,24}", data["phone"]):
        raise SystemExit("Telefonnummer ser ugyldigt ud.")


def build(data: dict[str, str], output: Path) -> None:
    validate(data)
    output.mkdir(parents=True, exist_ok=True)
    source_assets = DEFAULT_OUTPUT / "assets"
    target_assets = output / "assets"
    if output.resolve() != DEFAULT_OUTPUT.resolve():
        if target_assets.exists():
            shutil.rmtree(target_assets)
        shutil.copytree(source_assets, target_assets)

    email = data["email"]
    phone = data["phone"]
    tokens = {
        "BUSINESS_NAME": data["business_name"],
        "CVR": data["cvr"],
        "STREET": data["street"],
        "POSTCODE_CITY": data["postcode_city"],
        "EMAIL": email,
        "EMAIL_HREF": email,  # email syntax validated; attribute is HTML escaped
        "PHONE": phone,
        "PHONE_HREF": re.sub(r"[^+0-9]", "", phone),
    }

    def apply(value: str) -> str:
        for key, text in tokens.items():
            value = value.replace("@" + key + "@", html.escape(text, quote=True))
        return value

    header = apply((TEMPLATES / "_header.html").read_text(encoding="utf-8"))
    footer = apply((TEMPLATES / "_footer.html").read_text(encoding="utf-8"))
    for page in PAGES:
        page_html = (TEMPLATES / page).read_text(encoding="utf-8")
        page_html = page_html.replace("@HEADER@", header).replace("@FOOTER@", footer)
        page_html = apply(page_html)
        if re.search(r"@(BUSINESS_NAME|CVR|STREET|POSTCODE_CITY|EMAIL|PHONE|HEADER|FOOTER)(?:_HREF)?@", page_html):
            raise SystemExit(f"Skabelonfejl: uerstattede felter i {page}")
        (output / page).write_text(page_html, encoding="utf-8")
    (output / ".nojekyll").touch()
    (output / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    check(output)
    print(f"OK: {len(PAGES)} sider genereret i {output}")
    print("OBS: Offentlig adresse, telefon, CVR og e-mail bliver synlige på hjemmesiden.")


def check(output: Path) -> None:
    for page in PAGES:
        path = output / page
        if not path.exists():
            raise SystemExit(f"Mangler side: {path}")
        content = path.read_text(encoding="utf-8")
        if not all(mark in content for mark in ('lang="da"', "<main", "<footer", "CVR")):
            raise SystemExit(f"Manglende HTML-struktur: {page}")
        if "@BUSINESS_NAME@" in content or "@CVR@" in content or "@HEADER@" in content:
            raise SystemExit(f"Konfiguration ikke fuldført i {page}")
        for local_file in re.findall(r'(?:href|src)="([^"]+)"', content):
            if local_file.startswith(("#", "mailto:", "tel:", "https://", "http://")):
                continue
            target = local_file.split("#", 1)[0]
            if not target:
                continue
            if not (output / target).is_file():
                raise SystemExit(f"Ødelagt lokalt link: {page} → {local_file}")
    print("OK: links, genererede værdier og sidestruktur valideret")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edit", action="store_true", help="Indtast virksomhedsoplysninger på ny")
    parser.add_argument("--check", action="store_true", help="Kontroller den byggede hjemmeside")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Brug en alternativ JSON-konfiguration")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Skriv genererede sider til alternativ mappe")
    args = parser.parse_args()
    if args.check:
        check(args.output)
        return
    if args.edit and args.config != DEFAULT_CONFIG:
        parser.error("--edit kan ikke kombineres med --config")
    if args.edit or not args.config.exists():
        if not sys.stdin.isatty():
            raise SystemExit("Opret business.local.json, eller kør kommandoen interaktivt i terminalen.")
        data = interactive_config(args.config)
    else:
        data = read_config(args.config)
    build(data, args.output)


if __name__ == "__main__":
    main()
