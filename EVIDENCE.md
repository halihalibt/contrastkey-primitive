# Verification evidence

Canonical contract: [0x73c70ce43985C46b5224df708d36fF4Fd8b9135A](https://explorer-studio.genlayer.com/address/0x73c70ce43985C46b5224df708d36fF4Fd8b9135A). Stable Studionet **61999**, zero gas price, zero transfer value, full consensus (`leaderOnly: false`). Verified at 2026-11-03T05:59:53.114Z.

| Operation | Transaction | Final status | Recorded vote result |
| --- | --- | --- | --- |
| deploy | [0x6c19ff9d0308a76d7b205073b08814e95026930c2b75d335285c3beedbe9e523](https://explorer-studio.genlayer.com/tx/0x6c19ff9d0308a76d7b205073b08814e95026930c2b75d335285c3beedbe9e523) | FINALIZED | 3 agree |
| seal | [0x6579fbcc73cc37de3f31a13e1a060decefaf1f9ad80537bbc2a6b71e3e4d7c32](https://explorer-studio.genlayer.com/tx/0x6579fbcc73cc37de3f31a13e1a060decefaf1f9ad80537bbc2a6b71e3e4d7c32) | FINALIZED | 3 agree |
| assess | [0xd021356df0b7736831ada8131bc7c18c17eedfc80bed5115e66bd12665163252](https://explorer-studio.genlayer.com/tx/0xd021356df0b7736831ada8131bc7c18c17eedfc80bed5115e66bd12665163252) | FINALIZED | 3 agree |
| certify | [0x68baeb4db88de3d553fc4627966f0c4fae0fea151af9dba0923d5178a145b9a3](https://explorer-studio.genlayer.com/tx/0x68baeb4db88de3d553fc4627966f0c4fae0fea151af9dba0923d5178a145b9a3) | FINALIZED | 3 agree |

Every canonical operation reached FINALIZED with successful execution and a majority of agreeing votes. The semantic assessment independently rederived the bounded semantics on validators. Constructor and deterministic-operation consensus alone would not prove this; the `assess` receipt is the semantic evidence.

The accepted matrix yields a worst-case depth-2 tree with no indistinguishable pairs.

The final record `0x6c0e8589067a617f552fb71dd7ae32711ee4bb3f:basic` is CERTIFIED at revision 2. The source returned by `gen_getContractCode` exactly matches `contracts/contrastkey.py`. [Recorded readbacks and summary](evidence/studionet.json) · [Exact deployed source response](evidence/deployed-code.json). Full receipts are in `evidence/*-receipt.json`.

## Local evidence

11 unit tests pass, using a scripted host with actual validator callback invocation. Exhaustive cases cover all 729 ternary 3-candidate/2-question matrices against an independent minimax oracle. Malformed model output, independent disagreement, owner isolation, revision checks, bounded inputs, quota and terminal states are covered. These tests are not network consensus.

Official SDK direct storage/calldata/closure serialization checks pass with a mocked model. Linter and live RPC compilation pass; the linter reports only an informational newer-runner advisory. See `evidence/unit-tests.txt`, `evidence/sdk-check.txt`, `evidence/lint.json` and `evidence/preflight.json`.

Run `python tools/verify_evidence.py` to verify source identity, stored finalized receipt records, readback, deterministic proof and hash commitments offline. This does not create or repeat a transaction.

## Historical deployments

One constructor-only deployment was superseded for JSON return-type compatibility before any semantic assessment. Its finalized receipt and exact source are retained.

Historical addresses are under `evidence/deployment-history/` and must never be used as canonical fallbacks. No appeal was made. No successful canonical operation was repeated to obtain a preferred result. Real-network negative business cases are not claimed; negative controls remain local.

## Scope

The deployer was a new disposable, unfunded test signer. No user wallet private key or seed phrase was requested. It owns only these example records. Other wallets can use their own namespaced records on the canonical contract. A successful shared semantic result is not a guarantee of objective truth; see [SECURITY.md](SECURITY.md).
