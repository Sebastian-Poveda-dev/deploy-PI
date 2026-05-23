/**
 * Returns true if the current user can approve the given case.
 * Requires status PENDING and role admin / advisor.
 */
export function canApproveCase(user, caseData) {
  if (!user || !caseData) return false
  if (caseData.status !== 'PENDING') return false
  return ['admin', 'advisor'].includes(user.role)
}

/**
 * Returns true if a student can request cancellation/reassignment.
 */
export function canRequestCancellation(user, caseData) {
  if (!user || !caseData) return false
  if (user.role !== 'student') return false
  if (caseData.pendingCancellation) return false
  const assigned = caseData.assignedUsers
    ? caseData.assignedUsers.split(',').map((u) => u.trim()).filter(Boolean)
    : []
  return assigned.includes(user.username)
}

/**
 * Returns true if the current user can reject (remove) their own case assignment.
 * Only admins and advisors; students must use the cancellation request flow.
 */
export function canRejectCase(user, caseData) {
  if (!user || !caseData) return false
  return ['admin', 'advisor'].includes(user.role)
}

/**
 * Returns true if a user can review a pending cancellation request.
 */
export function canReviewCancellation(user, caseData) {
  if (!user || !caseData) return false
  if (!caseData.pendingCancellation) return false
  return ['admin', 'advisor'].includes(user.role)
}
