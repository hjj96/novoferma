#!/usr/bin/env python3
"""Build a standalone, printable supplier catalogue from reviewed public facts.

Python 3.9+, standard library only. No network calls or runtime site mutations.
Run: python3 scripts/build_supplier_materials.py
"""
import base64
import hashlib
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/b2b-content.json"
OUTPUT = ROOT / "output/concept/downloads/novoferma-supplier-catalogue.html"
ALLOWED_FIELDS = {"name", "weight", "weightGrams"}


def validate(data):
    """Fail closed if facts, provenance or explicit publication gates change."""
    if data.get("publicationStatus") != "publishable_verified_subset":
        raise ValueError("Registry is not cleared for publishing its verified subset")
    policy = data["publicationPolicy"]
    if set(policy["allowedProductFields"]) != ALLOWED_FIELDS:
        raise ValueError("This renderer only supports reviewed names and weights")
    products = data["products"]
    if len(products) != 14 or len({p["slug"] for p in products}) != 14:
        raise ValueError("Expected 14 distinct reviewed catalogue entries")
    sources = {s["id"]: s for s in data["sources"]}
    inventory_path = ROOT / data["inventory"]["path"]
    inventory = {p["slug"]: p for p in json.loads(inventory_path.read_text())}
    if set(inventory) != {p["slug"] for p in products}:
        raise ValueError("Registry and site inventory differ: review the source data")
    for product in products:
        if product["publicationStatus"] != "name_weight_only":
            raise ValueError("Unsupported publication status for " + product["slug"])
        original = inventory[product["slug"]]
        expected = {
            "name": original.get("displayName", original["name"]),
            "weight": original["weight"], "weightGrams": original["weightGrams"],
        }
        for field in ALLOWED_FIELDS:
            fact = product["facts"][field]
            if fact["publicationStatus"] != "publishable_source_verified":
                raise ValueError("Unverified field: " + product["slug"] + "." + field)
            if fact["source"] not in sources or not fact.get("verifiedAt"):
                raise ValueError("Missing provenance for " + product["slug"])
            if fact["value"] != expected[field] or product[field] != fact["value"]:
                raise ValueError("Fact changed without a matching review: " + product["slug"])
        if set(product["unverifiedFacts"]) != set(policy["excludedProductFields"]):
            raise ValueError("Incomplete unverified-facts gate for " + product["slug"])
        for gate in product["unverifiedFacts"].values():
            if gate["publicationStatus"] != "blocked_unverified" or gate["value"] is not None:
                raise ValueError("New specification facts require a reviewed renderer update")
    for gate in data["businessGates"].values():
        if gate["publicationStatus"] != "blocked_unverified" or gate["value"] is not None:
            raise ValueError("New commercial terms require a reviewed renderer update")
    if any(c["includeInSupplierCatalogue"] for c in data["concepts"]):
        raise ValueError("Concepts are not approved for this catalogue")
    contacts = data["contacts"]
    if contacts["publicationStatus"] != "publishable_official_contact":
        raise ValueError("Contact details are not verified")
    if contacts["source"] not in sources:
        raise ValueError("Missing contact source")


