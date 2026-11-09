// Format and align ImageGen results; image content and alpha come from ImageGen.
const sharp = require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = process.cwd();
const site = path.join(root, 'output/concept');
const research = path.join(root, 'output/research/catalogue-edge-cleanup');
const out = path.join(site, 'assets/catalogue-clean-v2');
const products = JSON.parse(fs.readFileSync(path.join(site, 'site-manifest.json'))).products;
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const escapeXml = text => text.replaceAll('&','&amp;').replaceAll('<','&lt;');
function textSvg(text, width, height, dark) {
  return Buffer.from(`<svg width="${width}" height="${height}"><text x="10" y="20" font-family="Arial" font-size="12" fill="${dark?'#fff5e3':'#402111'}">${escapeXml(text)}</text></svg>`);
}
(async () => {
  fs.mkdirSync(out, {recursive:true});
  const records = [];
  for (const product of products) {
    const slug = product.id;
    const native = path.join(research, slug+'-clean-v2.png');
    const prompt = path.join(research, slug+'-clean-v2-prompt.txt');
    if (!fs.existsSync(native)||!fs.existsSync(prompt)) throw Error('Missing generation: '+slug);
    const {data,info} = await sharp(native).ensureAlpha().raw().toBuffer({resolveWithObject:true});
    let x0=info.width,y0=info.height,x1=0,y1=0;
    for(let y=0;y<info.height;y++) for(let x=0;x<info.width;x++) {
      if(data[(y*info.width+x)*4+3]>=64) {x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);}
    }
    const width=x1-x0+1,height=y1-y0+1;
    if(width<info.width*.5||height<info.height*.4) throw Error('Unexpected silhouette: '+slug);
    const padding=6;
    const left=Math.max(0,x0-padding),top=Math.max(0,y0-padding);
    const right=Math.min(info.width,x1+padding+1),bottom=Math.min(info.height,y1+padding+1);
    const scale=Math.min(736/width,640/height);
    const scaledWidth=Math.round((right-left)*scale),scaledHeight=Math.round((bottom-top)*scale);
    const cutout=await sharp(native).extract({left,top,width:right-left,height:bottom-top})
      .resize(scaledWidth,scaledHeight,{kernel:'lanczos3'}).png().toBuffer();
    const target=path.join(out,slug+'.webp');
    await sharp({create:{width:800,height:800,channels:4,background:{r:0,g:0,b:0,alpha:0}}})
      .composite([{input:cutout,left:Math.round(400-scaledWidth/2),top:Math.round(390-scaledHeight/2)}])
      .webp({lossless:true,effort:6}).toFile(target);
    const meta=await sharp(target).metadata();
    if(!meta.hasAlpha)throw Error('Missing alpha: '+slug);
    const composite = ['bitochki-kurinye-s-ovoshchami','ezhiki-iz-tsyplenka-s-risom'].includes(slug);
    const source='assets/catalogue-cutout/'+slug+(composite?'-front-v1':'')+'.webp';
    const editSource=composite?'output/research/catalogue-packshots/'+slug+'-front-v1.png':'output/concept/assets/catalogue/'+slug+'.webp';
    records.push({slug,file:'assets/catalogue-clean-v2/'+slug+'.webp',previousImage:source,
      kind:'Built-in ImageGen background and edge cleanup',native:path.relative(root,native),prompt:path.relative(root,prompt),
      editSource,editSourceSha256:hash(path.join(root,editSource)),previousSha256:hash(path.join(site,source)),sha256:hash(target),canvas:[800,800],
      alignment:{sourceAlphaBounds:[x0,y0,x1+1,y1+1],scale,bodyWidth:Math.round(width*scale),bodyHeight:Math.round(height*scale)}});
  }
  for (const [theme,background] of [['cream','#fff5e3'],['dark','#402111']]) {
    const dark=theme==='dark',full=[],edges=[];
    for(let i=0;i<products.length;i++) {
      const p=products[i],file=path.join(out,p.id+'.webp');
      const x=(i%4)*320,y=Math.floor(i/4)*346;
      const tile=await sharp(file).resize(310,310).flatten({background}).png().toBuffer();
      full.push({input:tile,left:x+5,top:y+28},{input:textSvg(p.name,320,28,dark),left:x,top:y});
      const row=Math.floor(i/2),productColumn=i%2;
      for(const [side,imageFile] of [[0,path.join(site,records[i].previousImage)],[1,file]]) {
        const edge=await sharp(imageFile).extract({left:100,top:540,width:600,height:215})
          .resize(390,140).flatten({background}).png().toBuffer();
        const ex=productColumn*800+side*400,ey=row*175;
        edges.push({input:edge,left:ex+5,top:ey+28},{input:textSvg(p.id+' '+(side?'AFTER':'BEFORE'),400,28,dark),left:ex,top:ey});
      }
    }
    await sharp({create:{width:1280,height:Math.ceil(products.length/4)*346,channels:3,background}}).composite(full).png().toFile(path.join(research,'all-clean-'+theme+'.png'));
    await sharp({create:{width:1600,height:Math.ceil(products.length/2)*175,channels:3,background}}).composite(edges).png().toFile(path.join(research,'lower-edges-'+theme+'.png'));
  }
  const provenance={date:'2026-10-16',tool:'Built-in ImageGen',operation:'Remove studio backdrop, ragged matte and baked cast shadow; retain complete translucent tray. Originals preserved.',records};
  fs.writeFileSync(path.join(out,'provenance.json'),JSON.stringify(provenance,null,2)+'\n');
  fs.writeFileSync(path.join(research,'prompts.json'),JSON.stringify({tool:provenance.tool,prompts:records.map(r=>({asset:r.file,prompt:fs.readFileSync(path.join(root,r.prompt),'utf8').trim()}))},null,2)+'\n');
  console.log(JSON.stringify({count:records.length,canvas:[800,800],alpha:true,files:records.map(r=>r.file)}));
})().catch(error=>{console.error(error);process.exit(1)});
