from documents.services import run_automatic_document_expiration_check

IGNORED_PATH_PREFIXES = (
    '/documents/notifications/check/',
)


class DocumentExpirationHeartbeatMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        should_run_heartbeat = (
            request.user.is_authenticated
            and not any(request.path.startswith(prefix) for prefix in IGNORED_PATH_PREFIXES)
        )

        if should_run_heartbeat:
            run_automatic_document_expiration_check()

        return self.get_response(request)
