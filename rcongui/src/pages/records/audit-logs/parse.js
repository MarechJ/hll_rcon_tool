export const parseAuditJson = (value) => {
  try {
    return JSON.parse(value ?? "null");
  } catch {
    return null;
  }
};

export const auditDetails = (log) => {
  const args = parseAuditJson(log.command_arguments) ?? {};
  const response = parseAuditJson(log.command_result) ?? {};
  const result = response.result;
  const record = Array.isArray(result) ? result[0] : result;
  const before = args.audit_before ?? {};

  return {
    failed: response.failed === true,
    error: response.error,
    playerId: args.player_id ?? record?.player_id ?? before.player_id,
    playerName:
      args.player_name ??
      args.description ??
      record?.player_name ??
      before.player_name,
    listName: args.name ?? record?.name ?? before.name ?? before.vip_list_name,
    listId: args.vip_list_id ?? record?.vip_list_id ?? before.vip_list_id,
  };
};
