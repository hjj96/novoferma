require('../../output/concept/loading-physics.js');
const sizes = [[1440,900],[390,844],[844,390]];
for (const [width,height] of sizes) {
  const world = new NovofermaPile(width,height);
  const then = performance.now();
  let maxOverlap = 0, maxAt = 0;
  for (let frame = 0; frame < 240; frame++) {
    world.step(1/60);
    let overlap = 0;
    for (let i=0;i<world.bodies.length;i++) for(let j=i+1;j<world.bodies.length;j++) {
      const a=world.bodies[i],b=world.bodies[j];
      if(a.y+a.r<0&&b.y+b.r<0) continue;
      const ratio = Math.max(0,(a.r+b.r-Math.hypot(a.x-b.x,a.y-b.y))/(a.r+b.r));
      overlap = Math.max(overlap,ratio);
    }
    if(overlap>maxOverlap){maxOverlap=overlap;maxAt=world.elapsed;}
    if([30,60,120,180,210].includes(frame)) console.log({width,height,time:+world.elapsed.toFixed(2),count:world.bodies.length,overlap:+overlap.toFixed(5),top:+Math.min(...world.bodies.map(b=>b.y+b.r)).toFixed(1)});
    if(world.complete) break;
  }
  const tops = Array.from({length:12},(_,i)=>{ const x=(i+.5)*width/12;return Math.min(...world.bodies.filter(b=>Math.abs(b.x-x)<b.r).map(b=>b.y-Math.sqrt(b.r*b.r-(b.x-x)**2)));});
  console.log({width,height,duration:world.elapsed,total:world.total,maxOverlap,maxAt,topMin:Math.min(...tops),topMax:Math.max(...tops),ms:performance.now()-then});
}
