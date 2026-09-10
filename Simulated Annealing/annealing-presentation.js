// Presentation uses the same simulation state throughout; no decorative RNG,
// independent metric tween, or frame-dependent particle motion is introduced.
const VIEW = Object.freeze({
  hudHz: 15,
  phaseNames: ['HIGH-T EXPLORATION', 'COOLING', 'ORDERING', 'LOW-T STATE'],
  thermalHot: [255, 184, 108],
  thermalMid: [189, 147, 249],
  thermalCold: [139, 233, 253],
  trailSeconds: 0.115,
  trailMaxLength: 30,
  gridSpacing: 60,
  bridgeFadeSeconds: 0.65,
  bridgeLastSeconds: 1,
  phasePulseSeconds: 0.65
});

/** Fixed world coordinates are uniformly mapped, never stretched on resize.
 * Moving a window between displays also rebuilds its physical-pixel backing. */
class CanvasManager {
  constructor(canvas) {
    this.canvas = canvas;
    this.context = canvas.getContext('2d');
    this.width = 1;
    this.height = 1;
    this.dpr = 1;
    this.observer = new ResizeObserver(() => this.resize());
    this.observer.observe(canvas);
    this.resize();
  }
  resize() {
    const rect = this.canvas.getBoundingClientRect();
    this.width = Math.max(1, rect.width);
    this.height = Math.max(1, rect.height);
    this.dpr = Math.max(1, window.devicePixelRatio || 1);
    this.canvas.width = Math.round(this.width * this.dpr);
    this.canvas.height = Math.round(this.height * this.dpr);
    this.context.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
  }
  clear() {
    if (this.dpr !== Math.max(1, window.devicePixelRatio || 1)) this.resize();
    this.context.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    this.context.clearRect(0, 0, this.width, this.height);
  }
}

