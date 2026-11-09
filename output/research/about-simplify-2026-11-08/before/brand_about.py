# -*- coding: utf-8 -*-
"""The Novoferma story through food, everyday moments and the pack."""


def render_about(crumb, asset_url, btn, arrow):
    nuggets = asset_url('assets/product-hero/desktop-v8/nuggets-food.webp')
    company = asset_url('assets/serving-company-crop.webp')
    popsy = asset_url('assets/popsy/popsy-lifestyle-v4.webp')
    pack = asset_url('assets/catalogue-clean-v2/frikadelki-klassicheskie.webp')
    hen = asset_url('assets/product-hero/running-mascot-v2.webp')
    return crumb('О Новоферме') + f'''
<section class="about-poster" aria-labelledby="about-heading">
  <div class="about-shell about-poster-inner">
    <div class="about-poster-copy">
      <p class="about-kicker">Новоферма · Санкт-Петербург</p>
      <h1 id="about-heading">Для своих.<br><span>Каждый день.</span></h1>
      <p class="about-poster-lead">Любимая еда. Тёплая компания.<br>И побольше времени друг для друга.</p>
      <a class="about-pill about-pill-light" href="#our-story">Давайте знакомиться<span aria-hidden="true">↓</span></a>
    </div>
    <figure class="about-poster-art">
      <div class="about-poster-orbit" aria-hidden="true"></div>
      <img src="{nuggets}" width="1254" height="1254" alt="Золотистые куриные наггетсы с соусом: хрустящая корочка и нежная начинка" fetchpriority="high" decoding="async">
      <figcaption>Есть чем поделиться!</figcaption>
      <span class="about-serving-note">Вариант подачи</span>
    </figure>
    <div class="about-poster-bottom"><span>Продукты из курицы и индейки</span><span>Для обычных дней и особенных встреч</span></div>
  </div>
</section>

<section class="about-story about-shell" id="our-story" aria-labelledby="about-story-heading">
  <div class="about-story-heading"><p class="about-kicker">Вот что нас объединяет</p><h2 id="about-story-heading">Хорошо,<br>когда <em>свои рядом.</em></h2></div>
  <div class="about-story-copy"><p class="about-lead">Мы — Новоферма из Санкт-Петербурга. Делаем замороженные продукты из курицы и индейки, с которыми легко придумать обед, ужин или перекус.</p><p>Нам близки простые вещи: знакомый вкус, любимый гарнир и разговоры за столом. Поэтому в нашем ассортименте — котлеты, фрикадельки, наггетсы и стрипсы. Еда, для которой всегда найдётся повод.</p></div>
  <div class="about-principles">
    <article><span class="about-index">01 / В основе</span><h3>Курица и индейка</h3><p>Мясо птицы — основа нашего ассортимента. А дальше — разные вкусы, формы и ваши любимые сочетания.</p></article>
    <article><span class="about-index">02 / В повседневности</span><h3>Знакомые блюда</h3><p>Фрикадельки к пюре, котлеты к овощам, наггетсы к соусу. Выбирайте под настроение и собирайте свой стол.</p></article>
    <article><span class="about-index">03 / В деталях</span><h3>Всё на виду</h3><p>Прозрачный контейнер, информация на обечайке и наши курочки, по которым легко узнать Новоферму.</p></article>
  </div>
</section>

<section class="about-moments about-shell" aria-labelledby="about-moments-heading">
  <div class="about-section-top"><div><p class="about-kicker">Вкусно быть вместе</p><h2 id="about-moments-heading">У каждого дня<br>свой <em>вкус.</em></h2></div><a class="about-text-link" href="catalogue.html">Найти свой продукт{arrow()}</a></div>
  <div class="about-moments-grid">
    <figure class="about-moment about-moment-table"><div class="about-moment-photo"><img src="{company}" width="1008" height="922" alt="Стрипсы и куриный попкорн с овощами и несколькими соусами на общем столе" loading="lazy" decoding="async"><span class="about-photo-note">Вариант подачи</span></div><figcaption><span class="about-index">Когда все в сборе</span><h3>На стол. Для всех.</h3><p>Побольше соусов, любимые закуски — и вечер в хорошей компании.</p></figcaption></figure>
    <figure class="about-moment about-moment-popsy"><div class="about-moment-photo"><img src="{popsy}" width="1536" height="1024" alt="Попсы Новофермы: упаковка и порция мини-наггетсов рядом с наушниками" loading="lazy" decoding="async"><span class="about-photo-note">Вариант подачи</span></div><figcaption><span class="about-index">Когда хочется паузу</span><h3>Маленький перерыв.</h3><p>Музыка, любимый соус и Попсы. Немного времени для себя — тоже хороший план.</p><a class="about-text-link" href="product-popsy.html">Познакомиться с Попсами{arrow()}</a></figcaption></figure>
  </div>
</section>

<section class="about-package" aria-labelledby="about-package-heading">
  <div class="about-shell about-package-inner">
    <div class="about-package-copy"><p class="about-kicker">Открыто о главном</p><h2 id="about-package-heading">Сначала —<br><em>посмотрите.</em><br>Потом — к столу.</h2><p class="about-lead">Нам нравится, когда выбор понятен ещё у полки.</p><p>Через прозрачный контейнер можно рассмотреть продукт до покупки. На обечайке — название и информация о нём. А рядом — наша курочка. Привет, это мы!</p><a class="about-text-link" href="product-frikadelki-klassicheskie.html">Рассмотреть фрикадельки{arrow()}</a></div>
    <figure class="about-package-art"><span class="about-package-circle" aria-hidden="true"></span><img src="{pack}" width="800" height="800" alt="Фрикадельки «Классические» Новофермы: прозрачный контейнер и обечайка с фирменной курочкой" loading="lazy" decoding="async"><figcaption>Знакомые на полке.<br>Свои за столом.</figcaption></figure>
  </div>
</section>

<section class="about-finale about-shell" aria-labelledby="about-finale-heading">
  <div class="about-finale-art"><img src="{hen}" width="1254" height="1254" alt="" aria-hidden="true" loading="lazy" decoding="async"></div>
  <div class="about-finale-copy"><p class="about-kicker">Ну что, к столу?</p><h2 id="about-finale-heading">Теперь<br>будем <em>знакомы.</em></h2><p>Загляните в каталог. Там наверняка найдётся что-то для ваших.</p><div class="about-finale-actions"><a class="about-pill about-pill-dark" href="catalogue.html">Выбрать вкусное{arrow()}</a><a class="about-text-link" href="partners.html">Стать партнёром{arrow()}</a></div></div>
</section>'''
