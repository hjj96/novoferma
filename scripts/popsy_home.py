"""Approved single-product homepage poster; all UI copy stays live."""


def render_popsy_home(asset_url, icon):
    def source(name):
        return asset_url('assets/popsy-home/' + name)

    pack_set = ', '.join(f'{source(name)} {width}w' for name, width in
                         [('pack-420.webp', 420), ('pack-720.webp', 720), ('pack.webp', 1254)])
    food_set = ', '.join(f'{source(name)} {width}w' for name, width in
                         [('food-420.webp', 420), ('food-600.webp', 600), ('food.webp', 1100)])
    return f'''<section class="popsy-home-hero" data-popsy-hero aria-labelledby="popsy-home-title"><div class="popsy-home-inner">
<h1 class="popsy-home-title" id="popsy-home-title">Попсы</h1>
<p class="popsy-home-note"><span>Хрусти</span> <span>в своём ритме</span></p>
<div class="popsy-home-art">
<div class="popsy-home-pack-layer"><img class="popsy-home-pack" src="{source('pack.webp')}" srcset="{pack_set}" sizes="(max-width: 699px) 87vw, (max-width: 1099px) 57vw, 54vw" width="1254" height="1254" alt="Упаковка Попсов Новофермы — мини-наггетсов из курицы" fetchpriority="high" decoding="async"></div>
<div class="popsy-home-food-layer"><img class="popsy-home-food" src="{source('food.webp')}" srcset="{food_set}" sizes="(max-width: 699px) 58vw, (max-width: 1099px) 43vw, 36vw" width="1100" height="825" alt="Готовые Попсы в золотистой панировке и кусочек в разрезе" decoding="async"></div>
</div>
<div class="popsy-home-bottom"><p class="popsy-home-description">Мини-наггетсы из курицы<br class="popsy-home-mobile-break"> в хрустящей панировке.</p><a class="button popsy-home-cta" href="product-popsy.html"><span>О Попсах</span>{icon('arrow-right','ui-icon icon-arrow')}</a></div>
</div></section>'''
