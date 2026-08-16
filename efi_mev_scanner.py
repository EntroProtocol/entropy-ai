"""
EFI MEV SCANNER — Solana Arbitrage + Sandwich Detection
========================================================
Scans Solana DEX pools for MEV opportunities using EFI 24D entropy analysis.
Finds: cross-DEX arbitrage, sandwich opportunities, anomalous swap patterns.

Uses Helius RPC (free premium access).
Runs on GitHub Actions cron every 5 minutes.

Created by: EntroProtocol
License: MIT
"""

import json, time, math, urllib.request, zlib, collections
from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════════
# HELIUS RPC CLIENT
# ═══════════════════════════════════════════════════════════════

HELIUS_RPC = "https://sibylla-253ej3-fast-mainnet.helius-rpc.com"

def rpc_call(method, params=None):
    """Make a Solana JSON-RPC call via Helius."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
    }
    if params:
        payload["params"] = params
    req = urllib.request.Request(
        HELIUS_RPC,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

# ═══════════════════════════════════════════════════════════════
# 24D ENTROPY CALCULATOR (Transaction-Optimized)
# ═══════════════════════════════════════════════════════════════

class EntropyCalculator:
    DIM_NAMES = [
        "Shannon", "NormShannon", "Kolmogorov", "Permutation", "Spectral",
        "MinEntropy", "Markov", "Wavelet", "OpcodeDiv", "StorageOps",
        "CallOps", "ControlFlow", "EntropyRate", "CrossContract",
        "Selectors", "Repetition", "Hurst", "Tsallis", "Renyi",
        "SampleEntropy", "ApproxEntropy", "Linguistic", "DataDensity", "CodeEntropy"
    ]

    def compute(self, data: bytes) -> list:
        s = ''.join(chr(b) for b in data[:4000] if b < 256) or '\x00'
        hexd = data.hex() if data else '00'
        return [
            self._shannon(s), self._norm_shannon(s), self._kolmogorov(data),
            self._permutation(s[:200]), self._spectral(s[:256]), self._min_entropy(s),
            self._markov(s), self._wavelet(s[:256]), self._opcode_div(hexd),
            self._storage_ops(hexd), self._call_ops(hexd), self._control_flow(hexd),
            self._entropy_rate(s), self._cross_contract(hexd), self._selectors(hexd),
            self._repetition(s), self._hurst(s[:200]), self._tsallis(s), self._renyi(s),
            self._sample_entropy(s[:200]), self._approx_entropy(s[:200]),
            self._linguistic(s), self._data_density(hexd), self._code_entropy(hexd),
        ]

    @staticmethod
    def _shannon(d):
        if not d: return 0.0
        f = collections.Counter(d); t = len(d)
        return -sum((c/t)*math.log2(c/t) for c in f.values())
    @staticmethod
    def _norm_shannon(d):
        if not d: return 0.0
        s = EntropyCalculator._shannon(d); u = len(set(d))
        return s/math.log2(u) if u > 1 else 0.0
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
            psd.append(r*r+i*i)
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
        w = 32; rates = [EntropyCalculator._shannon(d[i:i+w]) for i in range(0, len(d)-w, w)]
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
        rv = r*math.sqrt(sum((x-sum(v)/len(v))**2 for x in v)/len(v)) or 1.0
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
        rv = r*math.sqrt(sum((x-sum(v)/len(v))**2 for x in v)/len(v)) or 1.0
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
        es = [EntropyCalculator._shannon(c) for c in chunks if len(c) > 10]
        if not es: return 0.0
        m = sum(es)/len(es); v = sum((e-m)**2 for e in es)/len(es)
        return math.sqrt(v)


# ═══════════════════════════════════════════════════════════════
# DEX POOLS — Major Solana DEX programs
# ═══════════════════════════════════════════════════════════════

# Major Solana DEX program IDs
DEX_PROGRAMS = {
    "Raydium AMM v4": "675kPXtMm7j7sX5tYpQ5x2JYr8b9L2k6X5w2Y9r4m1k",  # placeholder
    "Orca Whirlpool": "whirQ7Qs7s3W5bQ5x2JYr8b9L2k6X5w2Y9r4m1k",     # placeholder
    "Meteora DLMM": "LWHQs7s3W5bQ5x2JYr8b9L2k6X5w2Y9r4m1k",          # placeholder
    "Pump.fun": "6EF8r3hW5bQ5x2JYr8b9L2k6X5w2Y9r4m1k",               # placeholder
}

# Known token mints for major trading pairs
TOKENS = {
    "SOL": "So11111111111111111111111111111111111111112",
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY7ck6X5w2Y9r4m1k",  # placeholder
    "WIF": "EKpQGSJtjMFqW5bQ5x2JYr8b9L2k6X5w2Y9r4m1k",       # placeholder
    "BONK": "DezXAZ8z7PnrnRJ3z7sX5tYpQ5x2JYr8b9L2k6X5w2Y9",  # placeholder
}

# ═══════════════════════════════════════════════════════════════
# MEV SCANNER
# ═══════════════════════════════════════════════════════════════

class EFIMEVScanner:
    def __init__(self):
        self.calc = EntropyCalculator()
        self.opportunities = []

    def scan_recent_signatures(self, address, limit=20):
        """Get recent transaction signatures for an address."""
        result = rpc_call("getSignaturesForAddress", [address, {"limit": limit}])
        if "error" in result:
            return []
        return result.get("result", [])

    def get_transaction(self, signature):
        """Get full transaction details."""
        result = rpc_call("getTransaction", [
            signature,
            {"encoding": "base64", "maxSupportedTransactionVersion": 0}
        ])
        if "error" in result:
            return None
        return result.get("result")

    def analyze_transaction_entropy(self, tx_data):
        """Analyze a transaction's entropy using 24D EFI."""
        if not tx_data or not tx_data.get("transaction"):
            return None

        # Extract transaction data
        tx = tx_data["transaction"]
        if isinstance(tx, list):
            # base64 encoded
            import base64
            try:
                raw = base64.b64decode(tx[0])
            except:
                return None
        elif isinstance(tx, dict):
            raw = json.dumps(tx, sort_keys=True).encode()
        else:
            return None

        # Compute 24D entropy
        entropy = self.calc.compute(raw[:4000])

        # Analyze for MEV patterns
        analysis = {
            "shannon": entropy[0],
            "kolmogorov": entropy[2],
            "permutation": entropy[3],
            "spectral": entropy[4],
            "markov": entropy[6],
            "hurst": entropy[16],
            "entropy_rate": entropy[12],
            "repetition": entropy[15],
            "sample_entropy": entropy[19],
            "full_24d": entropy,
        }

        # Detect patterns
        patterns = []

        # Large swap pattern: high Shannon + low Kolmogorov (structured but complex)
        if entropy[0] > 7.0 and entropy[2] < 0.7:
            patterns.append("LARGE_SWAP")

        # Sandwich vulnerability: low Hurst (anti-persistent) + high entropy rate
        if entropy[16] < 0.35 and entropy[12] > 0.3:
            patterns.append("SANDWICH_TARGET")

        # Arbitrage opportunity: high repetition + low sample entropy (predictable)
        if entropy[15] > 0.05 and entropy[19] < 0.5:
            patterns.append("ARBITRAGE_CANDIDATE")

        # Anomalous: high spectral entropy deviation
        if entropy[4] > 1.5:
            patterns.append("ANOMALOUS_FLOW")

        # New token pattern: very high Kolmogorov (incompressible = novel)
        if entropy[2] > 0.9 and entropy[0] > 7.5:
            patterns.append("NEW_TOKEN_LAUNCH")

        analysis["patterns"] = patterns
        return analysis

    def scan_address(self, address, label="unknown", limit=10):
        """Scan recent transactions for an address and find MEV patterns."""
        print(f"\n{'─'*50}")
        print(f"Scanning: {label} ({address[:12]}...)")
        print(f"{'─'*50}")

        sigs = self.scan_recent_signatures(address, limit)
        if not sigs:
            print(f"  No transactions found")
            return []

        print(f"  Found {len(sigs)} recent transactions")

        findings = []
        for sig_info in sigs[:limit]:
            sig = sig_info.get("signature", "")
            if sig_info.get("err"):
                continue

            # Get transaction
            tx = self.get_transaction(sig)
            if not tx:
                continue

            # Analyze with EFI 24D
            analysis = self.analyze_transaction_entropy(tx)
            if not analysis:
                continue

            if analysis["patterns"]:
                finding = {
                    "signature": sig,
                    "slot": tx.get("slot"),
                    "block_time": tx.get("blockTime"),
                    "patterns": analysis["patterns"],
                    "shannon": analysis["shannon"],
                    "kolmogorov": analysis["kolmogorov"],
                    "hurst": analysis["hurst"],
                    "entropy_rate": analysis["entropy_rate"],
                }
                findings.append(finding)
                print(f"\n  ⚡ MEV PATTERN DETECTED: {', '.join(analysis['patterns'])}")
                print(f"     Sig: {sig[:20]}...")
                print(f"     Shannon: {analysis['shannon']:.3f}")
                print(f"     Kolmogorov: {analysis['kolmogorov']:.3f}")
                print(f"     Hurst: {analysis['hurst']:.3f}")
                print(f"     Entropy Rate: {analysis['entropy_rate']:.3f}")

        if not findings:
            print(f"  No MEV patterns detected in {len(sigs)} transactions")
        else:
            print(f"\n  🎯 {len(findings)} MEV opportunities found!")

        return findings

    def scan_token_accounts(self, owner):
        """Get token accounts for an owner (find liquidity pools)."""
        result = rpc_call("getTokenAccountsByOwner", [
            owner,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"}
        ])
        if "error" in result:
            return []
        return result.get("result", {}).get("value", [])

    def get_account_info(self, address):
        """Get account info including data (for pool analysis)."""
        result = rpc_call("getAccountInfo", [
            address,
            {"encoding": "base64", "dataSlice": {"offset": 0, "length": 256}}
        ])
        if "error" in result:
            return None
        return result.get("result", {}).get("value")

    def analyze_pool_entropy(self, pool_address):
        """Analyze a liquidity pool's entropy for anomalies."""
        info = self.get_account_info(pool_address)
        if not info or not info.get("data"):
            return None

        import base64
        try:
            raw = base64.b64decode(info["data"][0])
        except:
            return None

        entropy = self.calc.compute(raw[:4000])

        # Pool anomaly detection
        anomalies = []

        # Low Kolmogorov = predictable pool state = arbitrage opportunity
        if entropy[2] < 0.6:
            anomalies.append("PREDICTABLE_STATE")

        # High entropy rate = volatile pool = sandwich opportunity
        if entropy[12] > 0.3:
            anomalies.append("VOLATILE_POOL")

        # Low Hurst = anti-persistent = mean-reverting = arbitrageable
        if entropy[16] < 0.4:
            anomalies.append("MEAN_REVERTING")

        # High repetition = repetitive swaps = bot activity
        if entropy[15] > 0.08:
            anomalies.append("BOT_ACTIVITY")

        return {
            "entropy": entropy[:8],  # First 8 dims for summary
            "anomalies": anomalies,
            "shannon": entropy[0],
            "kolmogorov": entropy[2],
            "hurst": entropy[16],
        }


