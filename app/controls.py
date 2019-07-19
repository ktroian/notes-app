from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from flask_login import login_user
from jwt import encode, decode
from .models import User as UserModel, Note as NoteModel
from .exceptions import *
from . import app, db, celery


class User(object):
    ''' User class designed to work with database
        and launch Celery tasks.
    '''
    model = UserModel
    session = db.session
    db = db

    def __init__(self, **kwargs):
        self.user = kwargs
        self.__password = False
        self.__exist = False
        self.__email = False
        self.__run_init()

    def set_password(self, password):
        self.user['password'] = password

    def create(self):
        ''' Starts Celery task that adds user data to database. '''
        email = self.user.get('email')
        password = self.user.pop('password', None)

        if not email:
            raise IncorrectEmailException('No email provided')

        if not self.user.get('pswd_hash') and password:
            self.user['pswd_hash'] = generate_password_hash(password, method='sha256')
        else:
            raise IncorrectPasswordException('No password provided')

        TaskManager.create_user.delay(user=self.user)

    def encode_token(self):
        ''' Creates and returns authentication token. '''
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(days=3),
                'iat': datetime.utcnow(),
                'sub': self.user.get('id')
            }
            return encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_token(token):
        ''' Decodes authentication token, returns ID of user. '''
        try:
            payload = decode(token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except InvalidTokenError:
            return 'Invalid token. Please log in again.'

    @staticmethod
    def get(id):
        ''' Returns user from database. '''
        user = User.model.query.filter_by(id=id).first()
        if not user:
            raise DoesNotExistException("User does not exist.")
        return user

    def __fetch(self, user):
        self.user['id'] = user.id

    def __run_init(self):
        self.__is_valid()
        self.__has_password()

        if self.__is_exist():
            username = self.user.get('username')
            user = UserModel.query.filter_by(username=username).first()
            self.__validate_access(user)
            self.__fetch(user)
        elif not self.__email:
            raise DoesNotExistException('User doesn\'t exist.')

    def __validate_access(self, user):
        if not self.__password:
            raise IncorrectPasswordException('Password is not provided!')

        if self.user.get('pswd_hash'):
            return

        password = self.user.get('password')
        username = self.user.get('username')
        hash = generate_password_hash(password, method='sha256')
        user = UserModel.query.filter_by(username=username).first()

        if check_password_hash(user.pswd_hash, password):
            login_user(user=user)
        else:
            raise IncorrectPasswordException('Password does not match!')


    def __has_password(self):
        if 'password' in self.user.keys():
            self.__password = True

        if 'pswd_hash' in self.user.keys():
            self.__password = True

    def __is_valid(self):
        ''' Check user data, in case of mismatch raises exception. '''
        if not self.user.get('username'):
            raise IncorrectUsernameException('Username is not provided')
        if self.user.get('email'):
            self.__email = True

    def __is_exist(self):
        self.__exist = True
        entity = UserModel.query.filter_by(username=self.user.get('username')).first()

        if not entity:
            return False
        return True

    def __repr__(self):
        return '<User %r>' % self.user.get('username')


class Note(object):
    ''' Designed to work with database and launch Celery tasks.
        It is sort of a proxy to the User db.Model.
        Requires username and one of ID or name of the note.
        If note exists in DataBase, it will be fetched, otherwise
        created automatically.
    '''
    model = NoteModel
    session = db.session
    db = db

    def __init__(self, *args, **kwargs):
        self.note = kwargs
        self.__run_init()

    def get(self):
        ''' Returns JSON serialisable note dictionary.
            Data corresponds to the one from database.
        '''
        return self.note

    @staticmethod
    def get_all(author):
        ''' Returns all notes from DataBase. '''
        return Note.model.query.filter_by(author=author).all()

    def update(self, **changes):
        ''' Starts Celery task that updates note data.'''
        TaskManager.update_note(old=self.note, new=changes)
        self.note.update(changes)

    def delete(self):
        ''' Starts Celery task that deletes note. '''
        TaskManager.delete_note.delay(note=self.note)
    
    def __run_init(self):
        self.__is_valid()

        if self.__is_exist():
            self.__fetch()
        else:
            self.__create()

    def __fetch(self):
        ''' Fetches user data from DB with User instance
            to synchronise the data.
        '''
        note = NoteModel.query.filter_by(**self.note).first()
        self.note['id'] = note.id
        self.note['name'] = note.name
        self.note['text'] = note.text

    def __create(self):
        ''' Starts Celery task. '''
        TaskManager.create_note.delay(note=self.note)

    def __is_valid(self):
        fields = self.note.keys()

        if not 'author' in fields:
            raise InvalidModelError('Note should have author.')

        if (not 'name' in fields) and (not 'id' in fields):
            raise InvalidModelError('Note should name or id author.')

    def __is_exist(self):
        note = NoteModel.query.filter_by(**self.note).first()
        return True if note else False

    def __repr__(self):
        return '<Note %r>' % self.note.get('name')


class TaskManager(object):
    ''' Class of Celery tasks. '''
    @celery.task(name='app.controls.create_note')
    def create_note(note):
        # a workaround needed to have user specific ID for notes
        # better to set up dynamic note tables
        author = note['author']
        notes = Note.model.query.filter_by(author=author).all()
        if notes:
            length = len(notes) - 1
            id = notes[length].id + 1
        else:
            id = 1
        note = NoteModel(id=id, **note)
        db.session.add(note)
        db.session.commit()

    @celery.task(name='app.controls.update_note')
    def update_note(old, new):
        Note.model.query.filter_by(**old).update(dict(**new))
        db.session.commit()

    @celery.task(name='app.controls.delete_note')
    def delete_note(note):
        note_obj = Note.model.query.filter_by(**note).first()
        db.session.delete(note_obj)
        db.session.commit()

    @celery.task(name='app.controls.create_user')
    def create_user(user):
        user = UserModel(**user)
        db.session.add(user)
        db.session.commit()

