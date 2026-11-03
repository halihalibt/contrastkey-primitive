# ContrastKey

A reusable primitive for synthesizing a worst-case optimal identification interview from declared observable properties.

## Mechanism

The leader and validators independently classify every candidate/question cell as Y, N or U. The validator requires agreement on the entire normalized matrix, including cells outside the eventual tree. A deterministic minimax dynamic program then considers every reducing question at each candidate subset. U belongs to both observation branches. The resulting tree minimizes the maximum number of questions; ties choose the lowest question index. Each leaf must contain exactly one candidate. A Bellman table and indistinguishable pairs make the result independently inspectable.

The model supplies bounded semantic facts, never the final optimization or certificate. GenLayer decides whether the accepted facts pass independent consensus; contract code derives and commits the result atomically. A database and one model call would remove this independent acceptance boundary.

## Use

Deploy `contracts/contrastkey.py`, without constructor arguments, on **Stable Studionet 61999**, RPC `https://studio.genlayer.com/api`, Normal (Full Consensus) mode. The exact GenVM runner is pinned in the source header. This runner passed current Studio compilation; linter's newer-runner advisory is informational.

Pass the exact text in `examples/basic.json` as `payload`:

```text
seal("basic", payload)
assess("<lowercase-sender>:basic", 0)
certify("<lowercase-sender>:basic", 1)
get_record("<lowercase-sender>:basic")
```

Wait for successful FINALIZED execution and matching finalized readback between writes. `ACCEPTED` is provisional. Inspect [EVIDENCE.md](EVIDENCE.md) for the canonical address and transaction evidence. `examples/expected.json` is a local expected semantic fixture, not evidence until the chain readback matches it.

## Verification

```sh
python -m unittest discover -s tests -v
pip install -r requirements-dev.txt
genvm-lint check contracts/contrastkey.py --json
python tools/sdk_check.py
npm install
node tools/preflight.mjs
```

Unit tests use a scripted host and invoke the actual validator callback. SDK direct tests use the official pinned SDK with a mocked model; neither is live consensus. The RPC preflight checks chain identity, zero gas price and compiles the exact production source. No paid API, frontend or server is required.

For an independent deployment, set `DEPLOY_EVIDENCE_DIR` to a new empty output directory so canonical evidence stays intact. Then `tools/onchain.mjs` accepts `TEST_SIGNER_FILE` pointing to a private local disposable test key file, creating one if absent. This is never a request for a user wallet key. Use a private path outside the repository. The script records broadcast intent and hash before subsequent operations; an unresolved intent stops execution for manual chain inspection. Timeouts track the existing hash and do not trigger another write. It never appeals.

[Protocol](PROTOCOL.md) · [Security and limitations](SECURITY.md) · [Design distinctions](DESIGN.md)
