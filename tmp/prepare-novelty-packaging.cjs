// Align approved ImageGen packshots with the existing catalogue canvas.
const sharp = require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const fs = require('fs');
const crypto = require('crypto');
const research='output/research/novelty-packaging/';
const runtime='output/concept/assets/novelty-packaging/';
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
(async()=>{
  fs.mkdirSync(runtime,{recursive:true});
  const records=[];
  for(const [slug,name,copy] of [
    ['fibriki','Фибрики',['ФИБРИКИ','ФРИКАДЕЛЬКИ ИЗ КУРИЦЫ','С ПИЩЕВЫМИ ВОЛОКНАМИ','Белок + клетчатка']],
    ['lulia-mini','Люля мини',['ЛЮЛЯ МИНИ','КУРИНЫЕ КОЛБАСКИ','С ЗЕЛЕНЬЮ И ОВОЩАМИ']]
  ]){
    const native=research+slug+'-pack-v1.png';
    const prompt=research+slug+'-pack-v1-prompt.txt';
    const {data,info}=await sharp(native).ensureAlpha().raw().toBuffer({resolveWithObject:true});
    let x0=info.width,y0=info.height,x1=0,y1=0;
    for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if(data[(y*info.width+x)*4+3]>=64){x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);}
    const width=x1-x0+1,height=y1-y0+1,scale=Math.min(736/width,640/height),padding=6;
    const left=Math.max(0,x0-padding),top=Math.max(0,y0-padding),right=Math.min(info.width,x1+padding+1),bottom=Math.min(info.height,y1+padding+1);
    const sw=Math.round((right-left)*scale),sh=Math.round((bottom-top)*scale);
    const normalized=await sharp(native).extract({left,top,width:right-left,height:bottom-top}).resize(sw,sh).png().toBuffer();
    const target=runtime+slug+'-pack-v1.webp';
    await sharp({create:{width:800,height:800,channels:4,background:{r:0,g:0,b:0,alpha:0}}})
      .composite([{input:normalized,left:Math.round(400-sw/2),top:Math.round(390-sh/2)}]).webp({lossless:true,effort:6}).toFile(target);
    for(const [theme,background]of[['cream','#fff5e3'],['dark','#402111']]){
      await sharp(target).flatten({background}).png().toFile(research+slug+'-pack-v1-'+theme+'.png');
    }
    records.push({slug,name,file:'assets/novelty-packaging/'+slug+'-pack-v1.webp',kind:'User-requested concept of front packaging',tool:'Built-in ImageGen',date:'2026-10-16',native,prompt,copy,canvas:[800,800],hasAlpha:true,sha256:hash(target),factsNotProvided:['net weight','full ingredients','nutrition','storage/preparation','production barcode'],purpose:'Visual packaging concept in the existing Novoferma catalogue style; original references retained.'});
  }
  fs.writeFileSync(runtime+'provenance.json',JSON.stringify({records},null,2)+'\n');
  fs.writeFileSync(research+'prompts.json',JSON.stringify({tool:'Built-in ImageGen',prompts:records.map(r=>({asset:r.file,prompt:fs.readFileSync(r.prompt,'utf8').trim()}))},null,2)+'\n');
  const composition=[];
  for(let i=0;i<records.length;i++){
    const image=await sharp('output/concept/'+records[i].file).resize(700,700).png().toBuffer();
    composition.push({input:image,left:i*700,top:0});
  }
  await sharp({create:{width:1400,height:700,channels:3,background:'#fff5e3'}}).composite(composition).png().toFile(research+'two-packaging-concepts.png');
  console.log(JSON.stringify({count:records.length,files:records.map(r=>r.file)}));
})().catch(error=>{console.error(error);process.exit(1)});
