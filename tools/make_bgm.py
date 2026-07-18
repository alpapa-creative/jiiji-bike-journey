# demo-bike-tabi 用の自作チップチューンBGM生成（ライセンスクリーン）
# nori: 152BPM Aメジャー / shinmiri: 76BPM Cメジャー
import numpy as np, wave, os

SR = 44100
OUT = "/private/tmp/claude-501/-Users-r-a--Documents-03--------AI---04-others-aoki-playmode/a1fa17f3-ed63-4ead-94ec-c1c8ee81610a/scratchpad/bgm"

def f(m): return 440.0 * 2 ** ((m - 69) / 12)

def env(n, att=0.008, rel=0.04):
    e = np.ones(n)
    a = max(1, int(att * SR)); r = max(1, int(rel * SR))
    if a + r >= n: a = n // 3; r = n // 3
    e[:a] = np.linspace(0, 1, a)
    e[-r:] = np.linspace(1, 0, r)
    return e

def square(freq, n, duty=0.5, vib=0.0):
    t = np.arange(n) / SR
    ph = freq * t
    if vib: ph = ph * (1 + vib * np.sin(2 * np.pi * 5.2 * t))
    return np.where((ph % 1) < duty, 1.0, -1.0)

def tri(freq, n, vib=0.0):
    t = np.arange(n) / SR
    ph = freq * t
    if vib: ph = ph * (1 + vib * np.sin(2 * np.pi * 5.0 * t))
    return 2 * np.abs(2 * (ph % 1) - 1) - 1

def place(buf, sig, t0):
    i = int(t0 * SR)
    j = min(len(buf), i + len(sig))
    if i < len(buf): buf[i:j] += sig[: j - i]

def kick(n=None):
    n = n or int(0.11 * SR)
    t = np.arange(n) / SR
    fr = 110 * np.exp(-t * 30) + 35
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 22)

def snare():
    n = int(0.12 * SR); t = np.arange(n) / SR
    rng = np.random.default_rng(7)
    return (rng.standard_normal(n) * 0.7 + np.sin(2 * np.pi * 185 * t) * 0.4) * np.exp(-t * 30)

def hat():
    n = int(0.035 * SR)
    rng = np.random.default_rng(3)
    x = rng.standard_normal(n)
    return np.diff(x, prepend=0) * np.exp(-np.arange(n) / SR * 90) * 0.5

def echo(x, d, g):
    k = int(d * SR); y = x.copy()
    y[k:] += g * x[:-k]
    return y

def render_song(bpm, bars, melody, bass_roots, arps, drums, lead_wave, lead_vol,
                duty=0.25, vib=0.0, arp_vol=0.2, bass_vol=0.33, drum_vol=0.5,
                lead_echo=(0.19, 0.22)):
    beat = 60.0 / bpm
    total = int(bars * 4 * beat * SR) + SR // 5
    lead = np.zeros(total); bass = np.zeros(total); arp = np.zeros(total); dr = np.zeros(total)
    # melody: list of bars, each [(midi or None, dur_beats), ...]
    t = 0.0
    for bar in melody:
        for m, d in bar:
            n = int(d * beat * SR * 0.94)
            if m is not None:
                sig = lead_wave(f(m), n, duty, vib) if lead_wave is square else tri(f(m), n, vib)
                lead_seg = sig * env(n) * lead_vol
                place(lead, lead_seg, t)
            t += d * beat
    # bass: per bar root, pattern of 8ths [R,R,5,R,R,5,R,5]
    for bi, root in enumerate(bass_roots):
        pat = [0, 0, 7, 0, 0, 7, 0, 7]
        for k, off in enumerate(pat):
            n = int(0.5 * beat * SR * 0.85)
            place(bass, tri(f(root + off), n) * env(n) * bass_vol, (bi * 4 + k * 0.5) * beat)
    # arp: per bar chord tones 16ths
    for bi, tones in enumerate(arps):
        for k in range(16):
            m = tones[k % len(tones)]
            n = int(0.25 * beat * SR * 0.9)
            place(arp, square(f(m), n, 0.5) * env(n, 0.004, 0.02) * arp_vol, (bi * 4 + k * 0.25) * beat)
    # drums
    if drums:
        for bi in range(bars):
            for b in range(4):
                t0 = (bi * 4 + b) * beat
                if b in (0, 2): place(dr, kick() * 0.9, t0)
                if b in (1, 3): place(dr, snare() * 0.6, t0)
                place(dr, hat(), t0); place(dr, hat() * 0.6, t0 + 0.5 * beat)
    lead = echo(lead, *lead_echo)
    mix = lead + bass + arp + dr * drum_vol
    mix = np.tanh(1.15 * mix)
    mix = mix / np.max(np.abs(mix)) * 0.88
    # ループ用に末尾を短くフェード
    fd = int(0.03 * SR); mix[-fd:] *= np.linspace(1, 0, fd)
    return mix

