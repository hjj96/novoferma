# -*- coding: utf-8 -*-
"""Four clear chapters: brand, company, products and partnership."""


def render_about(crumb, asset_url, btn, arrow, product_cards):
    nuggets = asset_url('assets/product-hero/desktop-v8/nuggets-food.webp')
    return crumb('О Новоферме') + f'''
<section class="about-poster" aria-labelledby="about-heading">
  <div class="about-shell about-poster-inner">
    <div class="about-poster-copy">
      <h1 class="about-title" id="about-heading">Для своих.<br><span>Каждый день.</span></h1>
      <p class="about-copy">Любимая еда. Тёплая компания.<br>И побольше времени друг для друга.</p>
      <a class="about-pill about-pill-light" href="#our-story">Давайте знакомиться<span aria-hidden="true">↓</span></a>
    </div>
    <div class="about-poster-art">
      <img src="{nuggets}" width="1254" height="1254" alt="Куриные наггетсы с соусом" fetchpriority="high" decoding="async">
    </div>
  </div>
</section>

<section class="about-story about-shell" id="our-story" aria-labelledby="about-story-heading">
  <h2 class="about-title" id="about-story-heading">Когда<br><span>свои рядом.</span></h2>
  <div class="about-story-copy about-copy">
    <p>Мы — Новоферма из Санкт-Петербурга. Делаем замороженные продукты из курицы и индейки, с которыми легко придумать обед, ужин или перекус.</p>
    <p>В нашем ассортименте — котлеты, фрикадельки, наггетсы и стрипсы. Знакомые блюда для домашних обедов, ужинов и встреч за столом.</p>
  </div>
</section>

<section class="about-products home-products" aria-labelledby="about-products-heading">
  <div class="about-shell">
    <div class="about-products-heading">
      <h2 class="about-title" id="about-products-heading">У каждого дня<br><span>свой вкус.</span></h2>
      <a class="about-pill about-pill-dark" href="catalogue.html">Весь каталог{arrow()}</a>
    </div>
    <div class="product-grid featured">{product_cards}</div>
  </div>
</section>

<section class="cooperation-invite cooperation-invite-about" aria-labelledby="invite-about-heading">
  <div class="about-shell cooperation-invite-inner">
    <h2 class="about-title" id="invite-about-heading">Будем<br><span>партнёрами?</span></h2>
    <div class="cooperation-invite-response">
      <p class="about-copy">Для магазинов, кафе и ресторанов. Расскажите о вашем бизнесе — обсудим сотрудничество.</p>
      <a class="about-pill about-pill-light" href="partners.html">Стать партнёром{arrow()}</a>
    </div>
  </div>
</section>'''
