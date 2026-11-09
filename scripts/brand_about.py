# -*- coding: utf-8 -*-
"""Three clear chapters: company, products and partnership."""


def render_catalogue_preview(product_cards, arrow, *, heading_id='about-products-heading', section_id=''):
    section_id_attr = f' id="{section_id}"' if section_id else ''
    return f'''
<section class="about-products home-products"{section_id_attr} aria-labelledby="{heading_id}">
  <div class="about-shell">
    <div class="about-products-heading">
      <h2 class="about-title" id="{heading_id}">У каждого дня<br><span>свой вкус.</span></h2>
      <a class="about-pill about-pill-dark" href="catalogue.html">Весь каталог{arrow()}</a>
    </div>
    <div class="product-grid featured">{product_cards}</div>
  </div>
</section>
'''


def render_about(crumb, asset_url, btn, arrow, product_cards):
    return crumb('О Новоферме') + f'''
<section class="about-story about-story-hero" id="our-story" aria-labelledby="about-story-heading">
  <div class="about-shell about-story-inner">
    <h1 class="about-title" id="about-story-heading">Когда<br><span>свои рядом.</span></h1>
    <div class="about-story-copy about-copy">
      <p>Мы — Новоферма из Санкт-Петербурга. Делаем замороженные продукты из курицы и индейки, с которыми легко придумать обед, ужин или перекус.</p>
      <p>В нашем ассортименте — котлеты, фрикадельки, наггетсы и стрипсы. Знакомые блюда для домашних обедов, ужинов и встреч за столом.</p>
    </div>
  </div>
</section>

{render_catalogue_preview(product_cards, arrow)}

<section class="cooperation-invite cooperation-invite-about" aria-labelledby="invite-about-heading">
  <div class="about-shell cooperation-invite-inner">
    <h2 class="about-title" id="invite-about-heading">Будем<br><span>партнёрами?</span></h2>
    <div class="cooperation-invite-response">
      <p class="about-copy">Для магазинов, кафе и ресторанов. Расскажите о вашем бизнесе — обсудим сотрудничество.</p>
      <a class="about-pill about-pill-light" href="partners.html">Стать партнёром{arrow()}</a>
    </div>
  </div>
</section>'''
