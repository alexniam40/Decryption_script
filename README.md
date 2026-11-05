
```markdown
# 🔓 DECRYPTION_SCRIPTS

> **Public Python toolkit to decrypt configs from popular Android tunneling apps**  
> HTTP Injector • NPV Tunnel • HTTP Custom • Dark Tunnel • SSC Custom

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Channel](https://img.shields.io/badge/Telegram-Channel-blue?logo=telegram)](https://t.me/habibidecodez)

**📢 Official Channel:** [t.me/habibidecodez](https://t.me/habibidecodez)

---

## 👥 Script Authors

| Author | Telegram |
|--------|----------|
| HABIBI | [@HABIBI_1ST](https://t.me/HABIBI_1ST) |
| NullptrO | [@NullptrO](https://t.me/NullptrO) |

**🤝 Contributors & Admins:**  
[@YouKnowA9](https://t.me/YouKnowA9) • [@forjad0](https://t.me/forjad0)

---

## 🧰 Requirements

Install all dependencies with a single command:

```bash
pip install pycryptodome argon2-cffi msgpack
```

· pycryptodome – AES, ChaCha20, and other modern ciphers
· argon2-cffi – Argon2 key derivation (required for HTTP Injector)
· msgpack – MessagePack deserialization (required for Dark Tunnel)

Other imports (base64, json, struct, gzip, pickle, hashlib, re, io, contextlib, typing) are part of Python’s standard library – no extra install needed.

---

🚀 Usage

Every script exposes a run(file_bytes: bytes) -> Optional[str] function.
Just read your config file into bytes and call it:

```python
with open("config_file.ehi", "rb") as f:
    result = module.run(f.read())
if result:
    print(result)
