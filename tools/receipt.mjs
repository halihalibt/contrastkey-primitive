import {transactionsStatusNumberToName} from 'genlayer-js/types';

/** Studio returns leader and canceled validator receipts in the same array. */
export function summarizeReceipt(tx, hash) {
  const raw = tx.consensus_data?.leader_receipt;
  const leaders = Array.isArray(raw) ? raw : raw ? [raw] : [];
  const leader = leaders.find(receipt => receipt.mode === 'leader') ??
    (leaders.length === 1 && leaders[0].mode !== 'validator' ? leaders[0] : undefined);
  const execution = leader?.execution_result ?? tx.txExecutionResultName;
  const returnStatus = leader?.result?.status;
  const status = tx.statusName ?? transactionsStatusNumberToName[String(tx.status)] ?? tx.status;
  const votes = tx.consensus_data?.votes ?? {};
  const voteValues = Object.values(votes).map(value => String(value).toLowerCase());
  const agreeCount = voteValues.filter(value => value === 'agree').length;
  const quorumAgreed = voteValues.length > 0 && agreeCount > voteValues.length / 2;
  const successful = ['ACCEPTED', 'FINALIZED'].includes(status) && quorumAgreed &&
    ['SUCCESS', 'FINISHED_WITH_RETURN'].includes(execution) &&
    (returnStatus === undefined || returnStatus === 'return');
  return {
    hash, status,
    executionResult: execution, returnStatus: returnStatus ?? null, successful,
    contractAddress: tx.to_address ?? tx.recipient,
    votes, agreeCount, quorumAgreed,
    validatorCount: tx.consensus_data?.validators?.length ?? tx.lastRound?.roundValidators?.length ?? 0,
    error: successful ? null : leader?.error ?? leader?.genvm_result?.error_description ?? leader?.result?.payload ?? null,
  };
}
