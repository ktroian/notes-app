

def exception_message(exc):
    ''' Returns exception's message '''
    try:
        msg = exc.args[0]
    except:
        msg = 'Unknown server side error occured.'
    return msg


def fail(exc):
    ''' Returns json response with exception's message '''
    msg = exception_message(exc)
    return {
        'status': 'fail',
        'message': msg
    }


def authenticate(func):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1]
        uid = User.decode_token(auth_token)
        try:
            user = User.get(uid)
        except Exception as e:
            return fail(e)
        return func(*args, user, **kwargs)
    return wrapper