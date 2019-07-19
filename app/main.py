from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .controls import Note

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return redirect(url_for('main.notes'))


@main.route('/notes/edit/<name>', methods=['GET', 'POST'])
@login_required
def edit(name):
	if request.method == 'GET':
		author = current_user.username
		print('GET')
		note = Note(author=author, name=name)
		print(note.note['id'])
		return render_template('edit.html', note=note.get())
	elif request.method == 'POST':
		author = current_user.username
		note = Note(author=author, name=name)
		name = request.form.get('name')
		text = request.form.get('text')
		note.update(name=name, text=text)
		return redirect(url_for('main.notes'))


@main.route('/notes/delete/<name>', methods=['POST'])
@login_required
def delete(name):
	author = current_user.username
	note = Note(author=author, name=name)
	note.delete()
	return redirect(url_for('main.notes'))


@main.route('/notes/<name>', methods=['GET', 'POST'])
@login_required
def view(name):
	if request.method == 'GET':
		author = current_user.username
		note = Note(author=author, name=name)
		return redirect(url_for('main.notes'))


@main.route('/notes/create', methods=['GET', 'POST'])
@login_required
def create():
	if request.method == 'GET':
		return render_template('create.html')
	elif request.method == 'POST':
		note = Note(
			name=request.form.get('name'),
			text=request.form.get('text'),
			author=current_user.username
		)
		return redirect(url_for('main.notes'))


@main.route('/notes')
@login_required
def notes():
	name = current_user.username
	notes = Note.get_all(name)
	return render_template('notes.html', username=name, notes=notes)

