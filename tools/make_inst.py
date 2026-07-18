#!/usr/bin/env python3
"""歌入りBGMからインスト版を作る（センターキャンセル＋低域復元）。

方式:
  - side = (L-R)/2 … センター定位のボーカルが打ち消される
  - ただしベース/キックもセンターにいるため、mid=(L+R)/2 の低域だけを
    FFTブリックウォール（120-220Hzレイズドコサイン遷移）で取り出して足し戻す
  - 出力: L' = side + bass, R' = -side + bass（ステレオ感は side で維持）

使い方:
  python3 tools/make_inst.py <入力mp3> <出力mp3>
必要: numpy / ffmpeg(libmp3lame)。※ボーカルの残響がうっすら残るのは方式上の限界
"""
import subprocess, sys, os
import numpy as np

SR = 44100
CROSS_LO = 120.0   # この下は完全にmid低域を採用
CROSS_HI = 220.0   # この上はside成分のみ
OUT_GAIN_DB = -1.0 # 最終ピーク

def decode(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-acodec", "pcm_f32le",
         "-ac", "2", "-ar", str(SR), "-"],
        capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)
    return a[:, 0].astype(np.float32), a[:, 1].astype(np.float32)

def lowpass_fft(x, sr, lo, hi):
    """レイズドコサイン遷移のローパス（線形位相・FFT一発）"""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1.0 / sr)
    mask = np.ones_like(f)
    mask[f >= hi] = 0.0
    t = (f > lo) & (f < hi)
    mask[t] = 0.5 * (1 + np.cos(np.pi * (f[t] - lo) / (hi - lo)))
    y = np.fft.irfft(X * mask, n)
    del X
    return y.astype(np.float32)

def main(src, dst):
    L, R = decode(src)
    side = (L - R) * 0.5
    mid = (L + R) * 0.5
    del L, R
    bass = lowpass_fft(mid, SR, CROSS_LO, CROSS_HI)
    del mid
    outL = side + bass
    outR = -side + bass
    del side, bass
    peak = max(np.abs(outL).max(), np.abs(outR).max(), 1e-9)
    g = (10 ** (OUT_GAIN_DB / 20)) / peak
    inter = np.empty(outL.size * 2, dtype=np.float32)
    inter[0::2] = outL * g
    inter[1::2] = outR * g
    p = subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-",
         "-codec:a", "libmp3lame", "-q:a", "3", dst],
        input=inter.tobytes(), check=True)
    print("wrote", dst, os.path.getsize(dst), "bytes")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
