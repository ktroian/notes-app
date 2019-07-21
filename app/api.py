from flask import Blueprint, request, make_response, jsonify
from flask_login import login_required, current_user
from flask_restful import Api, Resource, reqparse, fields, marshal
from .controls import Note, User
from .utils import authenticate, fail

api_routes = Blueprint('api', __name__)
api = Api(api_routes)

note_fields = {
    'name': fields.String,
    'text': fields.String,
    'author': fields.String
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

class RegisterAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, location='json')
        self.reqparse.add_argument('password', type=str, location='json')
        self.reqparse.add_argument('email', type=str, location='json')
        super(RegisterAPI, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        password = args.get('password')
        username = args.get('username')
        try:
            user = User(
                email=args.get('email'),
                username=username,
                password=password
            )
            user.create()
        except Exception as e:
            return fail(e)

        auth_token = user.encode_token()
        resp = {
            'status': 'success',
            'message': 'User %s registered.' % username,
            'auth_token': auth_token.decode()
        }
        return jsonify(resp)

class LoginAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, location='json')
        self.reqparse.add_argument('password', type=str, location='json')
        super(LoginAPI, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        username = args.get('username')
        password = args.get('password')

        try:
            user = User(username=username, password=password)
        except Exception as e:
            return fail(e)

        auth_token = user.encode_token()
        resp = {
            'status': 'success',
            'message': 'User %s logged in.' % username,
            'auth_token': auth_token.decode()
        }
        return jsonify(resp)

class NotesListAPI(Resource):
    decorators = [authenticate]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('text', type=str, location='json')
        super(NotesListAPI, self).__init__()

    def get(self, user):
        notes = Note.get_all(user.username)

        return {
            'notes': [marshal(note, note_fields) for note in notes]
        }

    def post(self, user):
        args = self.reqparse.parse_args()
        name = args.get('name')
        text = args.get('text')
        try:
            note = Note(
                name=name,
                text=text,
                author=user.username
            )
            note.create()
        except Exception as e:
            return fail(e)

        return {
            'note': marshal(note.get(), note_fields)
        }


class NoteAPI(Resource):
    decorators = [authenticate]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('text', type=str, location='json')
        self.reqparse.add_argument('author', type=str, location='json')
        super(NoteAPI, self).__init__()

    def get(self, user, id):
        author = user.username
        try:
            note = Note(author=author, id=id).get()
        except Exception as e:
            return fail(e)

        return {
            'note': marshal(note, note_fields)
        }

    def put(self, user, id):
        args = self.reqparse.parse_args()
        try:
            note = Note(author=user.username, id=id)
            name = args.get('name')
            text = args.get('text')
            note.update(name=name, text=text)
            note = note.get()
        except Exception as e:
            return fail(e)
        return {
            'note': marshal(note, note_fields)
        }

    def delete(self, user, id):
        try:
            note = Note(author=user.username, id=id)
            note.delete()
        except Exception as e:
            return fail(e)
        return {
            'result': True
        }


api.add_resource(RegisterAPI, '/notes/api/v1.0/users/register', endpoint='register')
api.add_resource(LoginAPI, '/notes/api/v1.0/users/login', endpoint='login')
api.add_resource(NotesListAPI, '/notes/api/v1.0/notes', endpoint='notes')
api.add_resource(NoteAPI, '/notes/api/v1.0/notes/<int:id>', endpoint='note')
