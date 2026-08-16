"""
EFI PIXEL SCANNER v2 — 24D Entropy Microscope
=============================================
Scans images at pixel-block level using 24D entropy analysis.
Detects: AI-generated images, steganography, manipulation, deepfakes.

Created by: EntroProtocol
License: MIT
"""

import math, zlib, collections, time
import numpy as np
from PIL import Image
from typing import Dict, List, Tuple

class PixelEntropyCalculator:
    DIM_NAMES = ["Shannon","NormShannon","Kolmogorov","Permutation","Spectral",
                 "MinEntropy","Markov","Wavelet","OpcodeDiv","StorageOps","CallOps",
                 "ControlFlow","EntropyRate","CrossContract","Selectors","Repetition",
                 "Hurst","Tsallis","Renyi","SampleEntropy","ApproxEntropy",
                 "Linguistic","DataDensity","CodeEntropy"]

    def compute_block(self, block: np.ndarray) -> np.ndarray:
        flat = block.flatten()
        bdata = bytes(flat.tolist())
        s = ''.join(chr(b) for b in flat[:4000] if b < 256) or '\x00'
        hexd = bdata.hex() if bdata else '00'
        return np.array([
            self._shannon(s), self._norm_shannon(s), self._kolmogorov(bdata),
            self._permutation(s[:200]), self._spectral(s[:256]), self._min_entropy(s),
            self._markov(s), self._wavelet(s[:256]), self._opcode_div(hexd),
            self._storage_ops(hexd), self._call_ops(hexd), self._control_flow(hexd),
            self._entropy_rate(s), self._cross_contract(hexd), self._selectors(hexd),
            self._repetition(s), self._hurst(s[:200]), self._tsallis(s), self._renyi(s),
            self._sample_entropy(s[:200]), self._approx_entropy(s[:200]),
            self._linguistic(s), self._data_density(hexd), self._code_entropy(hexd),
        ], dtype=np.float64)

    @staticmethod
    def _shannon(d):
        if not d: return 0.0
        f = collections.Counter(d); t = len(d)
        return -sum((c/t)*math.log2(c/t) for c in f.values())
    @staticmethod
    def _norm_shannon(d):
        if not d: return 0.0
        s = PixelEntropyCalculator._shannon(d); u = len(set(d))
        m = math.log2(u) if u > 1 else 1.0
        return s/m if m > 0 else 0.0
    @staticmethod
    def _kolmogorov(d):
        if not d: return 0.0
        try: return len(zlib.compress(d))/max(len(d),1)
        except: return 0.0
    @staticmethod
    def _permutation(d, order=3):
        if len(d) < order+1: return 0.0
        v = [ord(c) for c in d[:200]]; patterns = []
        for i in range(len(v)-order):
            w = v[i:i+order+1]
            patterns.append(tuple(sorted(range(len(w)), key=lambda x: w[x])))
        if not patterns: return 0.0
        f = collections.Counter(patterns); t = len(patterns)
        return -sum((c/t)*math.log2(c/t) for c in f.values())
    @staticmethod
    def _spectral(d):
        if not d or len(d) < 8: return 0.0
        v = [ord(c) for c in d[:256]]; n = min(len(v), 32); psd = []
        for k in range(n):
            r = sum(v[j]*math.cos(2*math.pi*k*j/n) for j in range(n))
            i = -sum(v[j]*math.sin(2*math.pi*k*j/n) for j in range(n))
            psd.append(r**2+i**2)
        t = sum(psd)
        return -sum((p/t)*math.log2(p/t+1e-10) for p in psd if p > 0) if t > 0 else 0.0
    @staticmethod
    def _min_entropy(d):
        if not d: return 0.0
        f = collections.Counter(d); mx = max(f.values())/len(d)
        return -math.log2(mx) if mx > 0 else 0.0
    @staticmethod
    def _markov(d):
        if len(d) < 4: return 0.0
        trans = collections.defaultdict(int); total = 0
        for i in range(len(d)-2): trans[(d[i],d[i+1])] += 1; total += 1
        return -sum((c/total)*math.log2(c/total) for c in trans.values()) if total > 0 else 0.0
    @staticmethod
    def _wavelet(d):
        if len(d) < 8: return 0.0
        v = [ord(c) for c in d[:256]]
        detail = [(v[i]-v[i+1])/2 for i in range(0, len(v)-1, 2)]
        return math.log2(sum(x*x for x in detail)+1)
    @staticmethod
    def _opcode_div(h):
        return float(len(set(h[i:i+2] for i in range(0, len(h)-2, 2))))
    @staticmethod
    def _storage_ops(h): return float(h.count("54")+h.count("55"))
    @staticmethod
    def _call_ops(h): return float(h.count("f1")+h.count("fa")+h.count("f4"))
    @staticmethod
    def _control_flow(h): return float(h.count("56")+h.count("57")+h.count("5b"))
    @staticmethod
    def _entropy_rate(d):
        if len(d) < 64: return 0.0
        w = 32; rates = [PixelEntropyCalculator._shannon(d[i:i+w]) for i in range(0, len(d)-w, w)]
        if not rates: return 0.0
        m = sum(rates)/len(rates); v = sum((r-m)**2 for r in rates)/len(rates)
        return math.sqrt(v)
    @staticmethod
    def _cross_contract(h):
        c = h.count("f1")+h.count("f4")+h.count("fa")
        return h.count("f4")/c if c > 0 else 0.0
    @staticmethod
    def _selectors(h): return float(h.count("63"))
    @staticmethod
    def _repetition(d):
        if len(d) < 10: return 0.0
        b = collections.Counter(d[i:i+2] for i in range(len(d)-1))
        t = sum(b.values()); return sum((c/t)**2 for c in b.values()) if t > 0 else 0.0
    @staticmethod
    def _hurst(d):
        if len(d) < 100: return 0.5
        v = [ord(c) for c in d[:200]]; n = len(v); m = sum(v)/n
        dev = [x-m for x in v]; cum = [sum(dev[:i+1]) for i in range(n)]
        R = max(cum)-min(cum); s = math.sqrt(sum(x**2 for x in dev)/n)
        return math.log(R/s)/math.log(n) if s > 0 and R > 0 else 0.5
    @staticmethod
    def _tsallis(d, q=2):
        if not d: return 0.0
        f = collections.Counter(d); t = len(d)
        return (1-sum((c/t)**q for c in f.values()))/(q-1)
    @staticmethod
    def _renyi(d, alpha=2):
        if not d: return 0.0
        f = collections.Counter(d); t = len(d)
        return 1/(1-alpha)*math.log2(sum((c/t)**alpha for c in f.values())+1e-10)
    @staticmethod
    def _sample_entropy(d, m=2, r=0.2):
        if len(d) < m+1: return 0.0
        v = [ord(c) for c in d[:200]]
        rv = r*np.std(v) if np.std(v) > 0 else 1.0
        def _c(mv):
            ps = [tuple(v[i:i+mv]) for i in range(len(v)-mv)]; cnt = 0
            for i in range(len(ps)):
                for j in range(i+1, len(ps)):
                    if max(abs(a-b) for a,b in zip(ps[i],ps[j])) <= rv: cnt += 1
            return cnt
        A = _c(m+1); B = _c(m)
        return -math.log(A/B+1e-10) if B > 0 else 0.0
    @staticmethod
    def _approx_entropy(d, m=2, r=0.2):
        if len(d) < m+2: return 0.0
        v = [ord(c) for c in d[:200]]
        rv = r*np.std(v) if np.std(v) > 0 else 1.0
        def _p(mv):
            ps = [tuple(v[i:i+mv]) for i in range(len(v)-mv)]; cs = []
            for p in ps:
                c = sum(1 for q in ps if max(abs(a-b) for a,b in zip(p,q)) <= rv)
                cs.append(math.log(c/len(ps)+1e-10))
            return sum(cs)/len(cs) if cs else 0.0
        return _p(m)-_p(m+1)
    @staticmethod
    def _linguistic(d): return len(set(d))/len(d) if d else 0.0
    @staticmethod
    def _data_density(h): return sum(1 for c in h if c != '0')/len(h) if h else 0.0
    @staticmethod
    def _code_entropy(h):
        if len(h) < 100: return 0.0
        chunks = [h[i:i+100] for i in range(0, len(h), 100)]
        es = [PixelEntropyCalculator._shannon(c) for c in chunks if len(c) > 10]
        return float(np.std(es)) if es else 0.0


