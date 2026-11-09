from pathlib import Path
R=Path(__file__).resolve().parent
base=(R.parent/'build_packaging.py').read_text()
base=base.replace("ROOT=Path(__file__).resolve().parent", "ROOT=Path(__file__).resolve().parent")
base=base.replace("logo=ROOT.parent/'concept/assets/logo-reference.webp'", "logo=ROOT.parent.parent/'concept/assets/logo-reference.webp'")
base=base.replace("front+=picture(ASSETS/'pops-food-cutout.png',110,720,860,650)\nfront+=picture(ASSETS/'pops-mascot.png',950,680,730,740)", '''front+="<svg x='240' y='680' width='1320' height='735' viewBox='20 140 1220 960'>"+picture(ASSETS/'pops-bucket-mascot-v2.png',0,0,1254,1254)+"</svg>"''')
base=base.replace('Дизайн-концепт', 'Дизайн-концепт, версия 2')
base=base.replace('Полный перечень незаполненных полей: ../product-brief.txt.', 'Полный перечень незаполненных полей: product-brief.txt из первого комплекта. Ведёрко является образом подачи на этикетке; физическая тара — лоток с рукавом.')
exec(compile(base,str(R/'build_packaging_v2.py'),'exec'),{'__file__':str(R/'build_packaging_v2.py'),'__name__':'__main__'})
