/* audio-feats.js: a track feature map inside a scene, hit(kind, t, halfLife) and env(name, t).
 *
 * Idea after app/src/engine/audio.ts from mexicat/pdoom-video (MIT, (c) 2026 Giacomo Magnanini);
 * the code is written from scratch.
 *
 * Data: the `audio-feats.gen.js` written by `python3 tools/audio/audio_feats.py export <track> --offset ...
 * --out <scene>/audio-feats.gen.js`. It sets window.__AUDIO_FEATS already in video time (track offset subtracted).
 * Load both before your scene script:
 *   <script src="audio-feats.js"></script><script src="audio-feats.gen.js"></script>
 *
 * Two ways to use it, both deterministic (a frame is a function of t):
 *  1. Canvas or setTime(t) scenes: A.hit('kick', t), A.env('low', t) right in the draw call.
 *  2. GSAP timelines that a renderer seeks with suppressEvents (onUpdate is not called there): bake the
 *     reaction into tweens with A.pulses(...) and A.follow(...). Tweens of one property never overlap (each
 *     ends before the next hit).
 *
 * A tool, not a law: on a measured hit, cuts landed on the beat no more often than random ones. Use it for
 * interface sounds, accents and a background pulse; cuts on the beat only where the edit asks for a hit.
 */