class Renderer {
  constructor(canvas, system) {
    this.surface = new CanvasManager(canvas);
    this.system = system;
    this.neighbors = [];
    const particles = system.particles;
    const neighborRadius2 = Math.pow(system.spacing * 1.05, 2);
    // Connectivity only determines which near-neighbor pairs may be shown.
    // Every endpoint is an actual particle, never an independently drawn site.
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].tx - particles[j].tx;
        const dy = particles[i].ty - particles[j].ty;
        if (dx * dx + dy * dy < neighborRadius2) this.neighbors.push([i, j]);
      }
    }
  }
  draw() {
    const surface = this.surface, ctx = surface.context, s = this.system;
    surface.clear();
    const scale = Math.min(surface.width / s.config.worldWidth, surface.height / s.config.worldHeight);
    const offsetX = (surface.width - s.config.worldWidth * scale) / 2;
    const offsetY = (surface.height - s.config.worldHeight * scale) / 2;
    ctx.translate(offsetX, offsetY);
    ctx.scale(scale, scale);
    const b = s.bounds;

    // A faint instrument grid, unrelated to the triangular destination lattice.
    ctx.lineWidth = 0.7 / scale;
    ctx.strokeStyle = 'rgba(142, 166, 194, 0.045)';
    ctx.beginPath();
    for (let x = b.left; x <= b.right; x += VIEW.gridSpacing) {
      ctx.moveTo(x, b.top); ctx.lineTo(x, b.bottom);
    }
    for (let y = b.top; y <= b.bottom; y += VIEW.gridSpacing) {
      ctx.moveTo(b.left, y); ctx.lineTo(b.right, y);
    }
    ctx.stroke();
    ctx.strokeStyle = 'rgba(153, 181, 210, 0.13)';
    ctx.strokeRect(b.left, b.top, b.right - b.left, b.bottom - b.top);
    ctx.strokeStyle = 'rgba(151, 190, 210, 0.34)';
    ctx.lineWidth = 1 / scale;
    ctx.beginPath();
    const arm = 12;
    ctx.moveTo(b.left, b.top + arm); ctx.lineTo(b.left, b.top); ctx.lineTo(b.left + arm, b.top);
    ctx.moveTo(b.right - arm, b.top); ctx.lineTo(b.right, b.top); ctx.lineTo(b.right, b.top + arm);
    ctx.moveTo(b.right, b.bottom - arm); ctx.lineTo(b.right, b.bottom); ctx.lineTo(b.right - arm, b.bottom);
    ctx.moveTo(b.left + arm, b.bottom); ctx.lineTo(b.left, b.bottom); ctx.lineTo(b.left, b.bottom - arm);
    ctx.stroke();

    ctx.save();
    ctx.beginPath(); ctx.rect(b.left, b.top, b.right - b.left, b.bottom - b.top); ctx.clip();
    const particles = s.particles;
    const coherence = smoothstep((s.order - 0.42) / 0.5);
    if (coherence > 0) {
      ctx.lineWidth = 0.85 / scale;
      for (let index = 0; index < this.neighbors.length; index++) {
        const pair = this.neighbors[index], a = particles[pair[0]], z = particles[pair[1]];
        const dx = a.x - z.x, dy = a.y - z.y;
        const mismatch = Math.abs(Math.hypot(dx, dy) / s.spacing - 1);
        const proximity = clamp(1 - mismatch / 0.22);
        if (proximity > 0) {
          ctx.strokeStyle = `rgba(139, 233, 253, ${0.14 * coherence * proximity})`;
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(z.x, z.y); ctx.stroke();
        }
      }
    }
    const thermalFraction = clamp((s.temperature - s.config.temperatureMin) / (s.config.temperatureMax - s.config.temperatureMin));
    const radius = s.config.particleRadius;
    if (thermalFraction > 0.002) {
      // Short velocity-directed exposures. Both their extent and opacity are
      // derived from the current velocity and the actual controlled temperature.
      ctx.lineCap = 'round';
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        const speed = Math.hypot(p.vx, p.vy);
        if (speed < 1e-9) continue;
        const length = Math.min(VIEW.trailMaxLength, speed * VIEW.trailSeconds) * Math.sqrt(thermalFraction);
        const dx = p.vx / speed * length, dy = p.vy / speed * length;
        ctx.strokeStyle = `rgba(139, 233, 253, ${0.08 * thermalFraction})`;
        ctx.lineWidth = 3.1;
        ctx.beginPath(); ctx.moveTo(p.x - dx, p.y - dy); ctx.lineTo(p.x, p.y); ctx.stroke();
        ctx.strokeStyle = `rgba(180, 233, 246, ${0.27 * thermalFraction})`;
        ctx.lineWidth = 1.25;
        ctx.beginPath(); ctx.moveTo(p.x - dx * 0.64, p.y - dy * 0.64); ctx.lineTo(p.x, p.y); ctx.stroke();
      }
    }
    // Batched translucent discs supply a restrained halo without shadowBlur,
    // per-particle gradients, images, or expensive whole-canvas blur passes.
    ctx.fillStyle = 'rgba(139, 233, 253, 0.035)';
    ctx.beginPath();
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i]; ctx.moveTo(p.x + radius * 3, p.y); ctx.arc(p.x, p.y, radius * 3, 0, 2 * Math.PI);
    }
    ctx.fill();
    ctx.fillStyle = 'rgba(139, 233, 253, 0.09)';
    ctx.beginPath();
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i]; ctx.moveTo(p.x + radius * 1.8, p.y); ctx.arc(p.x, p.y, radius * 1.8, 0, 2 * Math.PI);
    }
    ctx.fill();
    ctx.fillStyle = '#a5dfeb';
    ctx.beginPath();
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i]; ctx.moveTo(p.x + radius, p.y); ctx.arc(p.x, p.y, radius, 0, 2 * Math.PI);
    }
    ctx.fill();
    ctx.fillStyle = '#effafd';
    ctx.beginPath();
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i]; ctx.moveTo(p.x + radius * 0.58, p.y); ctx.arc(p.x, p.y, radius * 0.58, 0, 2 * Math.PI);
    }
    ctx.fill();
    ctx.restore();
  }
}

