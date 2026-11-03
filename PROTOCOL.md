# Protocol

Version: `contrastkey-1`. Zero-based indices. String commitments use SHA256 of canonical UTF-8 JSON with sorted keys, compact separators, and unescaped Unicode. Exact source hash: [SOURCE_SHA256.txt](SOURCE_SHA256.txt).

## Persistent state

`records: TreeMap[str,str]` stores canonical JSON records; `counts: TreeMap[str,u32]` bounds each owner to 16 records. Each key is lowercase sender address + `:` + slug. Slugs have 3–32 lowercase ASCII letters, digits or hyphens. Inputs are sealed, immutable and bounded: 2–6 candidates (1,000 characters each), 1–6 observable questions (400 each); scope is at most 600 characters. Exact duplicate entries are rejected.

`seal(slug,payload) -> key` creates revision 0 in SEALED. An identical input under the same key returns that key without another record; changed input is ID_CONFLICT. Different senders have separate namespaces.

`assess(key,expected_revision) -> record JSON` requires owner, revision 0 and SEALED. Storage is copied into ordinary JSON values before non-deterministic execution. All cells are validated for shape and enums, then independently rederived by each validator from the sealed inputs. Acceptance compares canonical discrete fields, not incidental prose. A malformed model result or leader error is never converted to business uncertainty. The callback fails closed on any error. Consensus rejection means no record writes. After consensus the contract computes the proof and commits revision 1 in one of READY, AMBIGUOUS.

`certify(key,expected_revision) -> record JSON` requires owner, revision 1 and READY. It recomputes the proof, verifies its identity with stored data, and commits CERTIFIED revision 2 plus a certificate hash bound to version, input hash and assessment hash. No method can change a certified record.

`get_record(key)` returns stored JSON or empty string; `protocol()` exposes version, rules and record limit. Both are read-only.

## Error behavior

Owner mismatch, stale revision, malformed inputs, duplicate keys, quota overflow and invalid state fail before any write. A failed model/consensus call has no successful semantic record. Network status, execution success and final readback must all be checked. No automatic resubmission or appeal exists. Broadcast intent without a returned hash is deliberately an operator-inspection stop.

## Deterministic derivation

The leader and validators independently classify every candidate/question cell as Y, N or U. The validator requires agreement on the entire normalized matrix, including cells outside the eventual tree. A deterministic minimax dynamic program then considers every reducing question at each candidate subset. U belongs to both observation branches. The resulting tree minimizes the maximum number of questions; ties choose the lowest question index. Each leaf must contain exactly one candidate. A Bellman table and indistinguishable pairs make the result independently inspectable.

The certificate hash commits the accepted facts and derived proof; it is not a cryptographic proof of model truth. A reviewer can independently recompute every deterministic output from `accepted` using the checked-in source.
