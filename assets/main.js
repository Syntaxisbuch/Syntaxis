
document.addEventListener('DOMContentLoaded', function(){
  const revealEls = document.querySelectorAll('.reveal');
  const io = new IntersectionObserver((entries)=>{
    entries.forEach(e=>{
      if(e.isIntersecting){ e.target.classList.add('visible'); io.unobserve(e.target); }
    });
  }, {threshold:0.15});
  revealEls.forEach(el=>io.observe(el));

  const canvas = document.getElementById('bgCanvas');
  if(canvas){
    const ctx = canvas.getContext('2d');
    function resize(){ canvas.width = canvas.offsetWidth; canvas.height = canvas.offsetHeight; }
    resize();
    window.addEventListener('resize', resize);
    const mode = canvas.dataset.mode || 'stars';
    let particles = [];
    const count = mode === 'rain' ? 120 : 140;
    for(let i=0;i<count;i++){
      if(mode === 'rain'){
        particles.push({x:Math.random()*canvas.width, y:Math.random()*canvas.height, l:10+Math.random()*20, s:4+Math.random()*6, o:0.1+Math.random()*0.3});
      } else if(mode === 'dust'){
        particles.push({x:Math.random()*canvas.width, y:Math.random()*canvas.height, r:0.5+Math.random()*1.5, dx:(Math.random()-0.5)*0.15, dy:(Math.random()-0.5)*0.15, o:0.2+Math.random()*0.5});
      } else {
        particles.push({x:Math.random()*canvas.width, y:Math.random()*canvas.height, r:0.4+Math.random()*1.4, o:Math.random(), tw:0.005+Math.random()*0.02});
      }
    }
    function draw(){
      ctx.clearRect(0,0,canvas.width,canvas.height);
      if(mode==='rain'){
        ctx.strokeStyle = 'rgba(150,180,220,0.5)';
        particles.forEach(p=>{
          ctx.globalAlpha = p.o;
          ctx.beginPath();
          ctx.moveTo(p.x,p.y);
          ctx.lineTo(p.x-2,p.y+p.l);
          ctx.stroke();
          p.y += p.s;
          if(p.y > canvas.height){ p.y = -20; p.x = Math.random()*canvas.width; }
        });
      } else if(mode==='dust'){
        ctx.fillStyle = '#c98a3d';
        particles.forEach(p=>{
          ctx.globalAlpha = p.o;
          ctx.beginPath();
          ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
          ctx.fill();
          p.x += p.dx; p.y += p.dy;
          if(p.x<0)p.x=canvas.width; if(p.x>canvas.width)p.x=0;
          if(p.y<0)p.y=canvas.height; if(p.y>canvas.height)p.y=0;
        });
      } else {
        ctx.fillStyle = '#ffffff';
        particles.forEach(p=>{
          p.o += p.tw;
          const alpha = 0.3 + Math.abs(Math.sin(p.o));
          ctx.globalAlpha = alpha;
          ctx.beginPath();
          ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
          ctx.fill();
        });
      }
      ctx.globalAlpha = 1;
      requestAnimationFrame(draw);
    }
    draw();
  }
});
