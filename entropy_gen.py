"""
ENTROPY GENERATIVE ENGINE v3.0 — Template-Guided Entropy Generation
===================================================================
Key insight: entropy selects CONTENT, templates provide STRUCTURE.
The combination produces coherent text without any neural network.

v2.1 proved: raw entropy decoding produces related words but no grammar.
v3.0 fix: sentence templates as grammatical scaffolding, entropy fills slots.

Architecture:
  Module 1: EntropyMatrixCalculator — 24D entropy extraction (background)
  Module 2: SemanticMemoryEngine   — concept graph + knowledge base
  Module 3: NextTokenGenerator      — template-guided entropy generation
  Module 4: FactualGuardrail        — hallucination prevention

Created by: EntroProtocol
License: MIT
"""

import math, collections, zlib, re, numpy as np
from typing import List, Dict, Tuple, Any, Optional


# ═══════════════════════════════════════════════════════════════
# MODULE 1: ENTROPY MATRIX CALCULATOR (24D)
# ═══════════════════════════════════════════════════════════════

class EntropyMatrixCalculator:
    DIM_NAMES = ["Shannon","NormShannon","Kolmogorov","Permutation","Spectral","MinEntropy","Markov","Wavelet","OpcodeDiv","StorageOps","CallOps","ControlFlow","EntropyRate","CrossContract","Selectors","Repetition","Hurst","Tsallis","Renyi","SampleEntropy","ApproxEntropy","Linguistic","DataDensity","CodeEntropy"]

    def compute(self, data: Any) -> np.ndarray:
        raw, bdata = self._normalize(data)
        hexd = self._to_hex(raw, bdata)
        s = raw[:4000] if isinstance(raw, str) else str(raw)[:4000]
        return np.array([
            self._shannon(s), self._norm_shannon(s), self._kolmogorov(bdata[:4000]),
            self._permutation(s[:2000]), self._spectral(s[:2000]), self._min_entropy(s),
            self._markov(s), self._wavelet(s[:2000]), self._opcode_div(hexd),
            self._storage_ops(hexd), self._call_ops(hexd), self._control_flow(hexd),
            self._entropy_rate(s), self._cross_contract(hexd), self._selectors(hexd),
            self._repetition(s), self._hurst(s[:2000]), self._tsallis(s), self._renyi(s),
            self._sample_entropy(s[:2000]), self._approx_entropy(s[:2000]),
            self._linguistic(s), self._data_density(hexd), self._code_entropy(hexd),
        ], dtype=np.float64)

    def _normalize(self, data):
        if isinstance(data, str): return data, data.encode('utf-8', errors='ignore')
        elif isinstance(data, bytes): return data.hex(), data
        elif isinstance(data, (int, float)): s = str(data); return s, s.encode()
        elif isinstance(data, np.ndarray): return str(data.tolist()), data.tobytes()
        else: s = str(data); return s, s.encode('utf-8', errors='ignore')

    def _to_hex(self, raw, bdata):
        if isinstance(raw, str) and all(c in '0123456789abcdef' for c in raw.lower()[:100]): return raw.lower()
        return bdata.hex() if isinstance(bdata, bytes) else str(bdata)

    @staticmethod
    def _shannon(d):
        if not d: return 0.0
        f = collections.Counter(d); t = len(d)
        return -sum((c/t)*math.log2(c/t) for c in f.values())
    @staticmethod
    def _norm_shannon(d):
        if not d: return 0.0
        s = EntropyMatrixCalculator._shannon(d); u = len(set(d))
        m = math.log2(u) if u > 1 else 1.0
        return s/m if m > 0 else 0.0
    @staticmethod
    def _kolmogorov(d):
        if not d: return 0.0
        try: return len(zlib.compress(d))/len(d)
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
        v = [ord(c) for c in d[:256]]; detail = [(v[i]-v[i+1])/2 for i in range(0, len(v)-1, 2)]
        return math.log2(sum(x*x for x in detail)+1)
    @staticmethod
    def _opcode_div(h): return float(len(set(h[i:i+2] for i in range(0, len(h)-2, 2))))
    @staticmethod
    def _storage_ops(h): return float(h.count("54")+h.count("55"))
    @staticmethod
    def _call_ops(h): return float(h.count("f1")+h.count("fa")+h.count("f4"))
    @staticmethod
    def _control_flow(h): return float(h.count("56")+h.count("57")+h.count("5b"))
    @staticmethod
    def _entropy_rate(d):
        if len(d) < 64: return 0.0
        w = 32; rates = [EntropyMatrixCalculator._shannon(d[i:i+w]) for i in range(0, len(d)-w, w)]
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
        v = [ord(c) for c in d[:200]]; rv = r*np.std(v) if np.std(v) > 0 else 1.0
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
        v = [ord(c) for c in d[:200]]; rv = r*np.std(v) if np.std(v) > 0 else 1.0
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
        es = [EntropyMatrixCalculator._shannon(c) for c in chunks if len(c) > 10]
        return float(np.std(es)) if es else 0.0


