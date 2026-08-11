/**
 * Core Physics Engine for the Ising Model Simulation
 * Supports:
 * - 2D Square Lattice
 * - 2D Triangular Lattice (Geometric Frustration)
 * - 1D Chain
 * - Ferromagnetic (J > 0), Antiferromagnetic (J < 0), Spin Glass (Random Jij)
 * - Periodic and Open Boundary Conditions
 * - Fast Metropolis-Hastings update with precomputed Boltzmann probabilities
 */

class IsingEngine {
  constructor(L = 64, dimension = '2D_square') {
    this.L = L;
    this.dimension = dimension; // '2D_square', '2D_triangular', '1D'
    this.couplingType = 'ferro'; // 'ferro', 'antiferro', 'spin_glass'
    
    // Physics parameters
    this.T = 2.269; // Default near critical temp
    this.J = 1.0;   // Coupling constant amplitude
    this.B = 0.0;   // External magnetic field
    this.boundary = 'periodic'; // 'periodic' or 'open'
    
    // Grid array s[i] inside {-1, +1}
    this.N = L * L;
    this.spins = new Int8Array(this.N);
    
    // Coupling matrix for Spin Glass mode (sparse/neighbor index based)
    // For 2D square: max 4 neighbors per site
    // For 2D triangular: max 6 neighbors per site
    // For 1D: 2 neighbors
    this.J_couplings = null; // Map site -> neighbor couplings
    
    // Fast Boltzmann lookup cache for common energy changes
    this.expCache = new Map();
    
    // Tracking variables
    this.energy = 0;
    this.magnetization = 0;
    this.mcStepsExecuted = 0;

    this.resetGrid('random');
  }

  /**
   * Re-initialize spin lattice
   * @param {string} initialMode - 'random', 'all_up', 'all_down', 'checkerboard'
   */
  resetGrid(initialMode = 'random') {
    this.N = (this.dimension === '1D') ? this.L : this.L * this.L;
    this.spins = new Int8Array(this.N);

    for (let i = 0; i < this.N; i++) {
      if (initialMode === 'all_up') {
        this.spins[i] = 1;
      } else if (initialMode === 'all_down') {
        this.spins[i] = -1;
      } else if (initialMode === 'checkerboard') {
        if (this.dimension === '1D') {
          this.spins[i] = (i % 2 === 0) ? 1 : -1;
        } else {
          const x = i % this.L;
          const y = Math.floor(i / this.L);
          this.spins[i] = ((x + y) % 2 === 0) ? 1 : -1;
        }
      } else {
        // Random 50/50
        this.spins[i] = Math.random() < 0.5 ? 1 : -1;
      }
    }

    this.initCouplings();
    this.recomputeSystemStats();
    this.mcStepsExecuted = 0;
  }

  /**
   * Set up neighbor couplings based on geometry & model type
   */
  initCouplings() {
    if (this.couplingType === 'spin_glass') {
      // Bimodal random J_ij = +J or -J with equal probability
      this.J_couplings = new Float32Array(this.N * 6); // Up to 6 neighbors
      const currentJ = Math.abs(this.J);
      for (let i = 0; i < this.J_couplings.length; i++) {
        this.J_couplings[i] = (Math.random() < 0.5 ? 1 : -1) * currentJ;
      }
    } else {
      this.J_couplings = null; // Standard uniform coupling
    }
  }

  /**
   * Set temperature and update cache
   */
  setTemperature(T) {
    this.T = Math.max(0.01, T);
  }

  /**
   * Set external field B
   */
  setField(B) {
    const oldB = this.B;
    this.B = B;
    // Energy change due to field change = - (B_new - B_old) * Magnetization
    this.energy -= (B - oldB) * this.magnetization;
  }

  /**
   * Get neighbors of a site index i based on lattice geometry
   */
  getNeighborIndices(idx) {
    const L = this.L;
    
    if (this.dimension === '1D') {
      let left = idx - 1;
      let right = idx + 1;
      if (this.boundary === 'periodic') {
        if (left < 0) left = L - 1;
        if (right >= L) right = 0;
      } else {
        if (left < 0) left = idx; // boundary check
        if (right >= L) right = idx;
      }
      return [left, right];
    }

    const x = idx % L;
    const y = Math.floor(idx / L);

    let left = x - 1;
    let right = x + 1;
    let top = y - 1;
    let bottom = y + 1;

    if (this.boundary === 'periodic') {
      if (left < 0) left = L - 1;
      if (right >= L) right = 0;
      if (top < 0) top = L - 1;
      if (bottom >= L) bottom = 0;
    } else {
      if (left < 0) left = x;
      if (right >= L) right = x;
      if (top < 0) top = y;
      if (bottom >= L) bottom = y;
    }

    const idxLeft = y * L + left;
    const idxRight = y * L + right;
    const idxTop = top * L + x;
    const idxBottom = bottom * L + x;

    if (this.dimension === '2D_triangular') {
      // Triangular lattice adds diagonal neighbors (top-left & bottom-right)
      let topLeftY = y - 1;
      let topLeftX = x - 1;
      let btmRightY = y + 1;
      let btmRightX = x + 1;

      if (this.boundary === 'periodic') {
        if (topLeftX < 0) topLeftX = L - 1;
        if (topLeftY < 0) topLeftY = L - 1;
        if (btmRightX >= L) btmRightX = 0;
        if (btmRightY >= L) btmRightY = 0;
      } else {
        if (topLeftX < 0) topLeftX = x;
        if (topLeftY < 0) topLeftY = y;
        if (btmRightX >= L) btmRightX = x;
        if (btmRightY >= L) btmRightY = y;
      }

      const idxTopLeft = topLeftY * L + topLeftX;
      const idxBtmRight = btmRightY * L + btmRightX;

      return [idxLeft, idxRight, idxTop, idxBottom, idxTopLeft, idxBtmRight];
    }

    // Default 2D Square
    return [idxLeft, idxRight, idxTop, idxBottom];
  }