class EnergyChart {
  constructor(canvas) { this.surface = new CanvasManager(canvas); }
  draw(system) {
    const surface = this.surface, ctx = surface.context;
    surface.clear();
    const w = surface.width, h = surface.height;
    const history = system.history;
    // Never clip a high-temperature increase or force a descending envelope.
    let ymax = 1.2;
    for (let i = 0; i < history.length; i++) ymax = Math.max(ymax, history[i].energy * 1.12);
    const left = 2, top = 4, width = w - 4, height = h - 8;
    ctx.lineWidth = 1;
    ctx.strokeStyle = '#283040';
    ctx.beginPath();
    ctx.moveTo(left, top + height); ctx.lineTo(left + width, top + height);
    ctx.stroke();
    ctx.setLineDash([2, 5]);
    ctx.strokeStyle = '#252d3c';
    ctx.beginPath(); ctx.moveTo(left, top + height * 0.5); ctx.lineTo(left + width, top + height * 0.5); ctx.stroke();
    ctx.setLineDash([]);
    ctx.strokeStyle = '#bd93f9';
    ctx.lineWidth = 1.5;
    ctx.lineJoin = 'round';
    ctx.beginPath();
    for (let i = 0; i < history.length; i++) {
      const point = history[i];
      const x = left + width * point.time / system.config.duration;
      const y = top + height * (1 - point.energy / ymax);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();
    const last = history[history.length - 1];
    if (last) {
      const x = left + width * last.time / system.config.duration;
      const y = top + height * (1 - last.energy / ymax);
      ctx.fillStyle = '#d7b9ff'; ctx.beginPath(); ctx.arc(x, y, 2, 0, Math.PI * 2); ctx.fill();
    }
  }
}

class HUD {
  constructor(system) {
    this.system = system;
    this.nodes = {};
    const ids = ['temperature', 'energy', 'order', 'time', 'time-total', 'phase', 'phase-card',
      'temperature-fill', 'temperature-marker', 'temperature-meter', 'order-fill', 'order-meter',
      'timeline', 'timeline-progress', 'timeline-needle', 'timeline-labels', 'bridge', 'announcement'];
    for (const id of ids) this.nodes[id] = document.getElementById(id);
    this.chart = new EnergyChart(document.getElementById('energy-plot'));
    this.lastTime = -Infinity;
    this.lastPhase = -1;
    const c = system.config;
    this.nodes['time-total'].textContent = ` / ${c.duration.toFixed(1)} s`;
    this.nodes.timeline.setAttribute('aria-valuemax', c.duration);
    this.nodes.timeline.setAttribute('aria-label', `Progresso da sequência de ${c.duration} segundos`);
    document.getElementById('chart-duration').textContent = `0 — ${c.duration} s`;
    document.getElementById('particle-count').textContent = `N = ${c.particleCount}`;
    document.getElementById('particles').setAttribute('aria-label', `${c.particleCount} partículas: a agitação diminui e uma rede triangular emerge durante o resfriamento.`);
    const boundaries = [c.coolingStart, c.coolingEnd, c.orderingEnd];
    const ticks = ['tick-cooling', 'tick-ordering', 'tick-hold'];
    for (let i = 0; i < ticks.length; i++) document.getElementById(ticks[i]).style.left = `${boundaries[i] / c.duration * 100}%`;
    this.nodes['timeline-labels'].style.gridTemplateColumns = `${c.coolingStart}fr ${c.coolingEnd - c.coolingStart}fr ${c.orderingEnd - c.coolingEnd}fr ${c.duration - c.orderingEnd}fr`;
  }
  temperatureColor(value) {
    const low = value < 0.5;
    const from = low ? VIEW.thermalCold : VIEW.thermalMid;
    const to = low ? VIEW.thermalMid : VIEW.thermalHot;
    const weight = low ? value * 2 : (value - 0.5) * 2;
    return `rgb(${Math.round(from[0] + (to[0] - from[0]) * weight)}, ${Math.round(from[1] + (to[1] - from[1]) * weight)}, ${Math.round(from[2] + (to[2] - from[2]) * weight)})`;
  }
  update(force = false) {
    const s = this.system, n = this.nodes;
    if (!force && s.time >= this.lastTime && s.time - this.lastTime < 1 / VIEW.hudHz && this.lastPhase === s.phase) return;
    this.lastTime = s.time;
    const color = this.temperatureColor(s.temperature);
    document.documentElement.style.setProperty('--thermal', color);
    // Exact sampled values, rounded only for typography. Scientific notation
    // retains a nonzero small energy; interpolation would detach E/Q from state.
    n.temperature.textContent = s.temperature.toFixed(3);
    n.energy.textContent = s.energy >= 0.001 ? s.energy.toFixed(3) : s.energy.toExponential(2).replace('e-', 'e−');
    n.order.textContent = s.order.toFixed(3);
    n.time.textContent = s.time.toFixed(1).padStart(4, '0');
    n['temperature-fill'].style.transform = `scaleX(${s.temperature})`;
    n['temperature-marker'].style.left = `${s.temperature * 100}%`;
    n['temperature-meter'].setAttribute('aria-valuenow', s.temperature.toFixed(6));
    n['order-fill'].style.transform = `scaleX(${s.order})`;
    n['order-meter'].setAttribute('aria-valuenow', s.order.toFixed(6));
    n.timeline.setAttribute('aria-valuenow', s.time.toFixed(3));
    n.timeline.setAttribute('aria-valuetext', `${s.time.toFixed(1)} de ${s.config.duration.toFixed(1)} segundos; ${VIEW.phaseNames[s.phase]}`);
    this.chart.draw(s);
    if (s.phase !== this.lastPhase) {
      this.lastPhase = s.phase;
      n.phase.textContent = VIEW.phaseNames[s.phase];
      const labels = n['timeline-labels'].children;
      for (let i = 0; i < labels.length; i++) labels[i].classList.toggle('active', i === s.phase);
      n.announcement.textContent = `Fase ${s.phase + 1}: ${VIEW.phaseNames[s.phase]}.`;
    }
  }
  animate() {
    const s = this.system, n = this.nodes;
    // These are camera-overlay effects, all tied to simulation time so pause,
    // restart, and capture preserve the exact same composited sequence.
    n['timeline-progress'].style.transform = `scaleX(${s.progress})`;
    n['timeline-needle'].style.left = `${s.progress * 100}%`;
    const starts = [0, s.config.coolingStart, s.config.coolingEnd, s.config.orderingEnd];
    const phaseAge = s.time - starts[s.phase];
    const pulse = s.phase > 0 ? 0.055 * Math.pow(1 - clamp(phaseAge / VIEW.phasePulseSeconds), 2) : 0;
    n['phase-card'].style.setProperty('--phase-pulse', pulse);
    const bridge = smoothstep((s.time - (s.config.duration - VIEW.bridgeLastSeconds)) / VIEW.bridgeFadeSeconds);
    n.bridge.style.opacity = bridge;
    n.bridge.setAttribute('aria-hidden', bridge === 0 ? 'true' : 'false');
  }
}

/** Render timestamps never enter the stochastic dynamics. Pausing keeps the
 * residual accumulator; hiding the tab freezes the clock instead of fast-forwarding. */
class Timeline {
  constructor(system) {
    this.system = system;
    this.playing = false;
    this.accumulator = 0;
    this.lastTimestamp = null;
  }
  play() { this.playing = true; this.lastTimestamp = null; }
  pause() { this.playing = false; this.lastTimestamp = null; }
  restart() { this.system.reset(); this.accumulator = 0; this.lastTimestamp = null; }
  advance(timestamp) {
    if (!this.playing) return;
    if (this.lastTimestamp === null) { this.lastTimestamp = timestamp; return; }
    const delta = clamp((timestamp - this.lastTimestamp) / 1000, 0, this.system.config.maxFrameDelta);
    this.lastTimestamp = timestamp;
    this.accumulator += delta;
    const dt = this.system.config.physicsDt;
    while (this.accumulator + 1e-10 >= dt && this.system.time < this.system.config.duration) {
      this.system.step();
      this.accumulator = Math.max(0, this.accumulator - dt);
    }
    if (this.system.time >= this.system.config.duration) { this.accumulator = 0; this.pause(); }
  }
}

class Controls {
  constructor(timeline, redraw) {
    this.timeline = timeline;
    this.redraw = redraw;
    this.playButton = document.getElementById('play');
    this.pauseButton = document.getElementById('pause');
    this.transport = document.getElementById('transport');
    this.playButton.addEventListener('click', () => this.play());
    this.pauseButton.addEventListener('click', () => this.pause());
    document.getElementById('restart').addEventListener('click', () => this.restart());
    document.getElementById('fullscreen').addEventListener('click', () => this.fullscreen());
    document.addEventListener('keydown', event => {
      if (event.repeat || event.altKey || event.ctrlKey || event.metaKey) return;
      const target = event.target;
      if (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName)) return;
      if (event.code === 'Space') {
        event.preventDefault();
        this.timeline.playing ? this.pause() : this.play();
      } else if (event.code === 'KeyR') {
        event.preventDefault(); this.restart();
      } else if (event.code === 'KeyH') {
        event.preventDefault();
        // A focused button must not keep hidden capture controls visible.
        if (this.transport.contains(document.activeElement)) document.activeElement.blur();
        const hidden = this.transport.classList.toggle('controls-hidden');
        this.transport.inert = hidden;
      } else if (event.code === 'KeyF') {
        event.preventDefault(); this.fullscreen();
      }
    });
    document.addEventListener('visibilitychange', () => {
      // Freeze elapsed time in a background tab, including AUTO_PLAY on load.
      this.timeline.lastTimestamp = null;
    });
  }
  play() {
    if (this.timeline.system.time >= this.timeline.system.config.duration) this.timeline.restart();
    this.timeline.play(); this.sync(); this.redraw();
  }
  pause() {
    this.timeline.pause(); this.sync(); this.redraw();
    document.getElementById('announcement').textContent = 'Pausado. Pressione Espaço para continuar.';
  }
  restart() {
    this.timeline.restart(); this.timeline.play(); this.sync(); this.redraw();
  }
  sync() {
    this.playButton.disabled = this.timeline.playing;
    this.pauseButton.disabled = !this.timeline.playing;
  }
  async fullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else if (document.documentElement.requestFullscreen) await document.documentElement.requestFullscreen();
    } catch (_) {
      // Embedded previews may deny fullscreen; ordinary playback stays available.
      document.getElementById('announcement').textContent = 'Tela cheia indisponível nesta janela. Abra o arquivo em uma janela do navegador.';
    }
  }
}

