"""Buyer journeys. Business terms remain subject to individual confirmation."""
from html import escape
from urllib.parse import urlencode


def request_url(product='', intent='quote', format='retail'):
    return 'partners.html?' + escape(urlencode({
        'product': product, 'intent': intent, 'format': format,
    }), quote=True) + '#partner-contact'


def partner_form(products, arrow):
    options = '<option value="">Помогите подобрать ассортимент</option>'
    options += ''.join(
        '<option value="{id}">{name}{weight}{status}</option>'.format(
            id=escape(p['id']), name=escape(p['name']),
            weight=' — '+escape(p['weight']) if p.get('weight') else '',
            status=' — концепт новинки' if p.get('concept') else '') for p in products)
    return f'''<form class="partners-form" id="partner-request-form" action="mailto:zakaz@novoferma.ru" method="get">
<fieldset><legend>Какой формат вам интересен?</legend><div class="partners-format-options">
<label class="partners-format-option"><input type="radio" name="format" value="retail" checked aria-describedby="partner-format-help"><span>Розница</span></label>
<label class="partners-format-option"><input type="radio" name="format" value="horeca" aria-describedby="partner-format-help"><span>HoReCa</span></label>
<label class="partners-format-option"><input type="radio" name="format" value="stm" aria-describedby="partner-format-help"><span>СТМ</span></label>
</div><p class="partners-format-help" id="partner-format-help" aria-live="polite">Продукция Новофермы для вашего ассортимента.</p></fieldset>
<div class="partners-form-fields">
<label class="partners-form-field partners-form-field-wide"><span>Продукт</span><select id="partner-product" name="product">{options}</select></label>
<label class="partners-form-field partners-form-field-wide"><span>Что обсудим?</span><select id="partner-intent" name="intent"><option value="quote">Ассортимент и условия поставки</option><option value="specification">Спецификацию и документы</option><option value="samples">Возможность получить образцы</option><option value="stm">Проект под собственной маркой</option></select></label>
<label class="partners-form-field"><span>Компания *</span><input type="text" name="company" autocomplete="organization" placeholder="Название компании" maxlength="120" required></label>
<label class="partners-form-field"><span>Город</span><input type="text" name="city" autocomplete="address-level2" placeholder="Ваш город" maxlength="100"></label>
<label class="partners-form-field partners-form-field-wide"><span>Телефон или почта *</span><input type="text" name="contact" autocomplete="off" placeholder="Как с вами связаться" maxlength="160" required></label>
<label class="partners-form-field partners-form-field-wide"><span>Ваш запрос</span><textarea name="message" placeholder="Продукты, планируемый объём, упаковка или задача" maxlength="1200"></textarea></label>
</div>
<label class="partners-consent"><input type="checkbox" id="partner-consent" name="consent" required><span>Разрешаю использовать указанные данные, чтобы ответить на мой запрос. *</span></label>
<details class="partners-data-notice"><summary>Как используются данные</summary><p>Компания ООО «НОВОФЕРМА» получает название компании, город, контакт и текст запроса для обсуждения сотрудничества. Укажите рабочий контакт и не добавляйте лишние персональные сведения. По вопросам обработки данных можно написать на <a href="mailto:info@novoferma.ru">info@novoferma.ru</a>.</p></details>
<div class="partners-form-actions"><button class="button button-dark" type="submit">Отправить запрос{arrow()}</button><button class="partners-copy-button" id="partner-copy-request" type="button">Скопировать запрос</button></div>
<p class="partners-form-note">После сохранения запроса появится его номер. Условия, сроки и возможность поставки согласуем отдельно.</p>
<p class="partners-form-feedback" id="partner-request-feedback" role="status" aria-live="polite" aria-atomic="true" hidden></p>
<textarea class="partners-draft" id="partner-request-draft" aria-label="Текст запроса для копирования" readonly hidden></textarea>
<a class="partners-email-fallback" id="partner-email-request" href="mailto:zakaz@novoferma.ru">Отправить через свою почту</a>
<noscript><p class="partners-form-note">Для отправки формы нужен JavaScript. Напишите на zakaz@novoferma.ru или позвоните по указанному телефону.</p></noscript>
</form>'''


