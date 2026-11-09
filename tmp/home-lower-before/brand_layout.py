"""Calm editorial layout for the shared footer and homepage business section."""


def render_footer(arrow):
    return f'''<footer class="site-footer nf-footer"><div class="nf-footer-inner">
<div class="nf-footer-top"><div class="nf-footer-brand"><a class="brand" href="index.html" aria-label="Новоферма — главная"><img src="assets/logo-reference.webp" width="342" height="64" alt="NOVOferma"></a><p>Для своих. Каждый день.</p></div>
<div class="nf-footer-contacts"><a href="mailto:info@novoferma.ru">info@novoferma.ru{arrow()}</a><a href="tel:+78129155454">+7 (812) 915-54-54</a></div></div>
<div class="nf-footer-bottom"><p>© 2026 ООО «НОВОФЕРМА»</p><nav aria-label="Навигация в подвале"><a href="catalogue.html">Продукция</a><a href="about.html">О нас</a><a href="partners.html">Партнёрам</a><a href="contacts.html">Контакты</a></nav><span>Санкт-Петербург</span></div>
</div></footer>'''


def render_business(arrow):
    return f'''<section class="nf-business" id="cooperation" aria-labelledby="cooperation-heading"><div class="wrap nf-business-inner">
<div><p class="eyebrow home-kicker">Партнёрам</p><h2 id="cooperation-heading">Для вашей полки.<br>Для вашего меню.</h2></div>
<div class="nf-business-copy"><p>Продукты из курицы и индейки для магазинов, кафе и ресторанов. Выпускаем продукцию и под вашей торговой маркой.</p><a class="nf-editorial-link" href="partners.html">Форматы сотрудничества{arrow()}</a></div>
</div></section>'''
