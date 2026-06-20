# HUNT.ZA-hackathon-

Universal Acceptance email validator for `.africa`, `.joburg`, `.capetown`

## Branching Strategy

GitFlow:
As you can see, there's a main branch and a dev branch, basically whenever you want to add a new feature or change, you create a branch off of dev, and name it "feature_name/developer_name", and then you do whatever changes you make, then you make a PULL REQUEST, from your branch into dev, this PR will therefore need to be reviewed by the other two group members, and once there're no merge conflicts and everything works, it'll be merged and push into dev, and at the end, it'll all be pushed into MAIN

https://huntza.tytodev.online/submit

---

## What this project does

The validator checks whether an email address is valid in a Universal Acceptance (UA) sense. Rather than checking only for an `@` sign, it confirms that the domain's TLD is a real, currently delegated TLD (including newer ones such as `.africa`, `.joburg`, and `.capetown`), handles internationalised domain names, and screens out addresses that resolve to private network space.

## Repository layout

```
HUNT.ZA-hackathon-/
├── draft_files/
│   ├── hashmap.py
│   ├── idnconversion.py
│   ├── luan.py
│   ├── temp.txt
│   └── tldnames.txt
├── HUNT.ZA Opening Deck Light.pdf
├── main.py
├── README.md
└── testing.py
```

The repository is split into two tiers: working files at the root, and exploratory or superseded files moved into `draft_files/` so they remain part of the project history without cluttering the main working set.

| File | Status | Purpose |
|---|---|---|
| `testing.py` | Working, most complete | The actual validator. Loads TLDs into a hashmap bucketed by first letter, does binary search for TLD lookups, validates local-part/domain syntax, handles IDN conversion, parses RFC 5321 address literals (`user@[192.168.1.1]`, `user@[IPv6:...]`), and checks DNS MX/A records against RFC 1918 private ranges. Has a `__main__` block with sample test cases. Now loads its TLD data from `draft_files/tldnames.txt`. |
| `main.py` | Status unclear, likely stale | Starts by hardcoding the full TLD list as a string. Worth confirming whether this is still in active use, a merge artifact, or safe to fold into or replace with `testing.py`. |
| `HUNT.ZA Opening Deck Light.pdf` | Documentation | Hackathon pitch deck. |
| `draft_files/hashmap.py` | Early draft | Same bucket and binary-search idea as `testing.py`, but re-sorts the bucket on every `validate()` call instead of once at load time, plus some leftover dead code from prototyping (an `if key:` block referencing variables that are never defined). Superseded by `testing.py`. |
| `draft_files/idnconversion.py` | Scratch file | Standalone test of Python's built-in `idna` codec on a non-ASCII domain label. Logic from here was folded into `testing.py`. |
| `draft_files/luan.py` | Status unclear, likely stale | Earlier file, same size as `main.py` when last checked. Kept here for history; confirm whether it is safe to remove. |
| `draft_files/tldnames.txt` | Data | Plaintext list of IANA TLDs, one per line. This is the file `testing.py` loads at runtime (path updated to `draft_files/tldnames.txt`). |
| `draft_files/temp.txt` | Data | Raw IANA TLD list dump (with version and timestamp header), apparently a fresh download used to refresh `tldnames.txt`. |

Note: `ntu.py`, `tlds.txt`, and `tldnames.zip` from the earlier flat layout no longer appear in the tree. These appear to have been consolidated or removed as part of the cleanup. A one-line confirmation in the Findings and Open Questions section below would give the team a record of why.

## How to run it

```bash
# 1. Clone the repo
git clone https://github.com/mhmm16/HUNT.ZA-hackathon-.git
cd HUNT.ZA-hackathon-

# 2. Install dependencies
pip install dnspython

# 3. Run the validator's built-in test cases
python testing.py
```

`testing.py` loads its TLD data from `draft_files/tldnames.txt` at import time, into `TLD_MAP`. Run it from the repository root; do not change directory into `draft_files/` first, or the relative path will fail to resolve.

### Using it in your own code

```python
from testing import is_valid

is_valid("a@google.com")            # True
is_valid("admin@localhost")         # False, no valid TLD
is_valid("user@[192.168.1.1]")      # False, private IP literal
is_valid("user@[1.1.1.1]")          # True, public IP literal
```

