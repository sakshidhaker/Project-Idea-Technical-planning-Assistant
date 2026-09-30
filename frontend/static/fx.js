/* Animated neural-network background (landing, login, signup) */
(function(){
  const c=document.getElementById('fx'); if(!c||matchMedia('(prefers-reduced-motion:reduce)').matches) return;
  const x=c.getContext('2d'); let w,h,pts=[];
  function size(){w=c.width=innerWidth;h=c.height=innerHeight;pts=Array.from({length:Math.min(80,Math.floor(w*h/16000))},()=>({x:Math.random()*w,y:Math.random()*h,vx:(Math.random()-.5)*.5,vy:(Math.random()-.5)*.5}))}
  addEventListener('resize',size); size();
  const m={x:-999,y:-999}; addEventListener('pointermove',e=>{m.x=e.clientX;m.y=e.clientY});
  (function draw(){
    x.clearRect(0,0,w,h);
    const dark=document.documentElement.dataset.theme==='dark', rgb=dark?'140,150,255':'90,80,220';
    for(const p of pts){p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>w)p.vx*=-1;if(p.y<0||p.y>h)p.vy*=-1;
      x.fillStyle=`rgba(${rgb},.7)`;x.beginPath();x.arc(p.x,p.y,1.8,0,7);x.fill();}
    for(let i=0;i<pts.length;i++)for(let j=i+1;j<pts.length;j++){
      const a=pts[i],b=pts[j],d=Math.hypot(a.x-b.x,a.y-b.y);
      if(d<140){x.strokeStyle=`rgba(${rgb},${.28*(1-d/140)})`;x.beginPath();x.moveTo(a.x,a.y);x.lineTo(b.x,b.y);x.stroke();}}
    for(const p of pts){const d=Math.hypot(p.x-m.x,p.y-m.y);if(d<170){x.strokeStyle=`rgba(6,182,212,${.5*(1-d/170)})`;x.beginPath();x.moveTo(p.x,p.y);x.lineTo(m.x,m.y);x.stroke();}}
    requestAnimationFrame(draw);
  })();
})();