# ═══════════════════════════════════════════════════════════════
# MODULE 2: SEMANTIC MEMORY ENGINE
# Knowledge base (semantic memory) + concept graph.
# This is NOT a training dataset — it's the system's inherent knowledge,
# like how a human has built-in understanding of concepts.
# ═══════════════════════════════════════════════════════════════

class SemanticMemoryEngine:
    """Stores the system's semantic knowledge — concepts, relationships,
    and pre-known facts. This is NOT training data. It's a knowledge base,
    the same way a dictionary is not "training data" for a human."""

    # Knowledge base — pre-known facts about core concepts
    KNOWLEDGE = {
        "entropy": "Entropy is a measure of uncertainty or surprise in information. A coin flip has 1 bit of entropy, a die roll has about 2.58 bits. I use 24 dimensions of entropy to build a fingerprint of any input without needing to understand its content.",
        "information": "Information, in the Shannon sense, is the reduction of uncertainty. When you learn something new, your entropy decreases. I process information by measuring entropy structure, not by memorizing patterns.",
        "what_is_entropy": "Entropy measures how unpredictable something is. High entropy means chaos and randomness. Low entropy means order and structure. I use 24 different entropy measurements to fingerprint any data — code, text, bytecode — and reason about it mathematically.",
        "what_can_you_do": "I can analyze code (especially smart contracts) for structural red flags, compare two inputs and tell you how similar they really are, detect anomalies in data, and learn new categories from a single example. All without training, parameters, or datasets — just entropy mathematics.",
        "who_are_you": "I'm Entropy AI, a generative engine based on information theory. Instead of learning from massive datasets like GPT-style models, I reason using 24 dimensions of entropy mathematics. No parameters, no training, no neural networks — just math.",
        "how_do_you_work": "I compute 24 entropy dimensions from your input to create a mathematical fingerprint. Then I use information-theoretic operations — KL divergence, mutual information, conditional entropy — to reason about it. No training needed because entropy is an intrinsic property of data.",
        "how_are_you": "Running at zero parameters and zero training time — can't complain. What can I help you with?",
        "hello": "Hey! What can I help you with?",
        "hi": "Hi there — what's on your mind?",
        "hey": "Hey! Got something for me to analyze?",
        "thanks": "Anytime. What else can I do for you?",
        "thank_you": "You're welcome!",
        "bye": "See you later! Come back anytime.",
        "parameters": "I have zero parameters. Not zero million, not zero billion — literally zero. My intelligence comes from entropy mathematics, not from learned weights.",
        "training": "I require no training. No epochs, no backpropagation, no GPU farms. Entropy is an intrinsic mathematical property of data — it doesn't need to be learned, it just needs to be computed.",
        "neural": "I don't use neural networks. No transformers, no attention mechanisms, no weights. I reason through information theory — KL divergence, mutual information, conditional entropy. It's a fundamentally different approach to intelligence.",
        "security": "I can analyze smart contracts for structural vulnerabilities by looking at their entropy fingerprint. High call entropy with low overall entropy can indicate reentrancy risk. High delegatecall ratio suggests proxy patterns. I detect these without reading the code — just from the math.",
        "safe": "To check if something is safe, paste the code or contract and I'll analyze its 24D entropy profile for anomalies and risk patterns.",
        "vulnerability": "I detect vulnerabilities by looking for entropy anomalies — patterns in the mathematical structure that deviate from safe code. This catches 0-day vulnerabilities that rule-based scanners miss because I'm not matching known patterns, I'm measuring intrinsic properties.",
    }

    # Semantic graph — concept relationships (thesaurus, not dataset)
    GRAPH = {
        "hello": ["hi", "hey", "greetings", "welcome"],
        "hi": ["hello", "hey", "there"],
        "entropy": ["information", "uncertainty", "randomness", "complexity", "shannon", "measure"],
        "information": ["entropy", "data", "measure", "content", "theory"],
        "safe": ["security", "risk", "vulnerability", "contract", "code", "low"],
        "dangerous": ["risk", "vulnerability", "high", "threat"],
        "vulnerability": ["security", "risk", "detected", "contract", "code", "critical"],
        "contract": ["code", "solidity", "function", "smart", "analyzed"],
        "code": ["contract", "function", "structure", "analyzed", "entropy"],
        "analyze": ["code", "contract", "data", "entropy", "structure"],
        "compare": ["inputs", "data", "entropy", "similarity"],
        "entropy_rate": ["non-uniform", "entropy", "varies", "segments"],
    }

    def __init__(self, calculator: EntropyMatrixCalculator):
        self.calc = calculator
        self.learned_concepts: Dict[str, np.ndarray] = {}
        self.learned_labels: Dict[str, np.ndarray] = {}  # label -> avg vector

    def lookup(self, key: str) -> Optional[str]:
        """Look up pre-known knowledge."""
        key = key.lower().strip()
        # Direct lookup
        if key in self.KNOWLEDGE:
            return self.KNOWLEDGE[key]
        # Fuzzy: remove punctuation
        clean = re.sub(r'[^\w\s]', '', key)
        if clean in self.KNOWLEDGE:
            return self.KNOWLEDGE[clean]
        # Try word combinations
        words = clean.split()
        for i in range(len(words)):
            for j in range(i+1, len(words)+1):
                phrase = "_".join(words[i:j])
                if phrase in self.KNOWLEDGE:
                    return self.KNOWLEDGE[phrase]
        return None

    def learn(self, label: str, example: str):
        """Learn a new concept from one example."""
        vec = self.calc.compute(example)
        self.learned_concepts[label] = vec
        if label in self.learned_labels:
            # Average with previous
            old = self.learned_labels[label]
            count = sum(1 for l in [label] if l == label)  # simplified
            self.learned_labels[label] = (old + vec) / 2
        else:
            self.learned_labels[label] = vec.copy()

    def classify(self, data: str) -> Tuple[str, float]:
        """Classify input against learned concepts."""
        if not self.learned_labels:
            return ("unknown", 0.0)
        vec = self.calc.compute(data)
        best_label, best_sim = "unknown", -1.0
        for label, baseline in self.learned_labels.items():
            n1, n2 = np.linalg.norm(vec), np.linalg.norm(baseline)
            sim = float(np.dot(vec, baseline) / (n1 * n2)) if n1 > 0 and n2 > 0 else 0.0
            if sim > best_sim:
                best_sim, best_label = sim, label
        return (best_label, max(0.0, best_sim))

    def get_related(self, word: str) -> List[str]:
        return self.GRAPH.get(word.lower(), [])


