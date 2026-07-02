# Cryptography Agent Instructions

## Purpose
Specialized LoRA-tuned reasoning on AES, RSA, ECC, TLS, PKI, Post-Quantum. Does NOT code—only recommends.

## Usage
```python
from agents.crypto_agent import recommend_crypto_strategy
rec = recommend_crypto_strategy("bridge service encryption")
```

## Extension
- Fine-tune with crypto papers.
- Add threat modeling integration.