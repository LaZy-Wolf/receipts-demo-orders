class DomainError(Exception):
    status_code = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class NotFound(DomainError):
    status_code = 404


class Conflict(DomainError):
    status_code = 409


class OutOfStock(Conflict):
    pass


class InvalidTransition(Conflict):
    pass


class CouponError(DomainError):
    status_code = 422