def partners_section(products, arrow, asset_url):
    return f'''<section class="partners-business" aria-labelledby="partners-heading"><div class="wrap partners-business-inner">
<div class="partners-business-copy"><p class="eyebrow">Магазинам · HoReCa · СТМ</p><h1 id="partners-heading"><span>Дело</span> <span>со вкусом.</span></h1><p class="partners-business-description">Замороженные продукты из курицы и&nbsp;индейки для вашей полки, меню или собственной марки.</p><a class="button partners-primary" href="#partner-contact">Запросить условия{arrow()}</a></div>
<figure class="partners-business-scene"><div class="partners-scene-disc" aria-hidden="true"></div><img class="partners-host" src="{asset_url('assets/partners-brand-v1/partner-host-v1.webp')}" width="1024" height="1536" alt="Фирменная курочка Новофермы приглашает к сотрудничеству" fetchpriority="high" decoding="sync"></figure>
</div></section>
<section class="b2b-segments wrap" aria-labelledby="formats-heading"><div class="b2b-section-heading"><p class="eyebrow">Найдём ваш формат</p><h2 id="formats-heading">На полку. В меню.<br><em>Под вашей маркой.</em></h2></div><div class="b2b-segment-grid">
<article id="partner-retail"><p class="b2b-number">01 / Розница</p><h3>Для вашей полки</h3><p>Котлеты, наггетсы, фрикадельки, попкорн и стрипсы в потребительской упаковке.</p><a class="text-link" href="{request_url(format='retail')}" data-partner-format="retail">Запросить прайс{arrow()}</a></article>
<article id="partner-horeca"><p class="b2b-number">02 / HoReCa</p><h3>Для вашего меню</h3><p>Обсудим продукты, объём и подходящий формат поставки для вашего заведения.</p><a class="text-link" href="{request_url(format='horeca')}" data-partner-format="horeca">Обсудить поставки{arrow()}</a></article>
<article id="private-label"><p class="b2b-number">03 / СТМ</p><h3>Для вашей марки</h3><p>Обсудим выпуск под вашей торговой маркой. Начнём с продукта, упаковки и задачи.</p><a class="text-link" href="private-label.html">Как обсудить СТМ{arrow()}</a></article>
</div></section>
<section class="b2b-materials" aria-labelledby="buyer-materials-heading"><div class="wrap b2b-materials-inner"><div><p class="eyebrow">Закупщику под рукой</p><h2 id="buyer-materials-heading">Ассортимент<br><em>без лишних поисков.</em></h2><p>14 продуктов основного каталога: названия, масса упаковок и контакты отдела заказов. Концепты новинок показаны отдельно на сайте.</p></div><div class="b2b-material-actions"><a class="button button-dark" href="downloads/novoferma-supplier-catalogue.html" target="_blank" rel="noopener">Открыть каталог{arrow()}</a><p>HTML · печать и сохранение через браузер</p><a class="text-link" href="catalogue.html">Посмотреть продукты{arrow()}</a><a class="text-link" href="{request_url(intent='specification')}" data-partner-format="retail" data-partner-intent="specification">Запросить спецификации{arrow()}</a></div></div></section>
<section class="wrap b2b-answers" aria-labelledby="buyer-answers-heading"><div><p class="eyebrow">До первой поставки</p><h2 id="buyer-answers-heading">Договоримся<br><em>о деталях.</em></h2></div><div class="b2b-questions">
<details><summary>Какие условия нужно уточнить?</summary><p>Минимальную партию, цену, регион и способ доставки, оплату и сроки. Укажите город и планируемый объём в запросе — эти параметры согласуются индивидуально.</p></details>
<details><summary>Где получить состав и документы?</summary><p>Запросите актуальную спецификацию выбранного продукта: состав, аллергены, пищевую ценность, хранение и приготовление. Комплект документов для вашей закупки уточняется у отдела заказов.</p></details>
<details><summary>Можно обсудить образцы или новинку?</summary><p>Да, выберите в форме запрос об образцах или нужный концепт новинки. Возможность, условия и готовность продукта команда подтвердит отдельно.</p></details>
</div></section>
<section class="partners-contact" id="partner-contact" aria-labelledby="partner-contact-heading"><div class="wrap partners-contact-inner"><div class="partners-contact-copy"><p class="eyebrow">От запроса к разговору</p><h2 id="partner-contact-heading">Давайте<br><em>обсудим.</em></h2><p class="partners-contact-description">Выберите формат и продукт, оставьте рабочий контакт. Так мы сможем обсудить именно вашу задачу.</p><div class="partners-direct"><a class="partners-direct-email" href="mailto:zakaz@novoferma.ru">zakaz@novoferma.ru{arrow()}</a><a class="partners-direct-phone" href="tel:+79312135550">+7 (931) 213-55-50</a></div></div>{partner_form(products, arrow)}</div></section>'''


