const sharp = require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const fs = require('fs');
const dir = 'output/research/catalogue-grid-16/';
const assets = 'output/concept/assets/';
const version = process.argv[2] || '9';
const source = dir + `fibriki-pack-v${version}.png`;
const out = assets + `novelty-packaging/fibriki-pack-v${version}.webp`;
async function sheet(name, list, cell = 440) {
 const pieces = [];
 for (let i = 0; i < list.length; i++) {
  const [label,file] = list[i];
  pieces.push({input:await sharp(file).resize(cell,cell).png().toBuffer(),left:i*cell,top:36});
  pieces.push({input:Buffer.from(`<svg width="${cell}" height="36"><text x="16" y="25" font-family="Arial" font-size="17" fill="#402111">${label}</text></svg>`),left:i*cell,top:0});
 }
 await sharp({create:{width:cell*list.length,height:cell+36,channels:3,background:'#fff5e3'}}).composite(pieces).png().toFile(dir+name+'.png');
}
(async()=>{
 const {data,info} = await sharp(source).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 let x0=info.width,y0=info.height,x1=0,y1=0;
 for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if(data[(y*info.width+x)*4+3]>=64){x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);}
 const scale=Math.min(736/(x1-x0+1),640/(y1-y0+1)),pad=6;
 const left=Math.max(0,x0-pad),top=Math.max(0,y0-pad),right=Math.min(info.width,x1+pad+1),bottom=Math.min(info.height,y1+pad+1);
 const width=Math.round((right-left)*scale),height=Math.round((bottom-top)*scale);
 const im=await sharp(source).extract({left,top,width:right-left,height:bottom-top}).resize(width,height).png().toBuffer();
 await sharp({create:{width:800,height:800,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).composite([{input:im,left:Math.round(400-width/2),top:Math.round(390-height/2)}]).webp({lossless:true,effort:6}).toFile(out);
 for(const [theme,background]of[['cream','#fff5e3'],['dark','#402111']])await sharp(out).flatten({background}).png().toFile(dir+`fibriki-pack-v${version}-${theme}.png`);
 await sheet(`family-lineup-v${version}`,[['Стрипсы',assets+'catalogue-clean-v2/stripsy.webp'],['Фрикадельки',assets+'catalogue-clean-v2/frikadelki-klassicheskie.webp'],['Фибрики',out],['Котлеты по-домашнему',assets+'catalogue-clean-v2/kotlety-po-domashnemu.webp'],['Люля мини',assets+'novelty-packaging/lulia-mini-pack-v3.webp']]);
 await sheet(`fibriki-before-after-v${version}`,[['До',assets+'novelty-packaging/fibriki-pack-v8.webp'],['После',out]],700);
 console.log(JSON.stringify({out,source,native:{width:info.width,height:info.height},alphaBounds:{x0,y0,x1,y1},scale}));
})().catch(e=>{console.error(e);process.exit(1)});
