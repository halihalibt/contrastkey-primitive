# Design and reuse

A reusable primitive for synthesizing a worst-case optimal identification interview from declared observable properties.

The identification problem is adaptive: the next useful observation depends on the candidates still possible. Minimax optimization bounds the largest number of questions needed over all supported observation paths. Keeping unknown values in both branches prevents an uncertain property from making the interview appear easier than it is.

Reusable boundary: applications supply small immutable declarations; independent semantic consensus establishes the bounded facts; exact deterministic code emits a conservative certificate or an explicit obstruction. ContrastKey is intentionally restricted to its stated domain.

Official references checked: [equivalence principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle), [storage](https://docs.genlayer.com/developers/intelligent-contracts/features/storage), [LLM calls](https://docs.genlayer.com/developers/intelligent-contracts/features/calling-llms). Runtime compatibility is established by the recorded linter, SDK direct checks and Stable Studionet RPC compilation, rather than assuming every newly documented API is enabled on Studio.
