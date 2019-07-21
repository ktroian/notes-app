from jwt import ExpiredSignatureError, InvalidTokenError


class InvalidModelError(Exception):
	pass


class AllreadyExistsException(Exception):
	pass


class DoesNotExistException(Exception):
	pass


class IncorrectPasswordException(Exception):
	pass


class IncorrectUsernameException(Exception):
	pass


class IncorrectEmailException(Exception):
	pass


class InvalidModelException(Exception):
	pass