class EFIPixelScanner:
    def __init__(self, block_size=16):
        self.calc = PixelEntropyCalculator()
        self.block_size = block_size

    def scan_image_file(self, filepath: str) -> Dict:
        """Scan an image file."""
        img = Image.open(filepath)
        width, height = img.size
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return self.scan_image(img.tobytes(), width, height, 3)

    def scan_image(self, image_data: bytes, width: int, height: int, channels=3) -> Dict:
        bs = self.block_size
        blocks_x = width // bs
        blocks_y = height // bs
        img = np.frombuffer(image_data, dtype=np.uint8).reshape(height, width, channels)

        entropy_map = np.zeros((blocks_y, blocks_x, 24))
        for by in range(blocks_y):
            for bx in range(blocks_x):
                block = img[by*bs:(by+1)*bs, bx*bs:(bx+1)*bs]
                entropy_map[by, bx] = self.calc.compute_block(block)

        global_means = np.mean(entropy_map, axis=(0,1))
        global_stds = np.std(entropy_map, axis=(0,1))

        # Anomaly detection: z-score per block
        anomaly_map = np.zeros((blocks_y, blocks_x))
        anomaly_blocks = []
        for by in range(blocks_y):
            for bx in range(blocks_x):
                vec = entropy_map[by, bx]
                z = np.abs((vec - global_means) / (global_stds + 1e-10))
                max_z = np.max(z)
                anomaly_map[by, bx] = max_z
                if max_z > 3.0:
                    anom_dims = [self.calc.DIM_NAMES[i] for i in range(24) if z[i] > 3.0]
                    anomaly_blocks.append({
                        'x': bx, 'y': by, 'max_z': float(max_z),
                        'anomalous_dims': anom_dims
                    })

        classification = self._classify(entropy_map, global_means, global_stds, anomaly_blocks)

        return {
            'block_size': bs, 'blocks_x': blocks_x, 'blocks_y': blocks_y,
            'total_blocks': blocks_x * blocks_y, 'entropy_map': entropy_map,
            'anomaly_map': anomaly_map, 'global_means': global_means,
            'global_stds': global_stds, 'anomaly_blocks': anomaly_blocks,
            'anomaly_count': len(anomaly_blocks),
            'anomaly_ratio': len(anomaly_blocks) / max(blocks_x * blocks_y, 1),
            'classification': classification
        }

    def _classify(self, entropy_map, means, stds, anomalies) -> Dict:
        avg_std = float(np.mean(stds))
        anomaly_ratio = len(anomalies) / max(entropy_map.shape[0]*entropy_map.shape[1], 1)
        shannon_mean, shannon_std = float(means[0]), float(stds[0])
        kolmogorov_mean, kolmogorov_std = float(means[2]), float(stds[2])
        permutation_mean, permutation_std = float(means[3]), float(stds[3])
        spectral_mean, spectral_std = float(means[4]), float(stds[4])
        markov_mean, markov_std = float(means[6]), float(stds[6])
        hurst_mean = float(means[16])
        entropy_rate_mean = float(means[12])
        linguistic_mean, linguistic_std = float(means[21]), float(stds[21])

        findings = []
        verdict = "NATURAL"
        confidence = 0.0
        reasons = []

        # AI-GENERATED: smooth, compressible, low absolute entropy
        # AI images (diffusion/GAN) have smooth gradients → highly compressible → low Kolmogorov
        # and lower absolute Shannon entropy (less randomness in pixel values)
        ai_score = 0
        if kolmogorov_mean < 0.65:
            ai_score += 2
            reasons.append(f"low algorithmic complexity (K={kolmogorov_mean:.3f}) — highly compressible, smooth texture")
        elif kolmogorov_mean < 0.75:
            ai_score += 1

        if shannon_mean < 5.5:
            ai_score += 2
            reasons.append(f"low Shannon entropy (H={shannon_mean:.3f}) — limited pixel value diversity")
        elif shannon_mean < 6.0:
            ai_score += 1

        if permutation_mean < 2.5:
            ai_score += 1
            reasons.append("low permutation entropy — repetitive local order patterns")

        if avg_std < 0.5:
            ai_score += 1
            reasons.append("low entropy variance across blocks — uniform texture")

        if ai_score >= 4:
            verdict = "AI_GENERATED"
            confidence = min(0.55 + ai_score * 0.07, 0.95)
            findings.append(f"AI-GENERATED signature: {', '.join(reasons)}")

        # STEGANOGRAPHY: clustered anomalies in specific region
        if 0.05 < anomaly_ratio < 0.35 and len(anomalies) >= 2:
            clustered = self._check_clustering(anomalies)
            if clustered:
                if verdict == "NATURAL":
                    verdict = "STEGANOGRAPHY"
                findings.append(f"Clustered anomalies in {len(anomalies)} blocks — possible hidden data embedding")
                confidence = max(confidence, 0.65)

        # MANIPULATION: isolated anomaly with spectral deviation
        if 0.02 < anomaly_ratio < 0.20 and spectral_std > 0.5:
            if verdict == "NATURAL":
                verdict = "MANIPULATED"
            findings.append(f"Localized spectral anomaly — possible region manipulation ({len(anomalies)} blocks)")
            confidence = max(confidence, 0.55)

        # DEEPFAKE: anti-persistent + high local variation
        if hurst_mean < 0.35 and entropy_rate_mean > 0.3 and permutation_std > 0.3:
            if verdict == "NATURAL":
                verdict = "DEEPFAKE_SUSPECT"
            findings.append(f"Anti-persistent entropy (H={hurst_mean:.3f}) with high local variation — possible face-swap boundary")
            confidence = max(confidence, 0.50)

        # NATURAL: high absolute entropy, high Kolmogorov (incompressible = noisy = real)
        if kolmogorov_mean > 0.80 and shannon_mean > 6.0 and not findings:
            verdict = "NATURAL"
            findings.append(f"High entropy + incompressible (K={kolmogorov_mean:.3f}, H={shannon_mean:.3f}) — consistent with real photography noise")
            confidence = max(confidence, 0.65)

        if not findings:
            findings.append("Entropy profile within normal parameters — no significant anomalies")
            confidence = 0.50

        return {
            'verdict': verdict,
            'confidence': round(confidence, 4),
            'findings': findings,
            'metrics': {
                'avg_entropy_std': round(avg_std, 4),
                'shannon_mean': round(shannon_mean, 4), 'shannon_std': round(shannon_std, 4),
                'kolmogorov_mean': round(kolmogorov_mean, 4), 'kolmogorov_std': round(kolmogorov_std, 4),
                'permutation_mean': round(permutation_mean, 4), 'permutation_std': round(permutation_std, 4),
                'spectral_mean': round(spectral_mean, 4), 'spectral_std': round(spectral_std, 4),
                'markov_mean': round(markov_mean, 4), 'markov_std': round(markov_std, 4),
                'hurst_mean': round(hurst_mean, 4),
                'entropy_rate_mean': round(entropy_rate_mean, 4),
                'linguistic_mean': round(linguistic_mean, 4),
                'anomaly_ratio': round(anomaly_ratio, 4)
            }
        }

    def _check_clustering(self, anomalies) -> bool:
        if len(anomalies) < 3: return False
        coords = [(a['x'], a['y']) for a in anomalies]
        # Count blocks that have at least one adjacent neighbor (distance <= 1)
        clustered_blocks = 0
        for i, (x1, y1) in enumerate(coords):
            has_neighbor = False
            for j, (x2, y2) in enumerate(coords):
                if i != j and abs(x1-x2) <= 1 and abs(y1-y2) <= 1:
                    has_neighbor = True
                    break
            if has_neighbor: clustered_blocks += 1
        # At least 60% of anomalies must be in a cluster
        return clustered_blocks >= max(3, len(anomalies) * 0.6)

    def heatmap_ascii(self, anomaly_map) -> str:
        chars = ' .:-=+*#%@'
        h, w = anomaly_map.shape
        lines = []
        for y in range(h):
            line = ''
            for x in range(w):
                v = min(anomaly_map[y, x] / 5.0, 1.0)
                line += chars[int(v * (len(chars)-1))]
            lines.append(line)
        return '\n'.join(lines)