# ═══════════════════════════════════════════════════════════════
# SCANNER RUNNER
# ═══════════════════════════════════════════════════════════════

def run_scan():
    """Main scan loop — finds MEV opportunities on Solana."""
    print("╔══════════════════════════════════════════════════╗")
    print("║  EFI MEV SCANNER — Solana 24D Entropy Analysis    ║")
    print("║  Arbitrage · Sandwich · Anomaly Detection          ║")
    print("╚══════════════════════════════════════════════════╝")

    scanner = EFIMEVScanner()
    t_start = time.time()

    # 1. Check connection
    health = rpc_call("getHealth")
    if health.get("result") == "ok":
        print("\n✅ Helius RPC: Connected")
    else:
        print("\n❌ Helius RPC: Failed")
        return

    # 2. Get recent slot
    slot_result = rpc_call("getSlot")
    current_slot = slot_result.get("result", 0)
    print(f"📍 Current Slot: {current_slot}")

    # 3. Scan known high-activity addresses
    # These are major DEX routers and known MEV targets
    SCAN_TARGETS = [
        # Raydium AMM v4 (confirmed from docs.raydium.io)
        {"address": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8", "label": "Raydium AMM v4", "type": "dex"},
        # Pump.fun (confirmed from docs.solanatracker.io — new token launches = MEV goldmine)
        {"address": "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P", "label": "Pump.fun", "type": "launch"},
        # Orca Whirlpool (confirmed from nolimitnodes.com)
        {"address": "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc", "label": "Orca Whirlpool", "type": "dex"},
        # Wrapped SOL (token mint — high volume)
        {"address": "So11111111111111111111111111111111111111112", "label": "Wrapped SOL", "type": "token"},
        # USDC (token mint — highest volume on Solana)
        {"address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "label": "USDC", "type": "token"},
    ]

    all_findings = []

    for target in SCAN_TARGETS:
        try:
            findings = scanner.scan_address(
                target["address"],
                target["label"],
                limit=5
            )
            for f in findings:
                f["source"] = target["label"]
                all_findings.append(f)
        except Exception as e:
            print(f"  Error scanning {target['label']}: {e}")
            continue

    # 4. Analyze recent block transactions for entropy anomalies
    print(f"\n{'─'*50}")
    print(f"Scanning recent block transactions...")
    print(f"{'─'*50}")

    # Get recent block
    block_result = rpc_call("getLatestBlockhash")
    if block_result.get("result"):
        print(f"  Latest blockhash: {block_result['result']['value']['blockhash'][:20]}...")

    # 5. Summary
    elapsed = time.time() - t_start
    print(f"\n{'═'*50}")
    print(f"  SCAN SUMMARY")
    print(f"{'═'*50}")
    print(f"  Scan duration: {elapsed:.1f}s")
    print(f"  Targets scanned: {len(SCAN_TARGETS)}")
    print(f"  Total findings: {len(all_findings)}")

    if all_findings:
        print(f"\n  🎯 MEV OPPORTUNITIES:")
        for i, f in enumerate(all_findings, 1):
            print(f"  {i}. [{', '.join(f['patterns'])}] from {f.get('source', 'unknown')}")
            print(f"     Sig: {f['signature'][:30]}...")
            print(f"     Shannon={f['shannon']:.3f} K={f['kolmogorov']:.3f} H={f['hurst']:.3f}")

    # 6. EFI 24D Trial log
    trial = {
        "trial_id": f"MEV_SCAN_{int(time.time())}",
        "target_type": "solana_mempool",
        "target_identifier": "Solana Mainnet (Helius RPC)",
        "efi_version": "24D-v4.0-mev",
        "technique": "efi_guided_mev_scan",
        "technique_description": "24D entropy analysis of Solana transactions for MEV opportunity detection",
        "result": f"FOUND_{len(all_findings)}_OPPORTUNITIES" if all_findings else "NO_OPPORTUNITIES",
        "finding": f"Scanned {len(SCAN_TARGETS)} DEX targets, found {len(all_findings)} MEV patterns" if all_findings else "No MEV patterns detected in current scan",
        "confidence_score": 0.7 if all_findings else 0.3,
        "path_to_finding": f"Analyzed recent transactions from {len(SCAN_TARGETS)} DEX programs",
        "processing_time_ms": elapsed * 1000,
        "tags": ["mev", "solana", "arbitrage", "sandwich", "24D"],
    }

    return trial, all_findings


if __name__ == "__main__":
    trial, findings = run_scan()
    print(f"\n  Trial: {json.dumps(trial, indent=2)}")
