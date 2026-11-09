from pathlib import Path
R=Path(__file__).resolve().parent
base=(R.parent/'build_packaging.py').read_text()
base=base.replace("logo=ROOT.parent/'concept/assets/logo-reference.webp'", "logo=ROOT.parent.parent/'concept/assets/logo-reference.webp'")
base=base.replace("front+=text('ПОПСЫ',900,485,315,anchor='middle',family='Georgia',extra='letter-spacing=\"-8\"')", "front+=text('ПОПСЫ',900,425,280,anchor='middle',family='Baskerville',extra='textLength=\"1320\" lengthAdjust=\"spacing\"')")
base=base.replace("front+=text('МИНИ-НАГГЕТСЫ ИЗ КУРИЦЫ',900,580,55,anchor='middle',weight='bold',extra='letter-spacing=\"4\"')", "front+=text('МИНИ-НАГГЕТСЫ ИЗ КУРИЦЫ',900,520,41,anchor='middle',extra='letter-spacing=\"5\"')")
base=base.replace("front+=text('В ХРУСТЯЩЕЙ ПАНИРОВКЕ',900,650,41,anchor='middle',weight='bold',extra='letter-spacing=\"3\"')", "front+=text('В ХРУСТЯЩЕЙ ПАНИРОВКЕ',900,580,35,anchor='middle',extra='letter-spacing=\"4\"')")
base=base.replace("front+=picture(ASSETS/'pops-food-cutout.png',110,720,860,650)\nfront+=picture(ASSETS/'pops-mascot.png',950,680,730,740)", '''front+="<svg x='90' y='650' width='1620' height='730' viewBox='0 0 1683 935'>"+picture(ASSETS/'pops-v3-rock-art.png',0,0,1683,935)+"</svg>"''')
base=base.replace('Дизайн-концепт', 'Дизайн-концепт, версия 3')
base=base.replace("family='Georgia'", "family='Baskerville'")
base=base.replace('Georgia и Arial', 'Baskerville Regular и Arial')
base=base.replace('Полный перечень незаполненных полей: ../product-brief.txt.', 'Перед печатью сверить производственные поля с утвержденными данными. Ведёрко — печатный сюжет подачи, не комплектующая retail-упаковки. Внешний вид версии 3 сверялся с оригинальными фото классического каталога.')
exec(compile(base,str(R/'build_packaging_v3.py'),'exec'),{'__file__':str(R/'build_packaging_v3.py'),'__name__':'__main__'})