```

The output is a clean JSON string (with a small header) containing the fully decrypted configuration. Perfect for analysis, conversion, or further automation.

---

📜 Scripts & Decryption Breakdown

1️⃣ HTTP Injector (.ehi files)

App: HTTP Injector
File format: Binary .ehi container

Decryption steps:

1. Container parsing – The script reads the binary file and extracts an encrypted payload using a length‑prefixed UTF‑8 structure.
2. AES‑CBC Layer 1 – Tries multiple IVs (bypass & standard sets) to decrypt the payload with a static AES‑256 key (L1_KEY). Unpads the result.
3. Colon‑split extraction – Splits the decrypted string by :. Takes the second part (base64) and decrypts it with another static AES‑128 key (L2_KEY_STATIC) → yields garbage bytes.
4. XXTEA decryption – Decrypts that garbage using a hardcoded XXTEA master key (EOO_MASTER_KEY). Extracts a JSON string from the result.
5. Config JSON & salt – Reads configSalt from the JSON. If an advanced lock is active (standard IV):
   · XOR‑decrypts a configData field using the salt.
   · Derives an Argon2 key from a MasterKey (SHA‑256 of several config fields) and a salt extracted from the decrypted payload.
   · Decrypts the final config with ChaCha20‑Poly1305 (authenticated encryption).
6. Inner field decoding – Recursively decodes configMessage (Java‑UTF‑16 XOR) and other XOR‑protected fields. Finally parses embedded JSON strings inside v2rRawJson and overwriteServerData.

➡️ Output: The complete, human‑readable HTTP Injector configuration.

---

2️⃣ NPV Tunnel (NPVT1 / NPVTSUB1 files)

App: NPV Tunnel
File format: Text files with a header and a base64 payload

Decryption steps:

1. Header stripping – Removes NPVTSUB1 or NPVT1 prefix.
2. Payload split – Splits the remaining content by ,. The second element is a base64‑encoded ciphertext.
3. White‑box AES‑CTR – A pre‑loaded, serialised white‑box state (gzip‑compressed pickle) contains lookup tables. The script emulates AES‑CTR mode using a custom white‑box round function:
   · Uses the first 16 bytes of the decoded payload as the IV.
   · For each 16‑byte block, increments the IV and runs the white‑box AES on it to produce a keystream.
   · XORs the keystream with the ciphertext.
4. JSON parsing – The decrypted plaintext is parsed as JSON. If it’s a list, the first element is taken.
5. Clean output – The final JSON object is returned.

➡️ Output: Decrypted NPV Tunnel configuration (or raw string if JSON parsing fails).

---

3️⃣ HTTP Custom (.hc files)

App: HTTP Custom
File format: Custom binary/text with multiple encryption layers

Decryption steps:

1. Initial XOR – The entire file is XORed with a hardcoded hex key (e382e4b8adc386f09f9293) to reveal a hex‑encoded string.
2. ABC decryption (ChaCha20) – The hex string is decrypted using a static ChaCha20 key and static nonce → gives a JSON wrapper {"cfg": ...} or {"a": ..., "xy": ...}.
3. Format detection – The wrapper tells whether the config is new (has a cfg.content field) or old (has a.xy).
4. Meta‑value extraction – Extracts HWID, password, area, provider from the wrapper. These are used later to derive a dynamic ChaCha20 nonce (XORed with the static nonce).
5. Master ciphertext decryption:
   · New format: tries RST decryption (XOR + AES‑ECB with multiple keys) or ChaCha20 with various keys.
   · Old format: uses a fixed ChaCha20 key.
6. Split & field mapping – The decrypted string is split by a delimiter ([splitConfig]). Each token is mapped to a known configuration field using a token index.
7. Per‑field decryption:
   · ChaCha20 + JKL decoding (bitwise inverse + custom transformation).
   · SSH credentials are further processed with Braille decoding and Z3A extraction.
8. Assembly – The script returns a dictionary with Protections (HWID, password, etc.) and Config (all decrypted fields).

➡️ Output: Fully decrypted HTTP Custom configuration with all fields labelled.

---

4️⃣ Dark Tunnel

App: Dark Tunnel
File format: Base64‑encoded MessagePack container (often shared via darktunnel:// links)

Decryption steps:

1. URL cleaning – Strips darktunnel:// scheme if present.
2. Base64 decode – Decodes the rest into a JSON outer shell.
3. Outer AES‑CFB‑256 – Decrypts the encryptedLockedConfig field with a static 256‑bit key and static IV.
4. MessagePack unpack – Unpacks the decrypted bytes into a Python dictionary.
5. Inner AES‑CFB‑192 – If an EncryptedLockedConfig field exists, it’s decrypted again with a 192‑bit key and the same IV, then recursively cleaned.
6. Recursive cleaning – Walks through the entire structure; any dict key starting with Encrypted is AES‑CFB‑decrypted. Binary values are converted to UTF‑8 strings or lists if printing fails. Passwords are removed for safety.
7. JSON normalisation – The final structure is safely serialised to JSON, with auto‑parsing of embedded JSON strings.

➡️ Output: Fully decrypted Dark Tunnel configuration, human‑readable and password‑free.

---

5️⃣ SSC Custom (ssc:// links)

App: SSC Custom (Shadowsocks‑based)
File format: Hex‑encoded ChaCha20 ciphertext (from ssc:// or raw hex)

Decryption steps:

1. URL reversal – If the content starts with ssc://, it’s stripped and the remaining string is reversed.
2. Hex decode – All whitespace is removed, and the clean hex string is decoded to bytes.
3. First ChaCha20 layer – Decrypted with a static L1_KEY and a fixed nonce → yields a JSON object (L1 JSON).
4. L1 structure analysis:
   · If c exists and a is a string: The script extracts a 16‑byte nonce from a, then decrypts c with L2_KEY and that nonce → L2 JSON.
   · If a is a list: The L1 JSON is already the final config.
5. Field renaming & sanitisation – Every single‑char key is mapped to a readable name (e.g. a → CONFIGS, h → PROXY). Values are stripped of control characters, and IP addresses are extracted.
6. Inner CONFIGS decryption – If CONFIGS is a list, each element’s b (user key) is used to derive an 8‑byte nonce. Then fields like payload, proxy, address, etc. are decrypted with a third ChaCha20 key (L3_KEY) and that nonce.
7. Final assembly – All decrypted and sanitised fields are returned as a clean JSON object.

➡️ Output: Complete SSC profile with all secrets decrypted and sanitised.

---

⚠️ Disclaimer

These scripts are intended for educational purposes and legitimate config recovery only. Always respect the terms of service of the applications and the privacy of others. The authors are not responsible for any misuse.

---

📄 License

This project is released under the MIT License – you’re free to use, modify, and distribute it, with attribution.

---

🔐 Keep decrypting, stay curious!
Made with ❤️ by @HABIBI_1ST & @NullptrO
Maintained by @YouKnowA9 & @forjad0

```
