#!/usr/bin/env python3
"""
ENTROPY AI — Interactive CLI
=============================
Chat with the first AI that has NO parameters, NO training, NO datasets.
It reasons purely through information theory.

Usage:
    python3 chat.py              # Interactive mode
    python3 chat.py "analyze this text"  # Single query
    python3 chat.py --demo        # Run demo

Created by: EntroProtocol
License: MIT
"""

import sys
import json
from core import EntropyAI

BANNER = """
╔══════════════════════════════════════════════════╗
║  ENTROPY AI v1.0 — Information-Theoretic AI      ║
║  NO parameters · NO training · NO datasets        ║
║  Pure mathematics · Infinite capacity             ║
║  Created by EntroProtocol                         ║
╚══════════════════════════════════════════════════╝
"""

HELP = """
Commands:
  learn <label>    — Teach it one example (type/paste data after)
  analyze <text>   — Analyze any input
  compare          — Compare two inputs
  classify <text>  — Classify based on learned patterns
  profile <text>   — Show full entropy DNA profile
  stats            — Show model statistics
  demo             — Run built-in demo
  help             — Show this help
  quit             — Exit

The AI learns from SINGLE examples — no datasets needed.
Each 'learn' adds one entropy signature to memory.
"""

def demo(ai):
    """Built-in demo — shows the AI working across domains."""
    print("\n" + "=" * 50)
    print("DEMO: Teaching from single examples (no datasets)")
    print("=" * 50)
    
    # Learn from ONE example each
    examples = [
        ("The weather is nice today and I feel happy.", "natural_language"),
        ("pragma solidity ^0.8; contract Safe { uint256 val; function set(uint256 v) public { val=v; } }", "solidity_safe"),
        ("contract Vuln { function withdraw() public { msg.sender.call{value:1 ether}(''); } }", "solidity_vulnerable"),
        ("def fibonacci(n): a,b=0,1; result=[]; while a<n: result.append(a); a,b=b,a+b; return result", "python_code"),
        ("608060405234801561001057600080fd5b50600436106100365760003560e01c8063", "evm_bytecode"),
        ("' OR 1=1; DROP TABLE users; --", "sql_injection"),
    ]
    
    for text, label in examples:
        result = ai.learn(text, label)
        print(f"  ✓ Learned '{label}' from 1 example (memory: {result['memory_size']})")
    
    print(f"\nModel stats: {ai.stats()}")
    
    # Test on UNSEEN data
    print("\n" + "=" * 50)
    print("TEST: Analyzing unseen inputs (no training on these)")
    print("=" * 50)
    
    tests = [
        "Machine learning is transforming how we process information.",
        "contract MyToken { mapping(address=>uint) balances; function transfer(address to, uint amount) public { balances[msg.sender]-=amount; balances[to]+=amount; } }",
        "contract Bad { mapping(address=>uint) b; function w() public { payable(msg.sender).call{value:b[msg.sender]}(''); b[msg.sender]=0; } }",
        "import numpy as np; data = np.random.randn(100); mean = np.mean(data); std = np.std(data)",
        "6080604052600436106100295760003560e01c8063a9059cbb146100",
        "'; DELETE FROM accounts WHERE 1=1; --",
    ]
    
    for test in tests:
        label, conf = ai.classify(test)
        result = ai.analyze(test)
        anomalies = result.get('anomalies', [])
        print(f"\n  Input: {test[:60]}...")
        print(f"  → Classified as: {label} ({conf:.1%} confidence)")
        if anomalies:
            print(f"  → Anomalies: {', '.join(anomalies)}")
    
    # Show entropy DNA profile
    print("\n" + "=" * 50)
    print("ENTROPY DNA PROFILE of SQL injection:")
    print("=" * 50)
    print(ai.export_profile("' OR 1=1; DROP TABLE users; --"))
    
    # Compare two inputs
    print("\n" + "=" * 50)
    print("COMPARISON: Safe vs Vulnerable contract")
    print("=" * 50)
    safe = "contract Safe { mapping(address=>uint) b; function withdraw() public { uint amt=b[msg.sender]; b[msg.sender]=0; payable(msg.sender).transfer(amt); } }"
    vuln = "contract Bad { mapping(address=>uint) b; function withdraw() public { payable(msg.sender).call{value:b[msg.sender]}(''); b[msg.sender]=0; } }"
    cmp = ai.compare(safe, vuln)
    print(f"  Cosine similarity: {cmp['cosine_similarity']:.4f}")
    print(f"  KL divergence:    {cmp['kl_divergence']:.4f}")
    print(f"  Mutual info:       {cmp['mutual_information']:.4f}")
    print(f"  Verdict:           {cmp['verdict']}")


