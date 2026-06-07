# VaultKeeper – technical portfolio document

**prepared for:** visa application review  
**applicant:** mohsen jafari  
**github:** [github.com/mh3nj](https://github.com/mh3nj)  
**project repository:** [github.com/mh3nj/vaultkeeper](https://github.com/mh3nj/vaultkeeper)  
**document date:** june 7, 2026  
**development period:** may 11 – june 7, 2026

---

## what is vaultkeeper

vaultkeeper is a professional offline password manager. it stores credentials, totp secrets, secure notes, and file attachments in an encrypted sqlite database. the master password is never stored. the encryption uses aes-256-gcm with authenticated encryption. key derivation uses pbkdf2-hmac-sha256 with 200,000 iterations.

the project was conceived, designed, and built entirely by mohsen jafari, solo, over the course of one month, under significant technical constraints due to internet restrictions in iran.

it is not a prototype or a concept. it is a complete, stable, working desktop application used for real password management.

**verified by cloning and running:**

```bash
git clone https://github.com/mh3nj/vaultkeeper.git
cd vaultkeeper
pip install -r requirements.txt
python run.py
```

---

## the problem it solves

existing password managers fall into two categories. cloud-based services that store your credentials on someone else's servers, require monthly subscriptions, and have telemetry. offline managers that exist but are often poorly maintained, lack modern encryption standards, or have broken critical features like master password changes.

vaultkeeper takes a different approach. everything stays local. the database is encrypted on your disk. the master password is verified using hmac, never stored. if someone steals your database file, they get nothing without your password. if they try to brute force, the vault locks itself after 5 failed attempts.

the application was built because no existing solution combined strong cryptography, offline-first architecture, modern features (totp, attachments, breach detection), and completely local operation without subscription fees or telemetry.

---

## technical scope

| metric | value |
|--------|-------|
| total lines of code | 18,000+ (python, sql, qss, json) |
| python files | 25+ |
| development period | may 11 – june 7, 2026 |
| total active development hours | ~55 hours |
| platform | windows, mac, linux |
| primary language | python 3.11+ |
| encryption | aes-256-gcm (authenticated) |
| key derivation | pbkdf2-hmac-sha256, 200,000 iterations |
| database | sqlite with wal journal mode |
| internet required | no (fully offline) |

---

## security architecture

| component | implementation |
|-----------|----------------|
| encryption algorithm | aes-256-gcm |
| key derivation | pbkdf2-hmac-sha256, 200k iterations |
| password verification | hmac verifier (32-byte hmac of known constant) |
| memory safety | derived keys zeroed after use (`zero_key()` method) |
| master password | never stored as attribute, zeroed after derivation |
| failed attempt tracking | stored in config, vault locks after 5 failures |
| config writes | atomic (temp file + os.replace) |
| database | sqlite with row factory (named columns, not indexes) |
| emergency access | guardian key scheme (key never stored in package) |
| breach detection | hibp k-anonymity, fully offline |

---

## cryptographic implementation details

### aes-256-gcm authenticated encryption

the original version (pre-may 2026) used aes-256-cbc, which provides confidentiality but no integrity checking. a single bit flip in the ciphertext would silently corrupt decrypted data with no warning.

version 3.1 replaced cbc with gcm. every decryption authenticates the ciphertext. if the tag is invalid, `cryptoerror` is raised and the operation fails. tampering is detected. corrupted data is never returned to the user.

the implementation uses `cryptography.hazmat.primitives.ciphers.aead.aesgcm`. iv length is 16 bytes. tag length is 16 bytes. ciphertext layout is `iv + tag + ciphertext`.

### pbkdf2 key derivation

iterations were increased from 100,000 to 200,000. on a modern cpu, derivation takes approximately one second. this is a deliberate trade-off: slower key derivation makes brute force attacks exponentially more expensive.

the salt is 32 random bytes, generated per vault using `os.urandom(32)`.

### hmac verifier

the vault does not store the master password. it does not store a hash of the master password. instead, it stores a 32-byte hmac of a known constant (`b"vaultkeeper-v3-verify"`) keyed with the derived encryption key.

`make_verifier()` returns `hmac.new(key, constant, hashlib.sha256).digest()`  
`verify_key(stored_verifier)` recomputes the hmac and compares with `hmac.compare_digest()`.

this provides cryptographic verification of the master password without storing anything that could be reversed into the password itself.

### zero_key() memory wiping

python's memory management makes it difficult to guarantee that sensitive bytes are erased. the `zero_key()` method makes a best-effort attempt: it converts the key to a mutable bytearray, overwrites every byte with zero, then replaces the original reference.

this is not a perfect solution (python may have copied the bytes elsewhere), but it eliminates the most obvious retention vectors.

---

## critical bug fixes from version 3.0 to 3.1

### master password change corruption

the original `change_master_password()` function saved a new salt and config file but left every entry encrypted with the old key. the database became permanently corrupted after a password change. no error was shown. the user would only discover the corruption later when entries failed to decrypt.

the fixed version:
1. retrieves all encrypted fields from the database (`get_all_entries_raw()`)
2. decrypts each field with the old crypto instance
3. re-encrypts each field with the new crypto instance
4. updates the database with the newly encrypted values
5. only then writes the new config file

if any decryption fails, the entire operation is rolled back and an error is returned.

### emergency access time-lock bypass

the original emergency access feature used `sha256(timestamp)` as the encryption key and brute-forced ±86,400 offsets on decrypt. the waiting period was bypassable in seconds.

the new scheme:
1. generates a 32-byte guardian key using `secrets.token_bytes(32)`
2. derives an encryption key using `sha256(b"vk-emergency-v3|" + guardian_key)`
3. encrypts the vault password with aes-256-gcm
4. builds an hmac over `unlock_time` keyed with the guardian key
5. stores the encrypted payload, iv, tag, and time_mac in the package
6. the guardian key is never saved to disk

without the guardian key, decryption is computationally infeasible even with the package file. the time lock is enforced by checking `time.time() < unlock_time` before attempting decryption.

### wrong password detection

the original version would attempt to decrypt the database with any password. wrong passwords would produce garbled output. the user would see random characters instead of their passwords and not understand why.

version 3.1 verifies the password cryptographically before touching the database. the `unlock_with_password()` method:
1. loads the salt and verifier from config
2. derives a key using the provided password
3. calls `verify_key(verifier)` on the crypto instance
4. only opens the database if verification succeeds

failed attempts increment a counter in the config file. after 5 failures, the vault locks and refuses further unlock attempts.

---

## features implemented

| category | features |
|----------|----------|
| core vault | create vault, unlock with master password, change master password (re-encrypts all entries), lock vault, auto-lock timeout, failed attempt tracking (5 max) |
| password generator | random (1–4096 chars) with char set selection, pronounceable (4–100 chars), diceware (3–12 words, eff word list), pin (4–12 digits), apple-style (word-word-number) |
| auto-type | system-wide keyboard simulation using `keyboard` library. tokens: username, password, totp, tab, enter, escape, space, delay, delay2, clipboard. custom format strings. presets included. |
| totp 2fa | standard totp (rfc 6238, sha1/sha256/sha512, 6/8 digits, 30/60 sec), steam guard (5-char alphanum), yandex (pin-salted pbkdf2), motp (md5-based). time drift correction with permanent storage. |
| breach detection | offline hibp k-anonymity. compute sha-1 of password, extract first 5 hex chars, query local sqlite database. full 900m+ password list supported via `scripts/download_hibp.py`. fallback to top-500 common passwords. |
| security report | password strength distribution (weak/fair/strong/excellent), reused password detection (compares decrypted plaintext), weak password list with reasons, security score (0–100) with grade (a–f), recommendations. |
| expiry reminders | password age tracking (based on updated_at or created_at). configurable notification days (default: 7, 3, 1). notification deduplication per entry per day. bulk update from reminder dialog. |
| emergency access | create time-locked recovery packages. requires guardian key stored separately (printed, usb drive, etc). package contains encrypted vault password and hmac-verified unlock time. cannot be backdated. |
| import/export | bitwarden json (full custom fields, folder mapping, card/identity/note/ssh types), lastpass csv, plain json, plain text. duplicate detection (title + username). |
| backup scheduler | automatic encrypted backups. configurable frequency (daily/weekly/monthly). max backups (default 10, auto-prune oldest). atomic file copy via temp file + os.replace. |
| attachments | store files with entries. base64 encoded in database. file metadata (size, creation date, modification date). open with default system application. preview images with pil (optional). |
| custom fields | key-value storage per entry. supports text, hidden, boolean types. stored as json in database. |
| dark/light theme | toggle between themes. persistent across sessions via settings.json. recursive color propagation to all widgets. |
| cli console | built-in command line interface. commands: list, search, stats, export, generate, clear, exit. accessible via tools menu or ctrl+`. |
| system tray | background operation (optional). show window, lock vault, exit. |

---

## development timeline

version 3.0 was built in 5 days. version 3.1 followed over the subsequent month with security fixes, bug corrections, and feature additions.

### version 3.0 – may 11–15, 2026

| date | hours | work completed |
|------|-------|----------------|
| may 11 | ~8h | project architecture, crypto module (aes-gcm), database schema, vault manager |
| may 12 | ~10h | main window ui, entry list, details panel, add/edit entries, dark/light theme |
| may 13 | ~10h | password generator, totp (basic), auto-type, clipboard manager |
| may 14 | ~10h | breach detection (v1, fallback only), security report, expiry reminders |
| may 15 | ~10h | import/export (bitwarden, lastpass), attachments, emergency access (v1, broken), backup scheduler |

**version 3.0 total: ~48 hours across 5 days**

### version 3.1 – may 16 – june 7, 2026

| date | hours | work completed |
|------|-------|----------------|
| may 16 | ~2h | bug identification pass, security audit |
| may 18 | ~2h | cbc → gcm migration, pbkdf2 iterations increase (100k → 200k) |
| may 19 | ~3h | hmac verifier implementation, unlock_with_password rewrite |
| may 20 | ~4h | change_master_password rewrite (re-encrypts all entries) |
| may 21 | ~2h | database row factory fix (named columns, not indexes), like wildcard escaping |
| may 22 | ~3h | emergency access rewrite (guardian key scheme) |
| may 23 | ~4h | breach detection rewrite (hibp k-anonymity with sqlite) |
| may 24 | ~3h | totp fixes (motp, yandex, steam guard corrections) |
| may 25 | ~2h | password_gen entropy-based strength scoring |
| may 26 | ~2h | auto-type lazy token resolution, clipboard zeroing |
| may 27 | ~2h | atomic config writes (temp file + os.replace) |
| may 28 | ~3h | logging migration (replace print with logging) |
| may 29 | ~2h | launcher security fixes (no env var password leak) |
| may 30 | ~3h | testing across windows, mac, linux |
| june 1 | ~2h | edge case fixes, error handling improvements |
| june 2 | ~3h | documentation, requirements.txt update, .gitignore |
| june 3 | ~2h | final testing pass, regression checks |
| june 7 | ~1h | readme finalization, release preparation |

**version 3.1 additions: ~41 hours**

**combined total: ~89 hours. one month. one developer.**

---

## development context

this project was developed under significant constraints.

iran experienced widespread internet restrictions during this period, including whitelisting protocols that blocked access to github, pypi, stack overflow, and most standard development resources. the majority of the work was completed offline. dependencies were researched and downloaded during brief windows of connectivity. documentation was consulted from locally cached copies. problems were solved from first principles when no reference was available.

this affected not just convenience but fundamental development workflow. version control pushes, dependency management, and documentation access required planning and timing around unpredictable connectivity windows.

the application was built anyway. it works. it is documented. it can be cloned and run by anyone.

---

## code quality indicators

- all sensitive fields are encrypted before storage (password, notes, totp_secret)
- no master password retention in memory (zeroed after derivation)
- atomic file writes prevent config corruption
- logging at warning level by default, no sensitive data leaked to stdout
- explicit exception handling (no bare except clauses)
- sqlite row factory prevents column index errors
- like wildcard escaping prevents search injection
- hmac.compare_digest for constant-time verification
- secrets module for all random generation (cryptographically secure)

---

## third-party dependencies

| library | version | purpose |
|---------|---------|---------|
| cryptography | 42.0.0+ | aes-256-gcm, pbkdf2 |
| keyboard | 0.13.5+ | system-wide auto-type |
| qrcode[pil] | 7.4.2+ | emergency access qr codes |
| pillow | 10.3.0+ | image processing, icons |
| pystray | 0.19.0+ | system tray icon |
| pyperclip | 1.8.2+ | clipboard operations |

no http client (requests) is included. vaultkeeper is offline-first and makes no network requests except optional hibp database download (separate script).

---

## verification instructions

the authenticity and functionality of this project can be verified directly:

1. clone the repository: `git clone https://github.com/mh3nj/vaultkeeper.git`
2. install dependencies: `pip install -r requirements.txt`
3. run the application: `python run.py`
4. create a new vault with a master password
5. add an entry, verify encryption (inspect vaultkeeper.db, fields should be hex-encoded ciphertext)
6. change master password, verify all entries still decrypt correctly
7. create an emergency access package, verify time-lock works
8. run `scripts/download_hibp.py` (optional, requires internet), verify breach detection

the full application launches and operates exactly as documented. no binaries, no compiled executables required. every line of code is readable in the repository.

---

## known limitations

- auto-type on linux requires root or uinput permissions (`sudo modprobe uinput`)
- the full hibp database is ~900 mb and takes 10–30 minutes to download
- without the hibp database, breach detection falls back to top-500 common passwords
- attachments are stored base64-encoded in the database, which increases size by approximately 33%
- the emergency access guardian key must be stored separately; losing it makes the package undecryptable
- `zero_key()` makes a best-effort attempt but python's memory management may retain copies

---

## about the author

**mohsen jafari** is a full-time web developer based in iran, with professional experience in frontend development, backend systems, and desktop applications. he has been programming in python for several years and has contributed to multiple open-source projects.

vaultkeeper was built to solve a real need: a password manager that does not require trusting someone else's cloud, paying a monthly fee, or accepting telemetry. the result is a tool he uses himself, that he built himself, that works entirely offline.

- github: [github.com/mh3nj](https://github.com/mh3nj)
- xing: [xing.com/profile/Mohsen_Jafari093223](https://www.xing.com/profile/Mohsen_Jafari093223/)
- logo design: [parsegan.com](https://parsegan.com)
- portfolio: [dahgan.com](https://dahgan.com)

---

## declaration

i, mohsen jafari, confirm that the information in this document is accurate. vaultkeeper was built by me, solo, over the period of may 11 to june 7, 2026. the source code is available at the github repository listed above. the application works as described.

---

*this project was built during internet restrictions in iran. no stack overflow. no documentation access. no reliable connectivity. just whatever was cached, whatever could be reasoned through, and the determination to ship something real.*

*89 hours. 18,000+ lines. 30+ features. one month. one developer.*

*proof that creativity and persistence do not require a stable connection.*
