/**
 * High-performance, Canvas-based Didactic Charts for Ising Simulation
 * Fully self-contained, zero external dependencies.
 */

class RealtimeChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.historyM = [];
    this.historyE = [];
    this.maxPoints = 120;
    this.resize();
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = rect.height * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.width = rect.width;
    this.height = rect.height;
  }

  addPoint(m, e) {
    this.historyM.push(m);
    this.historyE.push(e);
    if (this.historyM.length > this.maxPoints) {
      this.historyM.shift();
      this.historyE.shift();
    }
    this.draw();
  }

  clear() {
    this.historyM = [];
    this.historyE = [];
    this.draw();
  }

  draw() {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    if (!ctx || w === 0 || h === 0) return;

    ctx.clearRect(0, 0, w, h);

    // Padding
    const pLeft = 40;
    const pRight = 15;
    const pTop = 20;
    const pBottom = 30;
    const graphW = w - pLeft - pRight;
    const graphH = h - pTop - pBottom;

    // Draw Grid Lines & Axes
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let yVal = -1; yVal <= 1; yVal += 0.5) {
      const py = pTop + graphH * (1 - (yVal + 1) / 2);
      ctx.moveTo(pLeft, py);
      ctx.lineTo(w - pRight, py);

      // Y-axis labels
      ctx.fillStyle = 'rgba(148, 163, 184, 0.7)';
      ctx.font = '10px "Fira Code", monospace';
      ctx.textAlign = 'right';
      ctx.fillText(yVal.toFixed(1), pLeft - 8, py + 3);
    }
    ctx.stroke();

    // Zero reference line
    const zeroY = pTop + graphH / 2;
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.beginPath();
    ctx.moveTo(pLeft, zeroY);
    ctx.lineTo(w - pRight, zeroY);
    ctx.stroke();

    if (this.historyM.length < 2) return;

    const dx = graphW / (this.maxPoints - 1);

    // Draw Energy Curve (Amber/Yellow)
    ctx.strokeStyle = '#ffb700';
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    for (let i = 0; i < this.historyE.length; i++) {
      const px = pLeft + i * dx;
      // Energy ranges roughly from -2 to +2
      const normalizedE = (this.historyE[i] + 2) / 4;
      const py = pTop + graphH * (1 - Math.max(0, Math.min(1, normalizedE)));
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();

    // Draw Magnetization Curve (Neon Cyan)
    ctx.strokeStyle = '#00f3ff';
    ctx.shadowColor = 'rgba(0, 243, 255, 0.5)';
    ctx.shadowBlur = 8;
    ctx.lineWidth = 2.2;
    ctx.beginPath();
    for (let i = 0; i < this.historyM.length; i++) {
      const px = pLeft + i * dx;
      const py = pTop + graphH * (1 - (this.historyM[i] + 1) / 2);
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();
    ctx.shadowBlur = 0; // reset glow

    // Chart Legend
    ctx.fillStyle = '#00f3ff';
    ctx.font = '600 11px Outfit, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('— Magnetização m(t)', pLeft + 10, pTop - 6);

    ctx.fillStyle = '#ffb700';
    ctx.fillText('— Energia e(t)', pLeft + 150, pTop - 6);
  }
}

class HysteresisChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.points = []; // { B, m }
    this.resize();
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = rect.height * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.width = rect.width;
    this.height = rect.height;
  }

  addPoint(B, m) {
    this.points.push({ B, m });
    if (this.points.length > 400) this.points.shift();
    this.draw();
  }

  clear() {
    this.points = [];
    this.draw();
  }

  draw() {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    if (!ctx || w === 0 || h === 0) return;

    ctx.clearRect(0, 0, w, h);

    const pLeft = 40;
    const pRight = 20;
    const pTop = 25;
    const pBottom = 35;
    const graphW = w - pLeft - pRight;
    const graphH = h - pTop - pBottom;

    // B range: -3.0 to +3.0
    const minB = -3.0, maxB = 3.0;

    // Axes
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
    ctx.lineWidth = 1;
    
    // Crosshair axes (B=0 and m=0)
    const zeroX = pLeft + graphW * (0 - minB) / (maxB - minB);
    const zeroY = pTop + graphH / 2;

    ctx.beginPath();
    ctx.moveTo(pLeft, zeroY); ctx.lineTo(w - pRight, zeroY);
    ctx.moveTo(zeroX, pTop); ctx.lineTo(zeroX, h - pBottom);
    ctx.stroke();

    // Labels
    ctx.fillStyle = 'rgba(148, 163, 184, 0.7)';
    ctx.font = '10px "Fira Code", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('Campo Magnético B', w / 2, h - 8);
    ctx.textAlign = 'right';
    ctx.fillText('m', pLeft - 8, zeroY + 3);

    if (this.points.length < 2) return;

    // Plot loop path
    ctx.strokeStyle = '#a855f7';
    ctx.shadowColor = 'rgba(168, 85, 247, 0.6)';
    ctx.shadowBlur = 6;
    ctx.lineWidth = 2;
    ctx.beginPath();

    for (let i = 0; i < this.points.length; i++) {
      const pt = this.points[i];
      const px = pLeft + graphW * (pt.B - minB) / (maxB - minB);
      const py = pTop + graphH * (1 - (pt.m + 1) / 2);
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Current point dot
    const last = this.points[this.points.length - 1];
    const lx = pLeft + graphW * (last.B - minB) / (maxB - minB);
    const ly = pTop + graphH * (1 - (last.m + 1) / 2);

    ctx.fillStyle = '#00f3ff';
    ctx.beginPath();
    ctx.arc(lx, ly, 5, 0, Math.PI * 2);
    ctx.fill();
  }
}

class PhaseChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.dataPoints = []; // { T, absM }
    this.resize();
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = rect.height * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.width = rect.width;
    this.height = rect.height;
  }

  setData(points) {
    this.dataPoints = points; // array of {T, absM}
    this.draw();
  }

  draw() {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    if (!ctx || w === 0 || h === 0) return;

    ctx.clearRect(0, 0, w, h);

    const pLeft = 40;
    const pRight = 20;
    const pTop = 25;
    const pBottom = 35;
    const graphW = w - pLeft - pRight;
    const graphH = h - pTop - pBottom;

    const minT = 0.1, maxT = 5.0;

    // Grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let tVal = 1; tVal <= 5; tVal++) {
      const px = pLeft + graphW * (tVal - minT) / (maxT - minT);
      ctx.moveTo(px, pTop); ctx.lineTo(px, h - pBottom);
      ctx.fillStyle = 'rgba(148, 163, 184, 0.7)';
      ctx.font = '10px "Fira Code", monospace';
      ctx.textAlign = 'center';
      ctx.fillText(tVal.toString(), px, h - pBottom + 15);
    }
    ctx.stroke();

    // Critical Temp line (Tc ≈ 2.27 for 2D square)
    const Tc = 2.269;
    const tcX = pLeft + graphW * (Tc - minT) / (maxT - minT);

    ctx.strokeStyle = 'rgba(255, 0, 85, 0.6)';
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(tcX, pTop);
    ctx.lineTo(tcX, h - pBottom);
    ctx.stroke();
    ctx.setLineDash([]); // reset dash

    ctx.fillStyle = '#ff0055';
    ctx.font = '600 10px Outfit, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Tc ≈ 2.27', tcX, pTop - 8);

    // Label X axis
    ctx.fillStyle = 'rgba(148, 163, 184, 0.8)';
    ctx.fillText('Temperatura (T)', w / 2, h - 5);

    // Plot Theoretical / Measured Curve
    if (this.dataPoints.length > 1) {
      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      for (let i = 0; i < this.dataPoints.length; i++) {
        const pt = this.dataPoints[i];
        const px = pLeft + graphW * (pt.T - minT) / (maxT - minT);
        const py = pTop + graphH * (1 - Math.max(0, Math.min(1, pt.absM)));
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.stroke();
    }
  }
}

if (typeof window !== 'undefined') {
  window.RealtimeChart = RealtimeChart;
  window.HysteresisChart = HysteresisChart;
  window.PhaseChart = PhaseChart;
}
