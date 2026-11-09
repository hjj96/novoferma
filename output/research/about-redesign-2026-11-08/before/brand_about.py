# -*- coding: utf-8 -*-
"""About-page content for the calm Novoferma editorial system."""


def render_about(crumb, asset_url, btn, arrow):
    meal = asset_url('assets/editorial/meal-v1.webp')
    pack = asset_url('assets/catalogue-clean-v2/frikadelki-klassicheskie.webp')
    hen = asset_url('assets/product-hero/running-mascot-v2.webp')
    return crumb('О Новоферме') + f'''
<section class="nf-about-hero nf-about-container" aria-labelledby="nf-about-heading">
  <div class="nf-about-intro">
    <p class="nf-about-kicker">О Новоферме</p>
    <h1 id="nf-about-heading"><span>Хорошая еда.</span><span>Больше времени <em>вместе.</em></span></h1>
    <p class="nf-about-lead">Мы — Новоферма из Санкт-Петербурга. Делаем замороженные продукты из курицы и индейки для повседневных обедов и ужинов.</p>
    <p class="nf-about-body">Котлеты, фрикадельки, наггетсы и стрипсы — знакомые продукты, с которыми легко собрать всех за столом.</p>
    <a class="nf-about-link" href="catalogue.html">Выбрать продукты{arrow()}</a>
  </div>
  <figure class="nf-about-meal">
    <img src="{meal}" width="1254" height="1254" alt="Идея подачи: куриные фрикадельки с картофельным пюре и зеленью" fetchpriority="high" decoding="async">
    <figcaption>Для обычных дней и тёплых встреч. Вариант подачи.</figcaption>
  </figure>
</section>

<section class="nf-about-packaging nf-about-container" aria-labelledby="nf-packaging-heading">
  <figure class="nf-about-pack">
    <div class="nf-about-pack-stage"><img src="{pack}" width="800" height="800" alt="Фрикадельки «Классические» в прозрачном контейнере с фирменной картонной обечайкой" loading="lazy" decoding="async"></div>
    <figcaption>Фрикадельки «Классические». Упаковка Новофермы.</figcaption>
  </figure>
  <div class="nf-about-pack-copy">
    <p class="nf-about-kicker">Продумано просто</p>
    <h2 id="nf-packaging-heading">Всё видно<br>до покупки.</h2>
    <p class="nf-about-lead">Прозрачный контейнер позволяет рассмотреть продукт прямо на полке.</p>
    <p class="nf-about-body">На обечайке — название и информация о продукте. Внутри — то, что вы выбрали к своему столу.</p>
  </div>
</section>

<section class="nf-about-facts nf-about-container" aria-label="Коротко о наших продуктах">
  <article class="nf-about-fact"><p class="nf-about-number" aria-hidden="true">01</p><h2>Курица и индейка</h2><p>В основе нашего ассортимента — продукты из мяса птицы.</p></article>
  <article class="nf-about-fact"><p class="nf-about-number" aria-hidden="true">02</p><h2>На каждый день</h2><p>Котлеты и фрикадельки к гарниру, наггетсы и стрипсы — с любимым соусом.</p></article>
  <article class="nf-about-fact"><p class="nf-about-number" aria-hidden="true">03</p><h2>Понятная упаковка</h2><p>Прозрачный контейнер и информация о продукте на этикетке.</p></article>
</section>

<section class="nf-about-character" aria-labelledby="nf-character-heading">
  <div class="nf-about-container nf-about-character-inner">
    <img src="{hen}" width="1254" height="1254" alt="" aria-hidden="true" loading="lazy" decoding="async">
    <div><p class="nf-about-kicker">Знакомые на полке</p><h2 id="nf-character-heading">Узнаёте наших?</h2><p>Курочки на упаковке — маленькая деталь, по которой легко найти Новоферму.</p></div>
  </div>
</section>'''