def private_label_section(arrow, asset_url):
    return f'''<section class="wrap stm-intro" aria-labelledby="stm-heading"><div><p class="eyebrow">Собственная торговая марка / СТМ</p><h1 id="stm-heading">Ваш бренд.<br><em>Наш продукт.</em></h1><p class="stm-lead">Обсудим выпуск замороженных продуктов из мяса птицы под вашей торговой маркой — начнём с задачи и желаемых характеристик.</p><a class="button button-dark" href="{request_url(intent='stm',format='stm')}">Обсудить проект{arrow()}</a></div><figure><img src="{asset_url('assets/catalogue-clean-v2/frikadelki-klassicheskie.webp')}" width="800" height="800" alt="Фрикадельки в прозрачном контейнере Новофермы — пример продукции" fetchpriority="high"><figcaption>Пример продукции Новофермы. Не макет упаковки СТМ.</figcaption></figure></section>
<section class="b2b-materials"><div class="wrap stm-brief"><div><p class="eyebrow">Начнём с вашей задачи</p><h2>Что важно<br><em>для вашего бренда?</em></h2><p>Не обязательно иметь готовое техническое задание. Расскажите, что уже определено, а что ещё нужно обсудить.</p></div><dl><div><dt>Продукт и аудитория</dt><dd>Категория, вкус, покупатель и канал продаж.</dd></div><div><dt>Упаковка</dt><dd>Желаемый формат, масса и требования к оформлению.</dd></div><div><dt>Объём и география</dt><dd>Планируемая партия, регулярность и город поставки.</dd></div><div><dt>Задача и сроки</dt><dd>Требования к продукту и желаемая дата запуска.</dd></div></dl></div></section>
<section class="wrap stm-process" aria-labelledby="stm-process-heading"><p class="eyebrow">Путь обсуждения проекта</p><h2 id="stm-process-heading">От идеи<br><em>к общему плану.</em></h2><ol><li><h3>Ваша задача</h3><p>Получаем запрос и уточняем продукт, канал продаж, объём и требования.</p></li><li><h3>Возможности</h3><p>Обсуждаем, что можем произвести, и какие характеристики нужно согласовать.</p></li><li><h3>Продукт и упаковка</h3><p>Согласуем спецификацию, вопрос образцов и требования к маркировке.</p></li><li><h3>Условия проекта</h3><p>Подтверждаем партию, стоимость, сроки и порядок поставки до начала работ.</p></li></ol><p class="b2b-note">Это ориентир для первого разговора. Возможность выпуска, минимальная партия, образцы и сроки подтверждаются после рассмотрения задачи.</p></section>
<section class="stm-invitation"><div class="wrap"><p class="eyebrow">Есть идея для своей марки?</p><h2>Давайте начнём<br><em>с разговора.</em></h2><a class="button button-dark" href="{request_url(intent='stm',format='stm')}">Отправить задачу по СТМ{arrow()}</a><a class="text-link" href="downloads/novoferma-supplier-catalogue.html" target="_blank" rel="noopener">Основной ассортимент{arrow()}</a></div></section>'''