// Bootstrap: everything is offline and self-contained. No network, audio,
// animation libraries, modules, fonts, or timer intervals are required.
(() => {
  document.body.classList.toggle('recording', RECORDING_MODE);
  const system = new ParticleSystem();
  const renderer = new Renderer(document.getElementById('particles'), system);
  const hud = new HUD(system);
  const timeline = new Timeline(system);
  const redraw = () => { renderer.draw(); hud.update(true); hud.animate(); };
  const controls = new Controls(timeline, redraw);
  let lastTick = -1;
  let wasPlaying = false;
  function frame(timestamp) {
    if (!document.hidden) timeline.advance(timestamp);
    renderer.draw();
    if (lastTick !== system.tick || wasPlaying !== timeline.playing) {
      hud.update(!timeline.playing);
      hud.animate();
      lastTick = system.tick;
    }
    if (wasPlaying !== timeline.playing) {
      controls.sync();
      if (!timeline.playing && system.time === CONFIG.duration) {
        document.getElementById('announcement').textContent = 'Sequência concluída. Configuração mais ordenada e de menor energia relativa. Pressione R para reproduzir novamente.';
      }
      wasPlaying = timeline.playing;
    }
    requestAnimationFrame(frame);
  }
  window.addEventListener('resize', () => { renderer.surface.resize(); hud.chart.surface.resize(); redraw(); });
  // ResizeObserver can fire without window.resize (for example, panel resizing).
  const resizeChart = new ResizeObserver(() => hud.chart.draw(system));
  resizeChart.observe(document.getElementById('energy-plot'));
  redraw();
  if (AUTO_PLAY) controls.play();
  requestAnimationFrame(frame);
})();
