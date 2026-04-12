/**
 * Returns true if the current user can approve the given case.
 * Requires status PENDING and role admin / advisor / professor.
 */
export function canApproveCase(user, caseData) {
  if (!user || !caseData) return false
  if (caseData.status !== 'PENDING') return false
  if (['admin', 'advisor'].includes(user.role)) return true
  if (user.role === 'professor') {
    const assigned = caseData.assignedUsers
      ? caseData.assignedUsers.split(',').map((u) => u.trim()).filter(Boolean)
      : []
    return assigned.includes(user.username)
  }
  return false
}

/**
 * Returns true if the current user can reject their assignment on the case.
 * Requires the user to be in the assigned users list and role student / professor.
 */
export function canRejectCase(user, caseData) {
  if (!user || !caseData) return false
  const assigned = caseData.assignedUsers
    ? caseData.assignedUsers.split(',').map((u) => u.trim()).filter(Boolean)
    : []
  return (
    assigned.includes(user.username) &&
    ['student', 'professor'].includes(user.role)
  )
}
