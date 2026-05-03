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
 * Now only for professors who want to leave a case (if allowed).
 */
export function canRejectCase(user, caseData) {
  if (!user || !caseData) return false
  const assigned = caseData.assignedUsers
    ? caseData.assignedUsers.split(',').map((u) => u.trim()).filter(Boolean)
    : []
  return (
    assigned.includes(user.username) &&
    user.role === 'professor'
  )
}

/**
 * Returns true if a student can request cancellation/reassignment.
 */
export function canRequestCancellation(user, caseData) {
  if (!user || !caseData) return false
  if (user.role !== 'student') return false
  if (caseData.pendingCancellation) return false // Already has a pending request
  const assigned = caseData.assignedUsers
    ? caseData.assignedUsers.split(',').map((u) => u.trim()).filter(Boolean)
    : []
  return assigned.includes(user.username)
}

/**
 * Returns true if a user can review a pending cancellation request.
 */
export function canReviewCancellation(user, caseData) {
  if (!user || !caseData) return false
  if (!caseData.pendingCancellation) return false
  if (['admin', 'advisor'].includes(user.role)) return true
  if (user.role === 'professor') {
    const assigned = caseData.assignedUsers
      ? caseData.assignedUsers.split(',').map((u) => u.trim()).filter(Boolean)
      : []
    return assigned.includes(user.username)
  }
  return false
}