def save(path, mix):
    data = (mix * 32767).astype(np.int16)
    st = np.column_stack([data, data]).ravel()
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(st.tobytes())

# ---------- nori: 152BPM A major ----------
A_mel = [
 [(76,.5),(74,.5),(73,.5),(71,.5),(69,1),(71,.5),(73,.5)],
 [(74,.5),(73,.5),(71,.5),(69,.5),(66,1),(64,1)],
 [(74,.5),(76,.5),(78,1),(74,.5),(73,.5),(71,1)],
 [(74,.5),(73,.5),(74,.5),(76,.5),(78,1),(81,1)],
 [(81,.5),(78,.5),(76,.5),(73,.5),(76,1),(78,.5),(76,.5)],
 [(74,.5),(76,.5),(73,1),(71,.5),(69,.5),(71,1)],
 [(68,.5),(71,.5),(76,.5),(71,.5),(68,.5),(71,.5),(64,1)],
 [(64,.5),(68,.5),(71,.5),(73,.5),(74,.5),(73,.5),(71,.5),(68,.5)],
]
B_mel = [
 [(81,.5),(83,.5),(81,.5),(78,.5),(76,1),(74,.5),(73,.5)],
 [(76,.5),(74,.5),(76,.5),(78,.5),(81,2)],
 [(78,.5),(81,.5),(83,.5),(81,.5),(78,.5),(76,.5),(74,1)],
 [(76,.5),(78,.5),(81,1),(74,1),(76,1)],
 [(73,.5),(76,.5),(78,.5),(81,.5),(78,.5),(76,.5),(73,.5),(71,.5)],
 [(73,1),(74,.5),(73,.5),(71,.5),(69,.5),(66,1)],
 [(64,.5),(68,.5),(71,.5),(68,.5),(76,1),(74,.5),(73,.5)],
 [(71,.5),(73,.5),(74,.5),(76,.5),(78,.5),(80,.5),(81,1)],
]
prog_roots = [45,45,50,50,42,42,40,40]           # A A D D F#m F#m E E
prog_arps  = [[69,73,76,73],[69,73,76,73],[74,78,81,78],[74,78,81,78],
              [66,69,73,69],[66,69,73,69],[64,68,71,68],[64,68,71,68]]
mel = A_mel + B_mel + A_mel + [b[:] for b in B_mel]
roots = prog_roots * 4
arps = prog_arps * 4
nori = render_song(152, 32, mel, roots, arps, True, square, 0.42, duty=0.25, vib=0.003)
save(f"{OUT}/bgm-nori.wav", nori)

# ---------- shinmiri: 76BPM C major ----------
S_mel = [
 [(76,2),(74,1),(72,1)],
 [(69,2),(72,1),(74,1)],
 [(77,1.5),(76,.5),(74,1),(72,1)],
 [(71,2),(74,1),(79,1)],
 [(79,2),(76,1),(74,1)],
 [(76,1.5),(74,.5),(72,1),(69,1)],
 [(74,2),(72,1),(69,1)],
 [(71,3),(None,1)],
]
S_mel2 = S_mel[:7] + [[(72,4)]]
s_roots = [48,45,41,43] * 2                      # C Am F G
s_arps  = [[60,67,64,67],[57,64,60,64],[53,60,57,60],[55,62,59,62]] * 2
mel_s = S_mel + S_mel2
roots_s = s_roots * 2
arps_s = s_arps * 2
shin = render_song(76, 16, mel_s, roots_s, arps_s, False, tri, 0.5, vib=0.004,
                   arp_vol=0.14, bass_vol=0.26, lead_echo=(0.28, 0.3))
save(f"{OUT}/bgm-shinmiri.wav", shin)
print("done", os.listdir(OUT))