def interactive():
    ai = EntropyAI()
    print(BANNER)
    print("Type 'help' for commands, 'demo' for built-in demo, or start chatting.\n")
    
    while True:
        try:
            user_input = input("│ entropy-ai> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        
        if not user_input:
            continue
        
        if user_input == "quit" or user_input == "exit":
            print("Goodbye.")
            break
        
        if user_input == "help":
            print(HELP)
            continue
        
        if user_input == "stats":
            s = ai.stats()
            print(f"\n  Parameters:    {s['parameters']}")
            print(f"  Memory size:   {s['memory_size']} signatures")
            print(f"  Baselines:     {s['baselines']}")
            print(f"  Dimensions:    {s['dimensions']}")
            print(f"  Training time: {s['training_time']}s")
            print(f"  Model size:    {s['model_size_bytes']} bytes")
            print(f"  Architecture:  {s['architecture']}")
            print(f"  Version:       {s['version']}")
            continue
        
        if user_input == "demo":
            demo(ai)
            continue
        
        if user_input.startswith("learn "):
            label = user_input[6:].strip()
            print(f"  Enter/paste the example for '{label}':")
            data = input("  > ").strip()
            if data:
                result = ai.learn(data, label)
                print(f"  ✓ Learned '{label}' (memory: {result['memory_size']})")
                if result['anomalies']:
                    print(f"  Anomalies: {', '.join(result['anomalies'])}")
            continue
        
        if user_input.startswith("analyze "):
            data = user_input[8:].strip()
            result = ai.analyze(data)
            label, conf = ai.classify(data)
            print(f"\n  Classification: {label} ({conf:.1%})")
            print(f"  Anomalies: {result.get('anomalies', [])}")
            intrinsic = result.get('reasoning', {}).get('intrinsic', {})
            if intrinsic:
                print(f"  Total entropy: {intrinsic.get('total_entropy', 0):.4f}")
                print(f"  Complexity:     {intrinsic.get('complexity', 0):.4f}")
            continue
        
        if user_input.startswith("classify "):
            data = user_input[9:].strip()
            label, conf = ai.classify(data)
            print(f"  → {label} ({conf:.1%} confidence)")
            continue
        
        if user_input.startswith("profile "):
            data = user_input[8:].strip()
            print(ai.export_profile(data))
            continue
        
        if user_input.startswith("compare"):
            print("  First input:")
            x = input("  > ").strip()
            print("  Second input:")
            y = input("  > ").strip()
            if x and y:
                cmp = ai.compare(x, y)
                print(f"\n  Similarity:     {cmp['cosine_similarity']:.4f}")
                print(f"  KL divergence:  {cmp['kl_divergence']:.4f}")
                print(f"  Mutual info:     {cmp['mutual_information']:.4f}")
                print(f"  Verdict:         {cmp['verdict']}")
            continue
        
        # Default: analyze as text
        result = ai.analyze(user_input)
        label, conf = ai.classify(user_input)
        print(f"\n  → {label} ({conf:.1%})")
        anomalies = result.get('anomalies', [])
        if anomalies:
            print(f"  Anomalies: {', '.join(anomalies)}")
        intrinsic = result.get('reasoning', {}).get('intrinsic', {})
        if intrinsic:
            print(f"  Entropy: {intrinsic.get('total_entropy', 0):.4f} | Complexity: {intrinsic.get('complexity', 0):.4f}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            ai = EntropyAI()
            print(BANNER)
            demo(ai)
        else:
            ai = EntropyAI()
            data = " ".join(sys.argv[1:])
            print(ai.export_profile(data))
    else:
        interactive()
