const sharp=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const fs=require('fs');
const research='output/research/novelty-packaging-v2/',runtime='output/concept/assets/novelty-packaging/';
async function normalize(slug,revision=2){
 const source=research+slug+'-pack-v'+revision+'.png';if(!fs.existsSync(source))return;
 const {data,info}=await sharp(source).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 let x0=info.width,y0=info.height,x1=0,y1=0;
 for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if(data[(y*info.width+x)*4+3]>=64){x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);}
 const width=x1-x0+1,height=y1-y0+1,scale=Math.min(736/width,640/height),pad=6;
 const left=Math.max(0,x0-pad),top=Math.max(0,y0-pad),right=Math.min(info.width,x1+pad+1),bottom=Math.min(info.height,y1+pad+1);
 const sw=Math.round((right-left)*scale),sh=Math.round((bottom-top)*scale);
 const im=await sharp(source).extract({left,top,width:right-left,height:bottom-top}).resize(sw,sh).png().toBuffer();
 await sharp({create:{width:800,height:800,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).composite([{input:im,left:Math.round(400-sw/2),top:Math.round(390-sh/2)}]).webp({lossless:true,effort:6}).toFile(runtime+slug+'-pack-v'+revision+'.webp');
 for(const [theme,color]of[['cream','#fff5e3'],['dark','#402111']])await sharp(runtime+slug+'-pack-v'+revision+'.webp').flatten({background:color}).png().toFile(research+slug+'-pack-v'+revision+'-'+theme+'.png');
}
async function sheet(name,items){
 const pieces=[];
 for(let i=0;i<items.length;i++){
  const [label,file]=items[i];const im=await sharp(file).resize(500,500).png().toBuffer();
  const text=Buffer.from('<svg width="500" height="40"><text x="18" y="28" font-family="Arial" font-size="18" fill="#402111">'+label+'</text></svg>');
  pieces.push({input:im,left:i*500,top:40},{input:text,left:i*500,top:0});
 }
 await sharp({create:{width:items.length*500,height:540,channels:3,background:'#fff5e3'}}).composite(pieces).png().toFile(research+name+'.png');
}
(async()=>{
 await normalize('fibriki',2);
 await normalize('fibriki',3);
 await normalize('lulia-mini',2);
 const b='output/concept/assets/';
 await sheet('fibriki-in-lineup',[
  ['Котлеты',b+'catalogue-clean-v2/kotlety-po-domashnemu.webp'],
  ['Фрикадельки — эталон',b+'catalogue-clean-v2/frikadelki-klassicheskie.webp'],
  ['Фибрики — первая версия',b+'novelty-packaging/fibriki-pack-v1.webp'],
  ['Фибрики — новая версия',b+'novelty-packaging/fibriki-pack-v3.webp'],
  ['Ёжики',b+'catalogue-clean-v2/ezhiki-iz-tsyplenka-s-risom.webp']]);
 if(fs.existsSync(b+'novelty-packaging/lulia-mini-pack-v2.webp'))await sheet('final-family-lineup',[
  ['Котлеты',b+'catalogue-clean-v2/kotlety-po-domashnemu.webp'],
  ['Фрикадельки',b+'catalogue-clean-v2/frikadelki-klassicheskie.webp'],
  ['Фибрики',b+'novelty-packaging/fibriki-pack-v3.webp'],
  ['Люля мини',b+'novelty-packaging/lulia-mini-pack-v2.webp'],
  ['Биточки',b+'catalogue-clean-v2/bitochki-kurinye-s-ovoshchami.webp']]);
 console.log('Prepared current v2 assets and comparison sheets.');
})().catch(e=>{console.error(e);process.exit(1)});