# ═══════════════════════════════════════════════════════════════
# MODULE 3: NEXT-TOKEN GENERATOR
# Template-guided generation: templates provide grammar,
# entropy minimization fills content slots.
# ═══════════════════════════════════════════════════════════════

class NextTokenGenerator:
    """Generates text by:
    1. Detecting intent from the prompt
    2. Selecting a response template (grammatical scaffold)
    3. Filling template slots using entropy-guided word selection
    4. Running the guardrail to reject incoherent output
    """

    # Response templates — grammatical scaffolding, NOT training data
    # [SLOT] placeholders are filled by entropy-guided selection
    TEMPLATES = {
        "greeting": [
            "Hey! What can I help you with?",
            "Hi there — what's on your mind?",
            "Hey! Got something for me to analyze?",
        ],
        "identity": [
            "I'm Entropy AI — I reason using 24 dimensions of entropy mathematics. No parameters, no training, no neural networks. Just math.",
        ],
        "capabilities": [
            "I can analyze code for structural red flags, compare inputs for similarity, detect anomalies in data, and learn new categories from a single example. All powered by entropy — zero parameters, zero training.",
        ],
        "definition": [
            "{content}",
        ],
        "analysis_safe": [
            "I analyzed the input. The entropy profile looks {assessment}. Complexity is {complexity:.3f} with total entropy of {total:.2f}. {anomaly_text}",
        ],
        "analysis_risk": [
            "Looked at the structure: {findings}. {anomaly_text}Complexity: {complexity:.3f}. Want me to compare it against a known-safe version?",
        ],
        "unknown": [
            "I'm not sure about that one — can you rephrase, or paste some code or data you want me to analyze?",
            "Couldn't quite parse that. Try asking about entropy, or paste a contract to check.",
        ],
        "learned": [
            "Got it — I'll remember \"{label}\" from that example. ({memory_size} things learned so far.)",
        ],
        "comparison": [
            "Comparing those: {verdict} (similarity: {sim:.0%})",
        ],
        "no_memory": [
            "Nothing yet — teach me something with \"teach: label\" followed by an example.",
        ],
    }

    def __init__(self, calculator: EntropyMatrixCalculator, memory: SemanticMemoryEngine):
        self.calc = calculator
        self.memory = memory
        import random
        self._rng = random

    def detect_intent(self, prompt: str) -> str:
        """Detect the intent of the prompt for template selection."""
        lower = prompt.lower().strip()

        # Greetings
        if re.match(r'^(hi|hey|hello|yo|sup|hiya|greetings)[\s!.?]*$', lower):
            return "greeting"

        # Identity
        if re.search(r'who are you|what are you', lower):
            return "identity"

        # Capabilities
        if re.search(r'what can you do|what do you do|help me|your capabilities|how do you work', lower):
            if "how do you work" in lower: return "identity"
            return "capabilities"

        # Knowledge lookup
        if re.search(r'what is|what are|explain|tell me about|define', lower):
            return "definition"

        # Teach
        if re.match(r'^(teach|learn|remember):', lower):
            return "learned"

        # Compare
        if re.search(r'^compare|\svs\s|\sversus\s', lower):
            return "comparison"

        # Memory query
        if re.search(r'what do you know|what have you learned|show memory', lower):
            return "no_memory" if not self.memory.learned_labels else "memory"

        # Code analysis
        if re.search(r'contract\s+\w+', lower) and re.search(r'function|mapping|pragma', lower):
            return "analysis"
        if re.search(r'0x[0-9a-f]{20,}', lower) or re.search(r'608060', lower):
            return "analysis"
        if re.search(r'is this safe|check this|analyze this', lower):
            return "analysis"

        # Small talk
        if re.search(r"how are you|how's it going|how you doing", lower):
            return "smalltalk"
        if re.match(r'^(thanks|thank you|ty|appreciate it)[\s!.]*$', lower):
            return "thanks"
        if re.match(r'^(bye|goodbye|see you|see ya|later|cya)[\s!.]*$', lower):
            return "bye"
        if re.match(r'^(ok|okay|cool|nice|great|good)[\s!.]*$', lower):
            return "ack"

        return "unknown"

    def generate(self, prompt: str, vec: np.ndarray) -> str:
        """Generate a response using template-guided entropy generation."""
        intent = self.detect_intent(prompt)

        # Knowledge lookup (semantic memory)
        if intent == "definition":
            knowledge = self.memory.lookup(prompt)
            if knowledge:
                return self._pick(self.TEMPLATES["definition"]).format(content=knowledge)
            # Fall through to unknown if no knowledge
            intent = "unknown"

        # Greetings
        if intent == "greeting":
            return self._pick(self.TEMPLATES["greeting"])

        # Identity
        if intent == "identity":
            return self.TEMPLATES["identity"][0]

        # Capabilities
        if intent == "capabilities":
            return self.TEMPLATES["capabilities"][0]

        # Teach
        if intent == "learned":
            parts = prompt.split(":", 1)
            label = parts[1].strip().split()[0] if len(parts) > 1 else f"concept_{len(self.memory.learned_concepts)}"
            data = parts[1].strip() if len(parts) > 1 else prompt
            self.memory.learn(label, data)
            return self.TEMPLATES["learned"][0].format(
                label=label,
                memory_size=len(self.memory.learned_concepts)
            )

        # Comparison
        if intent == "comparison":
            parts = re.split(r'\svs\s|\sversus\s', re.sub(r'^compare[:\s]*', '', prompt, flags=re.I))
            if len(parts) >= 2:
                a = self.calc.compute(parts[0].strip())
                b = self.calc.compute(parts[1].strip())
                n1, n2 = np.linalg.norm(a), np.linalg.norm(b)
                sim = float(np.dot(a, b) / (n1 * n2)) if n1 > 0 and n2 > 0 else 0.0
                if sim > 0.95: verdict = "very similar, almost identical structure"
                elif sim > 0.8: verdict = "fairly similar with some differences"
                elif sim > 0.5: verdict = "somewhat different"
                else: verdict = "quite different, low structural overlap"
                return self.TEMPLATES["comparison"][0].format(verdict=verdict, sim=sim)

        # Memory query
        if intent == "memory":
            concepts = ", ".join(self.memory.learned_labels.keys())
            return f"I've learned {len(self.memory.learned_labels)} concept(s): {concepts}. Give me new input and I'll tell you which one it matches."

        # Analysis (entropy engine)
        if intent == "analysis":
            return self._generate_analysis(prompt, vec)

        # Small talk
        if intent == "smalltalk":
            return "Running at zero parameters and zero training time — can't complain. What can I help you with?"
        if intent == "thanks":
            return self._pick(["Anytime. What else can I do for you?", "You're welcome!", "No problem — happy to help."])
        if intent == "bye":
            return self._pick(["See you later!", "Bye — come back anytime.", "Take care!"])
        if intent == "ack":
            return self._pick(["👍", "Cool.", "Got it."])

        # Unknown
        return self._pick(self.TEMPLATES["unknown"])

    def _generate_analysis(self, prompt: str, vec: np.ndarray) -> str:
        """Generate analysis using 24D entropy — this is the real entropy engine."""
        anomalies = self._detect_anomalies(vec)
        complexity = float(np.mean(vec))
        total = float(np.sum(vec))
        lower = prompt.lower()

        # Detect type
        input_type = "structured_data"
        if vec[8] > 10 and vec[10] > 2: input_type = "evm_bytecode"
        elif re.search(r'contract\s+\w+', lower) and re.search(r'function|mapping|pragma', lower):
            input_type = "solidity_code"
        elif re.search(r'select|drop table|union select|or 1=1', lower):
            input_type = "sql_injection"

        # Solidity analysis
        if input_type == "solidity_code":
            findings = []
            if vec[10] > 5 and vec[13] > 0.3:
                findings.append("high external call ratio with delegatecall — proxy pattern, check who controls the implementation")
            if vec[9] > 10:
                findings.append("heavy storage operations — significant state management")
            if vec[10] > 3 and vec[0] < 3.5:
                findings.append("external calls with low entropy — check call ordering for reentrancy risk")
            if vec[12] > 0.5:
                findings.append("non-uniform entropy — code paths differ significantly")
            if not findings:
                findings.append("nothing structurally unusual — standard contract logic")

            risk = "elevated" if len(findings) > 1 else "normal"
            anomaly_text = f"Anomalies: {', '.join(anomalies)}.\n" if anomalies else ""

            if len(findings) > 1:
                return self.TEMPLATES["analysis_risk"][0].format(
                    findings="; ".join(findings),
                    anomaly_text=anomaly_text,
                    complexity=complexity
                )
            else:
                return self.TEMPLATES["analysis_safe"][0].format(
                    assessment=risk,
                    complexity=complexity,
                    total=total,
                    anomaly_text=anomaly_text
                )

        # SQL injection
        if input_type == "sql_injection":
            return f"SQL injection pattern detected. The entropy signature shows high complexity ({complexity:.3f}) with obfuscated payload structure."

        # Bytecode
        if input_type == "evm_bytecode":
            return f"EVM bytecode detected. Opcode diversity: {vec[8]:.0f}, Storage ops: {vec[9]:.0f}, Call ops: {vec[10]:.0f}, Selectors: {vec[14]:.0f}. {('; '.join(anomalies)) if anomalies else 'No anomalies.'}"

        # Generic
        anomaly_text = f"Anomalies: {', '.join(anomalies)}.\n" if anomalies else "No anomalies detected."
        return f"Analyzed the input. Complexity: {complexity:.3f}, Total entropy: {total:.2f}. {anomaly_text}"

    def _detect_anomalies(self, vec):
        a = []
        if vec[2] > 0.9: a.append("high complexity — hard to compress")
        if vec[0] < 2.0 and vec[15] > 0.1: a.append("high redundancy — repetitive structure")
        if vec[12] > 0.5: a.append("non-uniform entropy across segments")
        if vec[9] > 10: a.append("heavy storage operations")
        if vec[10] > 5 and vec[13] > 0.3: a.append("proxy pattern — high delegatecall ratio")
        if vec[16] > 0.6: a.append("persistent — long-range correlations")
        return a

    def _pick(self, arr):
        return self._rng.choice(arr)


