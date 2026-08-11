/**
 * UI Controller and Canvas Renderer for Ising Simulation
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Engine
  const engine = new IsingEngine(64, '2D_square');
  
  // UI Element Selectors
  const canvas = document.getElementById('isingCanvas');
  const ctx = canvas.getContext('2d');
  
  // Controls
  const tempSlider = document.getElementById('tempSlider');
  const tempVal = document.getElementById('tempVal');
  const couplingSlider = document.getElementById('couplingSlider');
  const couplingVal = document.getElementById('couplingVal');
  const fieldSlider = document.getElementById('fieldSlider');
  const fieldVal = document.getElementById('fieldVal');
  const speedSlider = document.getElementById('speedSlider');
  const speedVal = document.getElementById('speedVal');
  const latticeSizeSelect = document.getElementById('latticeSizeSelect');
  const geometrySelect = document.getElementById('geometrySelect');
  const couplingTypeSelect = document.getElementById('couplingTypeSelect');
  const themeSelect = document.getElementById('themeSelect');
  
  // Buttons
  const playPauseBtn = document.getElementById('playPauseBtn');
  const stepBtn = document.getElementById('stepBtn');
  const resetBtn = document.getElementById('resetBtn');
  const sweepHysteresisBtn = document.getElementById('sweepHysteresisBtn');
  
  // HUD Displays
  const valMag = document.getElementById('valMag');
  const valAbsMag = document.getElementById('valAbsMag');
  const valEnergy = document.getElementById('valEnergy');
  const valPhase = document.getElementById('valPhase');
  const badgePhase = document.getElementById('badgePhase');
  const fpsDisplay = document.getElementById('fpsDisplay');

  // Interactive Tools Buttons
  const toolButtons = document.querySelectorAll('.tool-btn');
  let currentTool = 'laser'; // 'flip', 'up', 'down', 'laser'
  let isMouseDown = false;

  // Initialize Charts
  const realtimeChart = new RealtimeChart('realtimeChartCanvas');
  const hysteresisChart = new HysteresisChart('hysteresisChartCanvas');
  const phaseChart = new PhaseChart('phaseChartCanvas');

  // Simulation State
  let isRunning = true;
  let mcStepsPerFrame = 5;
  let isHysteresisSweeping = false;
  let hysteresisDirection = 1;
  let hysteresisStep = 0;
  
  let lastFrameTime = performance.now();
  let frameCount = 0;
  let fps = 60;
  let frameStepCounter = 0;

  // Color Themes
  const themes = {
    cyberpunk: { up: '#00f3ff', down: '#ff0055', bg: '#05080e' },
    classic: { up: '#2563eb', down: '#dc2626', bg: '#0b0f19' },
    emerald: { up: '#10b981', down: '#1e293b', bg: '#060a12' },
    monochrome: { up: '#ffffff', down: '#111827', bg: '#000000' }
  };
  let currentTheme = themes.cyberpunk;

  // Resize canvas according to container
  function resizeCanvas() {
    const parent = canvas.parentElement;
    const size = Math.min(parent.clientWidth - 20, 500);
    canvas.width = size * window.devicePixelRatio;
    canvas.height = size * window.devicePixelRatio;
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    realtimeChart.resize();
    hysteresisChart.resize();
    phaseChart.resize();
  }
  window.addEventListener('resize', resizeCanvas);

  /**
   * Main Render Loop for Spin Grid
   */
  function renderGrid() {
    const displayWidth = canvas.clientWidth;
    const displayHeight = canvas.clientHeight;
    ctx.fillStyle = currentTheme.bg;
    ctx.fillRect(0, 0, displayWidth, displayHeight);

    const L = engine.L;
    const N = engine.spins.length;

    if (engine.dimension === '1D') {
      // Render 1D chain as horizontal strip/grid
      const cellW = displayWidth / L;
      const cellH = displayHeight / 8;
      const startY = (displayHeight - cellH) / 2;

      for (let i = 0; i < L; i++) {
        const s = engine.spins[i];
        ctx.fillStyle = s === 1 ? currentTheme.up : currentTheme.down;
        ctx.fillRect(i * cellW, startY, cellW + 0.5, cellH);
      }
      
      // Draw grid outline
      ctx.strokeStyle = 'rgba(255,255,255,0.05)';
      ctx.lineWidth = 1;
      ctx.strokeRect(0, startY, displayWidth, cellH);

    } else if (engine.dimension === '2D_triangular') {
      // Render 2D Triangular Lattice with staggered rows
      const rows = L;
      const cols = L;
      const cellH = displayHeight / rows;
      const cellW = displayWidth / (cols + 0.5);

      for (let y = 0; y < rows; y++) {
        const rowOffset = (y % 2 === 1) ? cellW * 0.5 : 0;
        for (let x = 0; x < cols; x++) {
          const idx = y * L + x;
          const s = engine.spins[idx];
          ctx.fillStyle = s === 1 ? currentTheme.up : currentTheme.down;

          const px = x * cellW + rowOffset;
          const py = y * cellH;

          // Render hexagon / staggered circle
          ctx.beginPath();
          ctx.arc(px + cellW / 2, py + cellH / 2, Math.max(1, cellW * 0.45), 0, Math.PI * 2);
          ctx.fill();
        }
      }
    } else {
      // Render Standard 2D Square Lattice
      const cellW = displayWidth / L;
      const cellH = displayHeight / L;

      // Optimization for large grids: use ImageData pixel manipulation if L >= 128
      if (L >= 128) {
        const imgData = ctx.createImageData(displayWidth, displayHeight);
        const data = imgData.data;
        const upRGB = hexToRgb(currentTheme.up);
        const downRGB = hexToRgb(currentTheme.down);

        for (let y = 0; y < displayHeight; y++) {
          const gridY = Math.floor((y / displayHeight) * L);
          for (let x = 0; x < displayWidth; x++) {
            const gridX = Math.floor((x / displayWidth) * L);
            const idx = gridY * L + gridX;
            const s = engine.spins[idx];
            const rgb = (s === 1) ? upRGB : downRGB;

            const pixelIdx = (y * displayWidth + x) * 4;
            data[pixelIdx] = rgb.r;
            data[pixelIdx + 1] = rgb.g;
            data[pixelIdx + 2] = rgb.b;
            data[pixelIdx + 3] = 255;
          }
        }
        ctx.putImageData(imgData, 0, 0);
      } else {
        for (let y = 0; y < L; y++) {
          for (let x = 0; x < L; x++) {
            const idx = y * L + x;
            const s = engine.spins[idx];
            ctx.fillStyle = s === 1 ? currentTheme.up : currentTheme.down;
            ctx.fillRect(x * cellW, y * cellH, cellW + 0.4, cellH + 0.4);
          }
        }
      }
    }
  }

  function hexToRgb(hex) {
    hex = hex.replace('#', '');
    if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
    const num = parseInt(hex, 16);
    return { r: (num >> 16) & 255, g: (num >> 8) & 255, b: num & 255 };
  }

  /**
   * Update HUD and Didactic Context
   */
  function updateHUD() {
    const m = engine.m;
    const absM = Math.abs(m);
    const e = engine.e;

    valMag.textContent = (m >= 0 ? '+' : '') + m.toFixed(3);
    valAbsMag.textContent = absM.toFixed(3);
    valEnergy.textContent = e.toFixed(3);

    // Phase identification
    const Tc = engine.Tc2DSquare;
    if (engine.dimension === '1D') {
      valPhase.textContent = 'Sem Ordem Longo Alcance (1D)';
      badgePhase.style.borderColor = 'rgba(255, 183, 0, 0.4)';
      badgePhase.style.color = '#ffb700';
    } else if (engine.couplingType === 'antiferro') {
      valPhase.textContent = 'Ordem Antiferromagnética';
      badgePhase.style.borderColor = 'rgba(168, 85, 247, 0.4)';
      badgePhase.style.color = '#a855f7';
    } else if (engine.couplingType === 'spin_glass') {
      valPhase.textContent = 'Vidro de Spin (Frustrado)';
      badgePhase.style.borderColor = 'rgba(236, 72, 153, 0.4)';
      badgePhase.style.color = '#ec4899';
    } else if (Tc) {
      if (engine.T < Tc - 0.15) {
        valPhase.textContent = 'Fase Ferromagnética (Ordenada)';
        badgePhase.style.borderColor = 'rgba(0, 243, 255, 0.4)';
        badgePhase.style.color = '#00f3ff';
      } else if (engine.T > Tc + 0.15) {
        valPhase.textContent = 'Fase Paramagnética (Desordenada)';
        badgePhase.style.borderColor = 'rgba(255, 0, 85, 0.4)';
        badgePhase.style.color = '#ff0055';
      } else {
        valPhase.textContent = 'Ponto Crítico (Flutuações de Escala!)';
        badgePhase.style.borderColor = 'rgba(255, 183, 0, 0.6)';
        badgePhase.style.color = '#ffb700';
      }
    } else {
      valPhase.textContent = 'Simulando...';
    }
  }

  /**
   * Hysteresis Automated Sweep
   */
  function handleHysteresisSweep() {
    if (!isHysteresisSweeping) return;

    let currentB = engine.B;
    const stepSize = 0.05 * hysteresisDirection;
    currentB += stepSize;

    if (currentB >= 3.0) {
      currentB = 3.0;
      hysteresisDirection = -1;
    } else if (currentB <= -3.0) {
      currentB = -3.0;
      hysteresisDirection = 1;
      hysteresisStep++;
      if (hysteresisStep >= 2) {
        // Completed 2 full loops, stop automatically
        isHysteresisSweeping = false;
        sweepHysteresisBtn.classList.remove('active');
        sweepHysteresisBtn.innerHTML = '<i class="fa-solid fa-sync"></i> Loop de Histerese Auto';
      }
    }

    engine.setField(currentB);
    fieldSlider.value = currentB;
    fieldVal.textContent = (currentB >= 0 ? '+' : '') + currentB.toFixed(2);
  }

  /**
   * Main Simulation Loop
   */
  function animate(now) {
    // FPS calculation
    frameCount++;
    if (now - lastFrameTime >= 1000) {
      fps = Math.round((frameCount * 1000) / (now - lastFrameTime));
      fpsDisplay.textContent = `${fps} FPS`;
      frameCount = 0;
      lastFrameTime = now;
    }

    if (isRunning) {
      if (isHysteresisSweeping) {
        handleHysteresisSweep();
      }

      // Run Monte Carlo updates
      engine.step(mcStepsPerFrame);

      // Record chart data every 2 frames
      frameStepCounter++;
      if (frameStepCounter % 2 === 0) {
        realtimeChart.addPoint(engine.m, engine.e);
        hysteresisChart.addPoint(engine.B, engine.m);
      }
    }

    renderGrid();
    updateHUD();

    requestAnimationFrame(animate);
  }

  // Handle Input Controls
  tempSlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    tempVal.textContent = val.toFixed(2);
    engine.setTemperature(val);
  });

  couplingSlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    couplingVal.textContent = (val >= 0 ? '+' : '') + val.toFixed(2);
    engine.J = val;
    engine.recomputeSystemStats();
  });

  fieldSlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    fieldVal.textContent = (val >= 0 ? '+' : '') + val.toFixed(2);
    engine.setField(val);
  });

  speedSlider.addEventListener('input', (e) => {
    mcStepsPerFrame = parseInt(e.target.value, 10);
    speedVal.textContent = `${mcStepsPerFrame}x`;
  });

  latticeSizeSelect.addEventListener('change', (e) => {
    const newL = parseInt(e.target.value, 10);
    engine.L = newL;
    engine.resetGrid('random');
    realtimeChart.clear();
    hysteresisChart.clear();
    resizeCanvas();
  });

  geometrySelect.addEventListener('change', (e) => {
    engine.dimension = e.target.value;
    engine.resetGrid('random');
    realtimeChart.clear();
    hysteresisChart.clear();
  });

  couplingTypeSelect.addEventListener('change', (e) => {
    engine.couplingType = e.target.value;
    engine.initCouplings();
    engine.resetGrid('random');
    realtimeChart.clear();
    hysteresisChart.clear();
  });

  themeSelect.addEventListener('change', (e) => {
    currentTheme = themes[e.target.value] || themes.cyberpunk;
    document.documentElement.style.setProperty('--spin-up-color', currentTheme.up);
    document.documentElement.style.setProperty('--spin-down-color', currentTheme.down);
  });

  // Buttons Play/Pause/Step/Reset
  playPauseBtn.addEventListener('click', () => {
    isRunning = !isRunning;
    const dot = document.querySelector('.status-dot');
    if (isRunning) {
      playPauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i> Pausar';
      playPauseBtn.classList.remove('btn-secondary');
      playPauseBtn.classList.add('btn-primary');
      if (dot) dot.classList.remove('paused');
    } else {
      playPauseBtn.innerHTML = '<i class="fa-solid fa-play"></i> Continuar';
      playPauseBtn.classList.remove('btn-primary');
      playPauseBtn.classList.add('btn-secondary');
      if (dot) dot.classList.add('paused');
    }
  });

  stepBtn.addEventListener('click', () => {
    engine.step(1);
    realtimeChart.addPoint(engine.m, engine.e);
    hysteresisChart.addPoint(engine.B, engine.m);
    renderGrid();
    updateHUD();
  });

  resetBtn.addEventListener('click', () => {
    engine.resetGrid('random');
    realtimeChart.clear();
    hysteresisChart.clear();
  });

  sweepHysteresisBtn.addEventListener('click', () => {
    isHysteresisSweeping = !isHysteresisSweeping;
    hysteresisStep = 0;
    hysteresisDirection = 1;
    if (isHysteresisSweeping) {
      sweepHysteresisBtn.classList.add('active');
      sweepHysteresisBtn.innerHTML = '<i class="fa-solid fa-stop"></i> Parar Histerese';
      // Switch to hysteresis tab
      document.querySelector('[data-tab="tab-hysteresis"]').click();
    } else {
      sweepHysteresisBtn.classList.remove('active');
      sweepHysteresisBtn.innerHTML = '<i class="fa-solid fa-sync"></i> Loop de Histerese Auto';
    }
  });

  // Interactive Tools Selection
  toolButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      toolButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentTool = btn.dataset.tool;
    });
  });

  // Mouse Canvas Interaction
  function handleCanvasMouse(e) {
    const rect = canvas.getBoundingClientRect();
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    if (!clientX || !clientY) return;

    const x = (clientX - rect.left) / rect.width;
    const y = (clientY - rect.top) / rect.height;

    const L = engine.L;
    const gridX = Math.floor(x * L);
    const gridY = Math.floor(y * L);

    if (currentTool === 'flip') {
      engine.flipSpinAt(gridX, gridY);
    } else if (currentTool === 'up') {
      engine.setSpinAt(gridX, gridY, 1);
    } else if (currentTool === 'down') {
      engine.setSpinAt(gridX, gridY, -1);
    } else if (currentTool === 'laser') {
      engine.applyLaserField(gridX, gridY, Math.max(2, Math.floor(L / 16)), true);
    }
  }

  canvas.addEventListener('mousedown', (e) => {
    isMouseDown = true;
    handleCanvasMouse(e);
  });
  canvas.addEventListener('mousemove', (e) => {
    if (isMouseDown) handleCanvasMouse(e);
  });
  window.addEventListener('mouseup', () => { isMouseDown = false; });

  // Touch support
  canvas.addEventListener('touchstart', (e) => {
    isMouseDown = true;
    handleCanvasMouse(e);
  });
  canvas.addEventListener('touchmove', (e) => {
    if (isMouseDown) handleCanvasMouse(e);
  });
  window.addEventListener('touchend', () => { isMouseDown = false; });

  // Presets Handlers
  const presetButtons = document.querySelectorAll('.preset-btn');
  presetButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      presetButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const preset = btn.dataset.preset;
      applyPreset(preset);
    });
  });

  function applyPreset(preset) {
    isHysteresisSweeping = false;
    sweepHysteresisBtn.classList.remove('active');
    sweepHysteresisBtn.innerHTML = '<i class="fa-solid fa-sync"></i> Loop de Histerese Auto';

    if (preset === 'ferro_low_t') {
      geometrySelect.value = '2D_square';
      couplingTypeSelect.value = 'ferro';
      engine.dimension = '2D_square';
      engine.couplingType = 'ferro';
      engine.setTemperature(1.20);
      engine.J = 1.0;
      engine.setField(0.0);
      engine.resetGrid('random');
    } else if (preset === 'critical_point') {
      geometrySelect.value = '2D_square';
      couplingTypeSelect.value = 'ferro';
      engine.dimension = '2D_square';
      engine.couplingType = 'ferro';
      engine.setTemperature(2.269); // Exact Tc
      engine.J = 1.0;
      engine.setField(0.0);
      engine.resetGrid('random');
    } else if (preset === 'paramagnetic') {
      geometrySelect.value = '2D_square';
      couplingTypeSelect.value = 'ferro';
      engine.dimension = '2D_square';
      engine.couplingType = 'ferro';
      engine.setTemperature(4.80);
      engine.J = 1.0;
      engine.setField(0.0);
      engine.resetGrid('random');
    } else if (preset === 'antiferro') {
      geometrySelect.value = '2D_square';
      couplingTypeSelect.value = 'antiferro';
      engine.dimension = '2D_square';
      engine.couplingType = 'antiferro';
      engine.setTemperature(1.00);
      engine.J = 1.0;
      engine.setField(0.0);
      engine.resetGrid('random');
    } else if (preset === 'triangular_frust') {
      geometrySelect.value = '2D_triangular';
      couplingTypeSelect.value = 'antiferro';
      engine.dimension = '2D_triangular';
      engine.couplingType = 'antiferro';
      engine.setTemperature(0.80);
      engine.J = 1.0;
      engine.setField(0.0);
      engine.resetGrid('random');
    } else if (preset === 'spin_glass') {
      geometrySelect.value = '2D_square';
      couplingTypeSelect.value = 'spin_glass';
      engine.dimension = '2D_square';
      engine.couplingType = 'spin_glass';
      engine.initCouplings();
      engine.setTemperature(0.70);
      engine.J = 1.0;
      engine.setField(0.0);
      engine.resetGrid('random');
    } else if (preset === 'model_1d') {
      geometrySelect.value = '1D';
      couplingTypeSelect.value = 'ferro';
      engine.dimension = '1D';
      engine.L = 128;
      latticeSizeSelect.value = '128';
      engine.couplingType = 'ferro';
      engine.setTemperature(0.80);
      engine.J = 1.0;
      engine.setField(0.0);
      engine.resetGrid('random');
    } else if (preset === 'hysteresis') {
      geometrySelect.value = '2D_square';
      couplingTypeSelect.value = 'ferro';
      engine.dimension = '2D_square';
      engine.couplingType = 'ferro';
      engine.setTemperature(1.50); // Below Tc for strong hysteresis
      engine.J = 1.0;
      engine.setField(-3.0);
      engine.resetGrid('all_down');
      
      // Enable hysteresis loop
      isHysteresisSweeping = true;
      sweepHysteresisBtn.classList.add('active');
      sweepHysteresisBtn.innerHTML = '<i class="fa-solid fa-stop"></i> Parar Histerese';
      document.querySelector('[data-tab="tab-hysteresis"]').click();
    }

    // Sync UI sliders
    tempSlider.value = engine.T;
    tempVal.textContent = engine.T.toFixed(2);
    couplingSlider.value = engine.J;
    couplingVal.textContent = (engine.J >= 0 ? '+' : '') + engine.J.toFixed(2);
    fieldSlider.value = engine.B;
    fieldVal.textContent = (engine.B >= 0 ? '+' : '') + engine.B.toFixed(2);

    realtimeChart.clear();
    hysteresisChart.clear();
  }

  // Tabs Switcher
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.dataset.tab;
      document.getElementById(targetId).classList.add('active');

      if (targetId === 'tab-phase') {
        computePhaseDiagram();
      }
    });
  });

  /**
   * Fast Phase Diagram Generator (|m| vs T curve)
   */
  function computePhaseDiagram() {
    const points = [];
    const savedT = engine.T;
    const tempEngine = new IsingEngine(32, engine.dimension);
    tempEngine.couplingType = engine.couplingType;

    for (let tVal = 0.2; tVal <= 5.0; tVal += 0.15) {
      tempEngine.setTemperature(tVal);
      tempEngine.resetGrid('all_up');
      tempEngine.step(30); // thermalization
      let avgAbsM = 0;
      for (let s = 0; s < 10; s++) {
        tempEngine.step(5);
        avgAbsM += Math.abs(tempEngine.m);
      }
      avgAbsM /= 10;
      points.push({ T: tVal, absM: avgAbsM });
    }

    phaseChart.setData(points);
  }

  // Accordion Didactic Cards
  const accordionHeaders = document.querySelectorAll('.didactic-card-header');
  accordionHeaders.forEach(header => {
    header.addEventListener('click', () => {
      const parentCard = header.parentElement;
      parentCard.classList.toggle('open');
    });
  });

  // Start Simulation
  resizeCanvas();
  requestAnimationFrame(animate);
});