def render(data):
    e = escape
    contact = data["contacts"]["orderDepartment"]
    office = data["contacts"]["office"]
    version = e(data["contentVersion"])
    rows = []
    for n, p in enumerate(data["products"], 1):
        name = e(p["facts"]["name"]["value"])
        weight = e(p["facts"]["weight"]["value"])
        slug = e(p["slug"])
        rows.append(f'''<tr data-product-id="{slug}">
          <td class="pick"><label><input type="checkbox" aria-label="Выбрать: {name}"><span class="sr-only">Выбрать {name}</span></label></td>
          <th scope="row">{name}</th><td class="weight">{weight}</td>
          <td class="amount"><input type="text" aria-label="Желаемый объём: {name}" placeholder="" maxlength="36"></td>
        </tr>''')
    table_rows = "\n".join(rows)
    logo = base64.b64encode((ROOT / "output/concept/assets/logo-reference.webp").read_bytes()).decode("ascii")
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Каталог Новофермы для запроса: 14 наименований, масса упаковки и контакты отдела приёма заказов.">
<meta name="color-scheme" content="light">
<title>Новоферма — ассортимент для партнёров</title>
<style>
*{{box-sizing:border-box}}html{{background:#f3eee4;color:#412615;font-family:Arial,Helvetica,sans-serif;line-height:1.5}}
body{{margin:0}}a{{color:#9f3b13;text-underline-offset:.2em}}a:hover{{text-decoration-thickness:2px}}
button,input{{font:inherit}}button,a,input{{touch-action:manipulation}}
:focus-visible{{outline:3px solid #be4e24;outline-offset:4px}}
.sheet{{max-width:1000px;margin:32px auto;background:#fffdf8;border:1px solid #ddd8cc;border-radius:20px;padding:42px 48px;box-shadow:0 12px 35px #41261509}}
.masthead{{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:32px}}
.wordmark img{{display:block;width:190px;height:auto;margin-bottom:8px}}
.wordmark{{font-weight:900;font-size:28px;letter-spacing:-1.2px;line-height:1;color:#412615}}
.label{{font-size:12px;text-transform:uppercase;letter-spacing:.12em;font-weight:700;color:#665e51}}
.print-button{{background:#fffdf8;color:#412615;border:1px solid #412615;padding:10px 14px;min-height:44px;border-radius:9px;cursor:pointer}}
.eyebrow{{margin:0 0 8px;color:#a64621;font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase}}
h1{{font-size:44px;line-height:1.08;letter-spacing:-1.8px;max-width:650px;margin:0 0 18px;font-weight:800}}
.intro{{font-size:17px;color:#5d4738;max-width:750px;margin:0}}
.section-title{{font-size:19px;margin:0 0 8px;letter-spacing:-.3px}}
.catalogue{{margin-top:30px}}
table{{width:100%;border-collapse:collapse;font-size:15px}}
caption{{text-align:left;padding:0 0 12px;font-size:13px;color:#6a5140}}
thead th{{font-size:12px;letter-spacing:.03em;font-weight:700;text-align:left;border-bottom:2px solid #412615;padding:10px 8px}}
tbody th,tbody td{{border-bottom:1px solid #deded3;padding:10px 8px;vertical-align:middle}}
tbody th{{text-align:left;font-weight:500}}tbody tr:nth-child(even){{background:#f6f4ed}}
.pick{{width:42px;text-align:center}}.pick input{{width:18px;height:18px;accent-color:#412615;vertical-align:middle}}
.pick label{{display:flex;min-width:24px;min-height:24px;align-items:center;justify-content:center}}
.weight{{width:110px;white-space:nowrap;font-variant-numeric:tabular-nums}}
.amount{{width:160px}}.amount input{{width:100%;min-width:0;border:0;border-bottom:1px solid #9ca595;border-radius:0;background:transparent;color:#412615;padding:3px 2px;min-height:26px;font-size:14px}}
.small-note{{font-size:12px;color:#6a5140;margin:12px 0 0}}
.next-step{{margin-top:30px;padding:22px 24px;border:1px solid #d7c6ae;border-radius:14px;background:#f2e4c9;display:grid;grid-template-columns:1.2fr 1fr;gap:26px}}
.next-step h2{{font-size:20px;line-height:1.2;letter-spacing:-.4px;margin:0 0 10px}}
.next-step p{{margin:0;font-size:14px}}
.contact-link{{display:block;font-size:19px;font-weight:700;line-height:1.5;overflow-wrap:anywhere}}
.contact-label{{font-size:12px;font-weight:700;color:#6a5140;margin-bottom:4px!important}}
.office{{margin-top:12px!important;font-size:12px!important;color:#6a5140}}
.request-fields{{display:flex;gap:24px;margin-top:19px;font-size:12px;color:#6a5140}}
.request-fields label{{flex:1}}.request-fields input{{display:block;width:100%;margin-top:4px;padding:3px 0;min-height:28px;background:transparent;border:0;border-bottom:1px solid #a9ad9d;border-radius:0;color:#412615}}
footer{{margin-top:24px;padding-top:14px;color:#6a5140;font-size:11px}}
footer p{{margin:0 0 5px}}.source-links{{display:flex;flex-wrap:wrap;gap:4px 14px}}.sr-only{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}
@media(max-width:640px){{.sheet{{margin:0;padding:25px 18px;border:0;border-radius:0;box-shadow:none}}.masthead{{align-items:flex-start;flex-wrap:wrap;margin-bottom:28px}}.wordmark{{font-size:25px}}.label{{font-size:10px}}h1{{font-size:35px;letter-spacing:-1.2px}}.intro{{font-size:15px}}.catalogue{{margin-top:24px}}table{{font-size:13px}}thead th{{font-size:10px;padding:8px 4px}}tbody th,tbody td{{padding:9px 4px}}.pick{{width:30px}}.weight{{width:59px}}.amount{{width:76px}}.amount input{{font-size:12px}}.next-step{{grid-template-columns:1fr;padding:19px;gap:18px}}.request-fields{{flex-direction:column;gap:10px}}}}
@page{{size:A4 portrait;margin:13mm}}
@media print{{html{{background:#fff;color:#28180f;font-size:10pt}}body{{margin:0}}.sheet{{max-width:none;margin:0;padding:0;border:0;border-radius:0;box-shadow:none}}.print-button{{display:none}}.masthead{{margin-bottom:15px}}.wordmark{{font-size:22pt}}.label{{font-size:8pt}}.eyebrow{{font-size:8pt;margin-bottom:5px}}h1{{font-size:28pt;max-width:none;margin-bottom:10px}}.intro{{font-size:10pt;line-height:1.4}}.catalogue{{margin-top:16px}}.section-title{{font-size:12pt}}table{{font-size:9pt}}caption{{font-size:8pt;padding-bottom:6px}}thead{{display:table-header-group}}thead th{{font-size:8pt;padding:5px 6px}}tbody th,tbody td{{padding:4px 6px}}tr{{break-inside:avoid}}.pick{{width:27px}}.pick input{{width:12px;height:12px}}.pick label{{min-height:18px}}.amount{{width:120px}}.amount input{{font-size:9pt;min-height:18px;padding:0}}.weight{{width:75px}}.small-note{{font-size:7.5pt;margin-top:7px}}.next-step{{margin-top:15px;padding:12px 15px;gap:18px;break-inside:avoid}}.next-step h2{{font-size:12pt;margin-bottom:6px}}.next-step p{{font-size:8.5pt}}.contact-link{{font-size:12pt}}.contact-label,.office{{font-size:8pt!important}}.office{{margin-top:7px!important}}.request-fields{{margin-top:10px;font-size:8pt;gap:20px}}.request-fields input{{font-size:8pt;min-height:18px}}footer{{margin-top:12px;padding-top:8px;font-size:7pt;break-inside:avoid}}a{{color:inherit}}.sheet{{print-color-adjust:exact;-webkit-print-color-adjust:exact}}}}
</style>
</head>
<body>
<main class="sheet">
  <header>
    <div class="masthead"><div><div class="wordmark"><img src="data:image/webp;base64,{logo}" width="342" height="64" alt="NOVOferma"></div><div class="label">Каталог для партнёров</div></div><button class="print-button" type="button" onclick="window.print()">Распечатать / сохранить PDF</button></div>
    <p class="eyebrow">Ассортимент для запроса</p>
    <h1>Знакомые продукты.<br>Понятный выбор.</h1>
    <p class="intro">Выберите позиции и отправьте запрос в отдел приёма заказов. Актуальные фасовки, наличие и условия поставки уточняются при обращении.</p>
  </header>
  <section class="catalogue" aria-labelledby="catalogue-heading">
    <h2 id="catalogue-heading" class="section-title">14 наименований из каталога</h2>
    <table>
      <caption>Отметьте нужные позиции. В последней колонке укажите желаемый объём и единицу: упаковки или кг.</caption>
      <thead><tr><th scope="col" class="pick"><span class="sr-only">Выбор</span></th><th scope="col">Наименование</th><th scope="col" class="weight">Масса упаковки</th><th scope="col" class="amount">Ваш объём</th></tr></thead>
      <tbody>{table_rows}</tbody>
    </table>
    <p class="small-note">Масса указана для упаковки из опубликованного каталога, а не для транспортного короба. Спецификацию и маркировку выбранной позиции запросите перед заказом.</p>
  </section>
  <section class="next-step" aria-labelledby="request-heading">
    <div><h2 id="request-heading">Обсудим ваш запрос</h2><p>Напишите выбранные позиции, ориентировочный объём, город и удобный способ связи. Для проекта под вашей маркой добавьте описание продукта и предполагаемую фасовку.</p></div>
    <div><p class="contact-label">{e(contact['label'])}</p><a class="contact-link" href="mailto:{e(contact['email'])}">{e(contact['email'])}</a><a class="contact-link" href="tel:{e(contact['tel'])}">{e(contact['phone'])}</a><p class="office">Общий офис: <a href="mailto:{e(office['email'])}">{e(office['email'])}</a> · <a href="tel:{e(office['tel'])}">{e(office['phone'])}</a></p></div>
  </section>
  <div class="request-fields"><label>Компания и город<input type="text" name="company_city" maxlength="150" autocomplete="off"></label><label>Контакт для ответа<input type="text" name="reply_contact" maxlength="120" autocomplete="off"></label></div>
  <footer>
    <p>Названия и масса: официальный каталог, прямая проверка 24.10.2026; сверка по поисковому индексу 05.11.2026. Контакты — официальная страница компании. Версия {version}.</p>
    <p>Этот лист помогает составить запрос и не заменяет спецификацию или коммерческое предложение. Заполненные поля не отправляются автоматически.</p>
    <div class="source-links"><a href="https://novoferma.ru/catalogue">novoferma.ru/catalogue</a><a href="https://novoferma.ru/contact">novoferma.ru/contact</a></div>
  </footer>
</main>
</body>
</html>
'''


def main():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    validate(data)
    html = render(data)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT.relative_to(ROOT)),
                      "contentVersion": data["contentVersion"],
                      "products": len(data["products"]),
                      "sha256": hashlib.sha256(html.encode()).hexdigest()},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