(function (root) {
  'use strict';
  const FR = 1 / 60;

  function make(data) {
    const D = data || root.__AUDIO_FEATS;
    if (!D) throw new Error('audio-feats: no window.__AUDIO_FEATS (run audio_feats.py export)');
    const fps = D.fps || 100, env0 = D.env || {}, ons = D.onsets || {}, B = D.beats || [], DB = D.downbeats || [];

    /** Envelope 0..1 (rms, low, mid, high), linearly interpolated. */
    function env(name, t) {
      const a = env0[name];
      if (!a || !a.length) return 0;
      const x = t * fps, i = Math.floor(x);
      if (i < 0) return a[0];
      if (i >= a.length - 1) return a[a.length - 1];
      const f = x - i;
      return a[i] * (1 - f) + a[i + 1] * f;
    }

    /** Peak over the last w seconds: a "click" on the hit without jitter. */
    function envPeak(name, t, w = 0.08) {
      let m = 0;
      for (let s = t - w; s <= t + 1e-9; s += 1 / fps) m = Math.max(m, env(name, s));
      return m;
    }

    /** Decaying impulse from the latest hits of kind (kick, snare, hat): 1 x strength on the hit, half-life halfLife. */
    function hit(kind, t, halfLife = 0.11) {
      const L = ons[kind];
      if (!L || !L.length) return 0;
      let lo = 0, hi = L.length;
      while (lo < hi) { const m = (lo + hi) >> 1; if (L[m][0] <= t) lo = m + 1; else hi = m; }
      let v = 0;
      for (let i = lo - 1; i >= 0 && i >= lo - 6; i--) {
        const dt = t - L[i][0];
        if (dt > halfLife * 8) break;
        v = Math.max(v, L[i][1] * Math.pow(0.5, dt / halfLife));
      }
      return v;
    }

    /** Hits of kind in [t0, t1) with a strength floor. */
    function events(kind, t0, t1, minStrength = 0) {
      return (ons[kind] || []).filter(([t, s]) => t >= t0 && t < t1 && s >= minStrength);
    }

    /** Continuous beat number (fractional between beats, extrapolated at the edges). */
    function beatAt(t) {
      if (B.length < 2) return t * (D.bpm || 120) / 60;
      if (t <= B[0]) return (t - B[0]) / (B[1] - B[0]);
      const n = B.length;
      if (t >= B[n - 1]) return n - 1 + (t - B[n - 1]) / (B[n - 1] - B[n - 2]);
      let lo = 0, hi = n - 1;
      while (hi - lo > 1) { const m = (lo + hi) >> 1; if (B[m] <= t) lo = m; else hi = m; }
      return lo + (t - B[lo]) / (B[hi] - B[lo]);
    }

    function timeOfBeat(i) {
      const n = B.length;
      if (!n) return i * 60 / (D.bpm || 120);
      const P = n > 1 ? (B[n - 1] - B[0]) / (n - 1) : 60 / (D.bpm || 120);
      if (i <= 0) return B[0] + i * P;
      if (i >= n - 1) return B[n - 1] + (i - (n - 1)) * P;
      const k = Math.floor(i);
      return B[k] + (B[k + 1] - B[k]) * (i - k);
    }

    /** Phase inside the beat 0..1 and whether it is a downbeat: for swaying "in time". */
    function phase(t) {
      const b = beatAt(t), i = Math.floor(b);
      const bt = timeOfBeat(i);
      return { i, p: b - i, down: DB.some(d => Math.abs(d - bt) < 0.02) };
    }

    const nearestBeat = t => timeOfBeat(Math.round(beatAt(t)));

    /** Cut on the last beat no later than the first word (tol 20 ms); beyond maxLead the cut stays on the word. */
    function cutBefore(tWord, tol = 0.02, maxLead = 0.6) {
      const c = timeOfBeat(Math.floor(beatAt(tWord + tol)));
      return tWord - c > maxLead ? tWord : c;
    }

    const section = t => (D.sections || []).find(s => t >= s.start && t < s.end) || null;

    /**
     * Bake impulses into GSAP: on every hit of kind, prop jumps to base + amp x strength and returns to base
     * with 'expo.out' (close to an exponential decay). Each impulse is cut to the next hit minus a frame, so
     * tweens of one property do not overlap.
     *   A.pulses(tl, '#bg', 'kick', {prop: 'scale', base: 1, amp: .03, t0: 2, t1: 9, min: .5})
     */
    function pulses(tl, target, kind, o = {}) {
      const prop = o.prop || 'scale', base = o.base ?? 1, amp = o.amp ?? 0.04, dur = o.dur ?? 0.32;
      const L = events(kind, o.t0 ?? 0, o.t1 ?? (D.duration || 1e9), o.min ?? 0.4);
      const ease = o.ease || 'expo.out';
      let n = 0;
      L.forEach(([t, s], i) => {
        const next = i + 1 < L.length ? L[i + 1][0] : t + dur;
        const d = Math.min(dur, next - t - (o.frame ?? FR));
        if (d < 0.04) return;
        tl.fromTo(target, { [prop]: base + amp * s }, { [prop]: base, duration: d, ease, immediateRender: false }, t);
        n++;
      });
      return n;
    }

    /**
     * Bake an envelope into GSAP as a chain of short linear tweens (step s): prop = from + (to - from) x env.
     *   A.follow(tl, '#glow', 'low', {prop: 'opacity', from: .2, to: .8, t0: 0, t1: 6, step: 1/15})
     */
    function follow(tl, target, name, o = {}) {
      const prop = o.prop || 'opacity', from = o.from ?? 0, to = o.to ?? 1, step = o.step ?? 1 / 15;
      const t0 = o.t0 ?? 0, t1 = o.t1 ?? (D.duration || 0);
      const val = t => +(from + (to - from) * envPeak(name, t, step)).toFixed(4);
      tl.set(target, { [prop]: val(t0) }, t0);
      let n = 0;
      for (let t = t0; t < t1 - 1e-6; t += step) {
        const d = Math.min(step, t1 - t);
        tl.to(target, { [prop]: val(t + d), duration: d, ease: 'none' }, t);
        n++;
      }
      return n;
    }

    return { data: D, env, envPeak, hit, events, beatAt, timeOfBeat, phase, nearestBeat, cutBefore, section, pulses, follow };
  }

  root.AudioFeats = { make };
  if (typeof module !== 'undefined' && module.exports) module.exports = { make };
})(typeof window !== 'undefined' ? window : globalThis);