  /**
   * Recalculate full energy and magnetization from scratch
   */
  recomputeSystemStats() {
    let E = 0;
    let M = 0;
    const effJ = (this.couplingType === 'antiferro') ? -Math.abs(this.J) : Math.abs(this.J);

    for (let i = 0; i < this.N; i++) {
      const s = this.spins[i];
      M += s;
      
      const neighbors = this.getNeighborIndices(i);
      let sumNeighborSpins = 0;

      if (this.couplingType === 'spin_glass') {
        for (let k = 0; k < neighbors.length; k++) {
          const nIdx = neighbors[k];
          const J_val = this.J_couplings[i * 6 + k];
          E -= 0.5 * J_val * s * this.spins[nIdx];
        }
      } else {
        for (let k = 0; k < neighbors.length; k++) {
          sumNeighborSpins += this.spins[neighbors[k]];
        }
        // Factor of 0.5 because each pair is counted twice
        E -= 0.5 * effJ * s * sumNeighborSpins;
      }

      E -= this.B * s;
    }

    this.energy = E;
    this.magnetization = M;
  }

  /**
   * Single Metropolis Monte Carlo sweep (N trial spin flips)
   * @param {number} sweeps - Number of full lattice sweeps to perform
   */
  step(sweeps = 1) {
    const N = this.N;
    const totalFlipsAttempted = sweeps * N;
    const effJ = (this.couplingType === 'antiferro') ? -Math.abs(this.J) : Math.abs(this.J);
    const beta = 1.0 / this.T;

    for (let step = 0; step < totalFlipsAttempted; step++) {
      // Pick random site
      const i = Math.floor(Math.random() * N);
      const s_i = this.spins[i];
      
      const neighbors = this.getNeighborIndices(i);
      let deltaE = 0;

      if (this.couplingType === 'spin_glass') {
        let sumInteraction = 0;
        for (let k = 0; k < neighbors.length; k++) {
          const nIdx = neighbors[k];
          const J_val = this.J_couplings[i * 6 + k];
          sumInteraction += J_val * this.spins[nIdx];
        }
        // Delta E = E_new - E_old = 2 * s_i * (sum_j J_ij s_j + B)
        deltaE = 2 * s_i * (sumInteraction + this.B);
      } else {
        let sumNeighborSpins = 0;
        for (let k = 0; k < neighbors.length; k++) {
          sumNeighborSpins += this.spins[neighbors[k]];
        }
        deltaE = 2 * s_i * (effJ * sumNeighborSpins + this.B);
      }

      // Metropolis criterion
      if (deltaE <= 0 || Math.random() < Math.exp(-deltaE * beta)) {
        // Accept flip
        this.spins[i] = -s_i;
        this.energy += deltaE;
        this.magnetization -= 2 * s_i;
      }
    }

    this.mcStepsExecuted += sweeps;
  }

  /**
   * Flip spin at specific grid location (interactive user action)
   */
  flipSpinAt(gridX, gridY) {
    const L = this.L;
    let idx = gridY * L + gridX;
    if (this.dimension === '1D') idx = gridX;

    if (idx >= 0 && idx < this.N) {
      const s_i = this.spins[idx];
      this.spins[idx] = -s_i;
      this.recomputeSystemStats();
    }
  }

  /**
   * Force spin value at coordinate
   */
  setSpinAt(gridX, gridY, val) {
    const L = this.L;
    let idx = gridY * L + gridX;
    if (this.dimension === '1D') idx = gridX;

    if (idx >= 0 && idx < this.N) {
      if (this.spins[idx] !== val) {
        this.spins[idx] = val;
        this.recomputeSystemStats();
      }
    }
  }

  /**
   * Apply local laser field around (gridX, gridY)
   */
  applyLaserField(gridX, gridY, radius = 3, forceUp = true) {
    const targetVal = forceUp ? 1 : -1;
    const L = this.L;

    if (this.dimension === '1D') {
      for (let dx = -radius; dx <= radius; dx++) {
        let x = (gridX + dx + L) % L;
        this.spins[x] = targetVal;
      }
    } else {
      for (let dy = -radius; dy <= radius; dy++) {
        for (let dx = -radius; dx <= radius; dx++) {
          if (dx * dx + dy * dy <= radius * radius) {
            let x = (gridX + dx + L) % L;
            let y = (gridY + dy + L) % L;
            this.spins[y * L + x] = targetVal;
          }
        }
      }
    }
    this.recomputeSystemStats();
  }

  /**
   * Average Magnetization m = M / N
   */
  get m() {
    return this.magnetization / this.N;
  }

  /**
   * Average Energy e = E / N
   */
  get e() {
    return this.energy / this.N;
  }

  /**
   * Theoretical Curie Temperature T_c for 2D Square Ferromagnet
   */
  get Tc2DSquare() {
    if (this.couplingType === 'ferro' && this.dimension === '2D_square') {
      return 2.0 * Math.abs(this.J) / Math.log(1 + Math.sqrt(2)); // ~ 2.269 * J
    }
    return null;
  }
}

// Export for usage
if (typeof window !== 'undefined') {
  window.IsingEngine = IsingEngine;
}