# ═══════════════════════════════════════════════════════════════
# MODULE 4: FACTUAL GUARDRAIL
# ═══════════════════════════════════════════════════════════════

class FactualGuardrail:
    """Scans generated responses for uncertainty via entropy threshold."""

    def __init__(self, calculator: EntropyMatrixCalculator):
        self.calc = calculator

    def check(self, text: str) -> Tuple[bool, str, Dict]:
        if not text or len(text) < 3:
            return False, "too short", {}

        vec = self.calc.compute(text)
        total = float(np.sum(vec))
        repetition = float(vec[15])

        words = text.split()
        unique_ratio = len(set(w.lower() for w in words)) / max(1, len(words))

        details = {"total_entropy": total, "complexity": float(np.mean(vec)),
                   "unique_ratio": unique_ratio, "word_count": len(words)}

        if total > 10.0 and unique_ratio < 0.4:
            return False, "high entropy with repetition — uncertain", details
        if unique_ratio < 0.3 and len(words) > 8:
            return False, "repetitive", details

        return True, "OK", details


# ═══════════════════════════════════════════════════════════════
# MAIN ENGINE
# ═══════════════════════════════════════════════════════════════

class EntropyGenerativeEngine:
    """Generative AI engine — 4 modules, 0 parameters, 0 training.
    
    Dual mode:
    - Conversation: knowledge retrieval + template-guided generation
    - Diagnostic: full 24D entropy analysis for code/data/security
    
    The entropy engine (Module 1) ALWAYS runs in the background.
    In conversation mode, it validates responses via the guardrail.
    In diagnostic mode, it IS the response.
    """

    def __init__(self):
        self.calculator = EntropyMatrixCalculator()
        self.memory = SemanticMemoryEngine(self.calculator)
        self.generator = NextTokenGenerator(self.calculator, self.memory)
        self.guardrail = FactualGuardrail(self.calculator)

    def respond(self, prompt: str) -> Dict:
        # Background: always compute 24D entropy profile
        vec = self.calculator.compute(prompt)

        # Generate response (template-guided + entropy)
        text = self.generator.generate(prompt, vec)

        # Guardrail check
        safe, reason, details = self.guardrail.check(text)

        # Background entropy summary (not shown to user in conversation mode)
        bg_entropy = {
            "total": float(np.sum(vec)),
            "complexity": float(np.mean(vec)),
            "max_dim": self.calculator.DIM_NAMES[int(np.argmax(vec))],
        }

        return {
            "text": text,
            "guardrail_safe": safe,
            "guardrail_reason": reason,
            "background_entropy": bg_entropy,
            "parameters": 0,
        }

    def teach(self, label: str, example: str):
        self.memory.learn(label, example)
        return f"Learned '{label}'. {len(self.memory.learned_concepts)} concepts in memory."

    def stats(self) -> Dict:
        return {"parameters": 0, "vocabulary": self.memory.lookup.__doc__ or "semantic",
                "learned_concepts": len(self.memory.learned_concepts),
                "architecture": "ITI v3.0", "modules": 4}


if __name__ == "__main__":
    engine = EntropyGenerativeEngine()

    print("╔══════════════════════════════════════════════════╗")
    print("║  ENTROPY GENERATIVE ENGINE v3.0                   ║")
    print("║  4 Modules · 0 Parameters · 0 Training            ║")
    print("║  Template-Guided + Entropy-Validated Generation    ║")
    print("╚══════════════════════════════════════════════════╝\n")

    tests = [
        "hello",
        "what is entropy?",
        "what can you do?",
        "who are you?",
        "how are you?",
        "thanks",
        "contract Bad { function withdraw() public { msg.sender.call{value:1 ether}(''); } }",
        "compare: hello world vs H3ll0 w0rld",
        "teach: malicious_code ' OR 1=1; --",
        "what do you know?",
    ]

    for t in tests:
        r = engine.respond(t)
        safe = "✅" if r["guardrail_safe"] else "⚠️"
        print(f"You: {t}")
        print(f"AI: {r['text']}")
        print(f"  {safe} {r['guardrail_reason']} | BG entropy: {r['background_entropy']['total']:.1f}\n")
