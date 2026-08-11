"""Votemap domain exceptions."""


class RestrictiveFilterError(Exception):
    pass


class VoteMapException(Exception):
    pass


class SelectionLimitExceeded(VoteMapException):
    pass


class InvalidVoteError(VoteMapException):
    pass


class VoteMapNoInitialised(VoteMapException):
    pass


class PlayerNotFound(Exception):
    pass


class PlayerVoteNotAllowed(VoteMapException):
    def __init__(self, message="Player is not allowed to vote map"):
        super().__init__(message)


class PlayerChoiceNotAllowed(VoteMapException):
    def __init__(self, message="Player does not have any of required flags."):
        super().__init__(message)


class InvalidMapParam(VoteMapException):
    pass