def run_trial(scanner, filepath, label):
    t0 = time.time()
    result = scanner.scan_image_file(filepath)
    elapsed = (time.time() - t0) * 1000
    trial = {
        'trial_id': f"PIXEL_{label}_{int(time.time())}",
        'target_type': 'image',
        'target_identifier': f"{label} ({filepath})",
        'efi_version': '24D-v4.0-pixel',
        'dimensions_used': PixelEntropyCalculator.DIM_NAMES,
        'technique': 'pixel_block_entropy_scan',
        'technique_description': f'24D entropy per {scanner.block_size}x{scanner.block_size} pixel block, z-score anomaly detection',
        'result': result['classification']['verdict'],
        'finding': '; '.join(result['classification']['findings']),
        'confidence_score': result['classification']['confidence'],
        'path_to_finding': f"Scanned {result['total_blocks']} blocks, {result['anomaly_count']} anomalies ({result['anomaly_ratio']:.1%})",
        'keys_used': f"block_size={scanner.block_size}, file={filepath}",
        'data_size': result.get('data_size', 0),
        'processing_time_ms': round(elapsed, 1),
        'tags': ['pixel_scan', 'image_analysis', 'steganography', 'ai_detection', '24D']
    }
    return trial, result


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════╗")
    print("║  EFI PIXEL SCANNER v2 — 24D Entropy Microscope    ║")
    print("║  Pixel-level analysis · 24 dimensions per block    ║")
    print("╚══════════════════════════════════════════════════╝\n")

    scanner = EFIPixelScanner(block_size=16)
    tests = [
        ('test_natural.png', 'natural_photo'),
        ('test_ai.png', 'ai_generated'),
        ('test_stego.png', 'steganography'),
        ('test_manip.png', 'manipulated'),
    ]

    all_trials = []
    for filepath, label in tests:
        print(f"{'═'*52}")
        print(f"  TRIAL: {label}")
        print(f"{'═'*52}")
        trial, result = run_trial(scanner, filepath, label)
        all_trials.append(trial)
        c = result['classification']
        print(f"  Verdict:    {c['verdict']}")
        print(f"  Confidence: {c['confidence']:.1%}")
        print(f"  Blocks:     {result['total_blocks']}")
        print(f"  Anomalies:  {result['anomaly_count']} ({result['anomaly_ratio']:.1%})")
        print(f"  Time:       {trial['processing_time_ms']:.0f}ms")
        print(f"  Findings:")
        for f in c['findings']:
            print(f"    • {f}")
        m = c['metrics']
        print(f"  Key 24D metrics:")
        print(f"    Shannon:     {m['shannon_mean']:.3f} ± {m['shannon_std']:.3f}")
        print(f"    Kolmogorov:  {m['kolmogorov_mean']:.3f} ± {m['kolmogorov_std']:.3f}")
        print(f"    Permutation: {m['permutation_mean']:.3f} ± {m['permutation_std']:.3f}")
        print(f"    Spectral:    {m['spectral_mean']:.3f} ± {m['spectral_std']:.3f}")
        print(f"    Markov:      {m['markov_mean']:.3f} ± {m['markov_std']:.3f}")
        print(f"    Hurst:       {m['hurst_mean']:.3f}")
        print(f"    EntropyRate: {m['entropy_rate_mean']:.3f}")
        print(f"    AvgStd:      {m['avg_entropy_std']:.3f}")
        print(f"\n  Anomaly heatmap (darker=normal, brighter=anomaly):")
        print(f"  {'─'*36}")
        for line in scanner.heatmap_ascii(result['anomaly_map']).split('\n'):
            print(f"  {line}")
        print(f"  {'─'*36}\n")

    print(f"\n{'═'*52}")
    print(f"  SUMMARY — {len(all_trials)} trials completed")
    print(f"{'═'*52}")
    for t in all_trials:
        print(f"  {t['target_identifier']:30s} → {t['result']:20s} ({t['confidence_score']:.0%}) [{t['processing_time_ms']:.0f}ms]")
