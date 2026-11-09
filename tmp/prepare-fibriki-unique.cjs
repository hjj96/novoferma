// Format generated artwork without changing its design or generated alpha.
const sharp = require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const fs = require('fs');
const root='output/research/fibriki-unique-v4/';
const runtime='output/concept/assets/novelty-packaging/';
const version=Number(process.argv[2]||6);
async function sheet(name,items,cell=440){
 const parts=[];
 for(let i=0;i<items.length;i++){
  const [label,path]=items[i];
  parts.push({input:await sharp(path).resize(cell,cell,{fit:'contain'}).png().toBuffer(),left:i*cell,top:36});
  const escaped=label.replaceAll('&','&amp;').replaceAll('<','&lt;');
  parts.push({input:Buffer.from(`<svg width="${cell}" height="36"><text x="16" y="25" font-family="Arial" font-size="17" fill="#402111">${escaped}</text></svg>`),left:i*cell,top:0});
 }
 await sharp({create:{width:cell*items.length,height:cell+36,channels:3,background:'#fff5e3'}}).composite(parts).png().toFile(root+name+'.png');
}
(async()=>{
 const native=root+`fibriki-pack-v${version}.png`;
 const {data,info}=await sharp(native).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 let x0=info.width,y0=info.height,x1=0,y1=0;
 for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if(data[(y*info.width+x)*4+3]>=64){x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);}
 const scale=Math.min(736/(x1-x0+1),640/(y1-y0+1)),pad=6;
 const left=Math.max(0,x0-pad),top=Math.max(0,y0-pad),right=Math.min(info.width,x1+pad+1),bottom=Math.min(info.height,y1+pad+1);
 const width=Math.round((right-left)*scale),height=Math.round((bottom-top)*scale);
 const im=await sharp(native).extract({left,top,width:right-left,height:bottom-top}).resize(width,height).png().toBuffer();
 const output=runtime+`fibriki-pack-v${version}.webp`;
 await sharp({create:{width:800,height:800,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).composite([{input:im,left:Math.round(400-width/2),top:Math.round(390-height/2)}]).webp({lossless:true,effort:6}).toFile(output);
 for(const [theme,background]of[['cream','#fff5e3'],['dark','#402111']])await sharp(output).flatten({background}).png().toFile(root+`fibriki-pack-v${version}-${theme}.png`);
 const b='output/concept/assets/';
 await sheet('fibriki-before-after',[
  ['Фрикадельки — существующая линейка',b+'catalogue-clean-v2/frikadelki-klassicheskie.webp'],
  ['Фибрики — прежняя версия',b+'novelty-packaging/fibriki-pack-v3.webp'],
  ['Фибрики — новая версия',output]
 ]);
 await sheet('family-lineup',[
  ['Стрипсы',b+'catalogue-clean-v2/stripsy.webp'],
  ['Фрикадельки',b+'catalogue-clean-v2/frikadelki-klassicheskie.webp'],
  ['Фибрики',output],
  ['Биточки',b+'catalogue-clean-v2/bitochki-kurinye-s-ovoshchami.webp'],
  ['Люля мини',b+'novelty-packaging/lulia-mini-pack-v2.webp']
 ]);
 const products=JSON.parse(fs.readFileSync('output/concept/products.json'));
 const items=products.map(p=>[p.displayName,b+`catalogue-clean-v2/${p.slug}.webp`]).concat([['Фибрики',output],['Люля мини',b+'novelty-packaging/lulia-mini-pack-v2.webp']]);
 const grid=[];
 for(let i=0;i<items.length;i++){
  const [label,path]=items[i],x=(i%4)*400,y=Math.floor(i/4)*425;
  grid.push({input:await sharp(path).resize(400,400).png().toBuffer(),left:x,top:y+25});
  grid.push({input:Buffer.from(`<svg width="400" height="25"><text x="12" y="20" font-family="Arial" font-size="15" fill="#402111">${label.replaceAll('&','&amp;')}</text></svg>`),left:x,top:y});
 }
 await sharp({create:{width:1600,height:1700,channels:3,background:'#fff5e3'}}).composite(grid).png().toFile(root+'all-sixteen-packages.png');
 console.log(JSON.stringify({runtime:output,native,nativeCanvas:[info.width,info.height],subjectBounds:{x0,y0,x1,y1},runtimeCanvas:[800,800]}));
})().catch(error=>{console.error(error);process.exit(1)});