### Dependencies

- Python 3.x
- [`dnspython`](https://pypi.org/project/dnspython/) — for the MX/A record private-network check

---

## Analysis

### Strengths
- TLD lookup runs in O(log n) per check once the hashmap is built (first-letter bucketing plus binary search), rather than a linear scan of roughly 1,500 TLDs.
- Goes beyond basic syntax checking: it also validates against the real, current TLD list, supports IDN domains, supports RFC 5321 address literals, and rejects addresses that resolve to private network ranges, which is squarely in the spirit of Universal Acceptance testing.
- `testing.py` documents why it differs from `hashmap.py` (sorting the bucket once at load time instead of on every call) directly in a code comment, which leaves a useful trail for code review.

### Risks and items to verify before calling this complete
- `main.py` is still unexplained. Confirm with the team whether it is safe to delete now that `testing.py` is the canonical validator, or whether it serves a separate purpose, such as an entry point that is meant to import from `testing.py`.
- `draft_files/luan.py` was kept rather than deleted during the cleanup. Confirm whether it is purely historical or still needed for reference, and consider removing it once confirmed.
- No automated test suite (such as `pytest`) exists. `testing.py`'s test cases only run via its `__main__` block, so there is no CI signal on regressions.
- The TLD data sources have been partially consolidated, down from four files to two: `draft_files/tldnames.txt` and `draft_files/temp.txt`. Confirm whether `temp.txt` is still needed, or whether `tldnames.txt` is now the single source of truth.
- The DNS-based private-network check (`has_rfc1918_dns`) makes live network calls. Decide whether that is the desired behaviour for all callers, or whether it should be optional or mockable for testing.
- Confirm that every other script or import that referenced `tldnames.txt`, `tlds.txt`, or `tldnames.zip` by their old root-level paths has been updated for the new `draft_files/` location, or removed if those files were superseded.

---

## Universal Acceptance Findings

The team ran a real-world Universal Acceptance test pass against 30 production websites, attempting registration or sign-up with email addresses using non-ASCII (IDN) local parts and domains, and with new gTLD addresses (`.africa`, `.capetown`, `.durban`, and similar). The goal was to confirm whether mainstream South African and international services correctly accept UA-compliant email addresses, independent of this repository's own validator.

Where a given site produced the same failure for multiple test addresses, the team recorded a single representative screenshot rather than one per address, to avoid duplication.

### Summary

- **Sites tested:** 30
- **Sites that failed on non-ASCII or IDN email addresses:** 27
- **Failures the team flagged as critical** (no working alternative path to register or sign up): 19
- **Failures explicitly flagged as not critical** (an alternative such as a mobile number was available): 1
- **Government websites tested:** 12, all of which failed on non-ASCII input
- **Failures tied specifically to South African TLD length** (domains rejected once the TLD exceeded five characters, e.g. `.africa`, `.capetown`, `.durban`): 5
- **Sites offering an alternative sign-up path** (mobile number, Google, Facebook, or Apple account): 7

### Sites tested and outcomes

| Site | Category | Outcome | Criticality |
|---|---|---|---|
| domains.co.za | Domain registration | Failed on non-ASCII email addresses | Critical |
| tyto.africa/workshop | Booking | Failed on non-ASCII email addresses | Critical |
| PayPal (za) | Banking | Failed on non-ASCII email addresses | Critical |
| Takealot | E-commerce | Failed on non-ASCII email addresses | Critical (Google/Facebook sign-up available) |
| Evetech | E-commerce | Failed on non-ASCII email addresses; non-SA domains passed | Critical |
| NATIS (gov.za) | Government | Failed on non-ASCII addresses and SA TLDs over 5 characters | Critical (mobile number available) |
| Gautrain | Government / transport | Rejected a validly formatted address | Critical |
| Vodacom | Telecom | Failed on non-ASCII email addresses | Critical |
| Telkom | Telecom | Failed on SA TLDs over 5 characters | Critical |
| SARS (gov.za) | Government | Failed on non-ASCII email addresses | Critical |
| GitHub | Developer platform | Rejected a validly formatted address (Google/Apple sign-up available) | Not specified |
| UIF/Labour (gov.za) | Government | Failed on non-ASCII email addresses | Not critical (mobile number available) |
| CIPC (gov.za) | Government | Failed on non-ASCII addresses and SA TLDs over 5 characters | Critical |
| Makro | E-commerce | Failed on non-ASCII email addresses (Google/Facebook sign-up available) | Not specified |
| CSD (gov.za) | Government | Failed on non-ASCII email addresses | Critical |
| e-Joburg (gov.za) | Government | Failed on non-ASCII email addresses | Critical |
| Bizportal (gov.za) | Government | Failed on non-ASCII email addresses | Critical |
| Bash | Consumer | Failed on non-ASCII email addresses (Google/Facebook/Apple sign-up available) | Not specified |
| NSFAS (gov.za) | Government | Failed on non-ASCII addresses and SA domains | Critical |
| e-Tshwane (gov.za) | Government | Failed on non-ASCII email addresses | Critical |
| Standard Bank | Banking | Failed on non-ASCII email addresses | Critical |
| OUTsurance | Insurance | Failed on non-ASCII email addresses | Critical |
| RAF (gov.za) | Government | Failed on non-ASCII email addresses | Critical |
| VFS Global / DHA | Government | Failed on non-ASCII addresses and SA domains | Critical |
| UCAS | Education | Failed on non-ASCII email addresses | Not specified |
| Discovery | Insurance | Refused entry on non-ASCII addresses (mobile number available) | Not specified |
| Chime | Banking | Refused South African email addresses | Critical |
| Qatar Airways | Travel | Failed on non-ASCII email addresses | Not specified |
| Emirates (za) | Travel | Failed on non-ASCII email addresses | Not specified |
| FlySAA Voyager | Travel | Failed on non-ASCII email addresses | Not specified |

Full URLs, descriptions, and the specific test addresses used per site are recorded in the team's source log (`HUNT_errors.md`), alongside screenshots of each failure.

### Findings

- Non-ASCII (IDN) email addresses are the most common failure point by a wide margin: 27 of 30 sites tested rejected them outright, across government, banking, telecom, e-commerce, and travel sectors alike.
- South African government websites showed a consistent pattern: every government site tested (12 of 12) failed on non-ASCII addresses, and several of these (NATIS, CIPC, NSFAS, VFS Global/DHA) additionally rejected valid South African new-gTLD domains once the TLD exceeded five characters, which directly affects `.africa`, `.capetown`, and `.durban`. Telkom, a telecom provider rather than a government site, showed the same TLD-length failure.
- Most failures were judged critical because email is the only registration path offered. Only a minority of sites (7 of 30) offered a fallback, such as a mobile number or a third-party login with Google, Facebook, or Apple.
- Two sites, GitHub and Gautrain, rejected validly formatted addresses outright rather than failing specifically on non-ASCII characters, which may indicate a stricter or outdated email-format regex rather than a UA-specific issue. This is worth re-testing in isolation to confirm the exact trigger.
- Banking and government services, the categories where Universal Acceptance compliance arguably matters most for inclusion, had no exceptions in this sample: all banking and government sites tested failed at least one UA test case.

### Open questions

- Several rows above are marked "Not specified" for criticality. Confirm with the team whether these should be reclassified as critical or non-critical, or whether the criticality judgment intentionally only applies to a subset of sites.
- Confirm whether any of these 30 sites have been retested since the screenshots were taken, since some (particularly large platforms like GitHub, PayPal, or the airline sites) may update their registration flows independently of this project.
- Decide whether this findings table should be cross-referenced against `testing.py`'s own test cases, to confirm the validator in this repository would correctly accept the addresses that real-world sites are rejecting.

### Next steps

- [ ] Reclassify the "Not specified" criticality rows with the team.
- [ ] Decide whether to report any of these findings to the affected organisations (particularly the government sites, given the public-service impact).
- [ ] Cross-check the test addresses used here against `testing.py`'s `is_valid()` to confirm the validator built in this repository handles them correctly.
- [ ] Retest a sample of sites closer to submission to confirm the findings are still current.
