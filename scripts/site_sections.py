# -*- coding: utf-8 -*-
"""Content-focused sections. Product facts and retail links come from verified data."""
import html

def esc(value):
    return html.escape(str(value), quote=True)

def where_section(products, retailers, arrow):
    options=''.join(f'<option value="{esc(p["id"])}">{esc(p["name"])}{(" — "+p["weight"]) if p.get("weight") else ""}</option>' for p in products)
    cards=[]
    for r in retailers:
        ids=' '.join(r.get('productIds',[]))
        product=next((p for p in products if p['id'] in r.get('productIds',[])),None)
        title=product['name'] if product else r['productName']
        weight=f'<span class="retailer-weight">{esc(product["weight"])}</span>' if product and product.get('weight') else ''
        cards.append(f'<article class="retailer-card" data-retailer-products="{esc(ids)}"><p class="eyebrow">{esc(r["name"])}</p><h3>{esc(title)}</h3>{weight}<p>{esc(r.get("note","Наличие зависит от выбранного адреса магазина."))}</p><a class="text-link" href="{esc(r["url"])}" target="_blank" rel="noopener">Посмотреть в магазине{arrow()}</a></article>')
    retail_intro='Выберите продукт, затем укажите свой адрес на сайте магазина. Наличие, фасовка и цена зависят от города и конкретной точки.' if retailers else 'Уточните у команды, где искать нужный продукт в вашем городе.'
    listings=f'<div class="retailer-grid">{"".join(cards)}</div><p class="retailer-empty" hidden>Для этого продукта пока нет подтверждённой ссылки. Уточните наличие у нашей команды ниже.</p><p class="retailer-checked">Ссылки проверены 24 октября 2026 года. Перед покупкой сверяйте массу и состав на актуальной этикетке.</p>' if retailers else ''
    return f'''<section class="wrap section page-intro where-intro"><p class="eyebrow">Где купить</p><h1>Найдите свой<br>продукт.</h1><p class="lead">{retail_intro}</p></section>
<section class="wrap retailers" aria-labelledby="retailers-heading"><div class="retailer-selector"><h2 id="retailers-heading">В магазинах</h2><label for="wanted-product">Что хотите найти?</label><select id="wanted-product" name="product" form="city-form"><option value="">Весь ассортимент</option>{options}</select></div>{listings}</section>
<section class="wrap where-layout"><div class="city-panel"><p class="eyebrow">Не нашли нужное?</p><h2>Уточним<br>для вас.</h2><p class="city-intro">Укажите город — подготовим обращение о выбранном продукте.</p><form id="city-form"><label for="city">Город</label><input id="city" name="city" autocomplete="address-level2" placeholder="Например, Санкт-Петербург" required maxlength="100"><div class="city-actions"><button class="button button-dark" type="submit">Открыть письмо{arrow()}</button><button class="city-copy" type="button" data-city-copy>Скопировать запрос</button></div><p class="form-hint">Запрос отправляете вы. Можно открыть почту или скопировать текст и отправить его на info@novoferma.ru.</p></form><p class="form-feedback" role="status" hidden></p><textarea data-city-draft aria-label="Текст запроса для копирования" readonly hidden></textarea></div><div class="where-explanation"><h3>Свяжитесь напрямую</h3><p>Поможем с вопросами об ассортименте и точках продаж.</p><a class="large-link" href="mailto:info@novoferma.ru">info@novoferma.ru{arrow()}</a><a class="phone-link" href="tel:+78129155454">+7 (812) 915-54-54</a><p class="small-note">При обращении назовите город, продукт и массу упаковки. Наличие уточняйте в магазине перед поездкой.</p></div></section>'''
