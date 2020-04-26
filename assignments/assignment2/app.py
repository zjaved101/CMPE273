from flask import Flask, escape, request, jsonify, g, url_for, send_from_directory
import sqlite3
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

DATABASE = 'assignment2.db'
UPLOAD_FOLDER = 'files'
ALLOWED_EXTENSIONS = {'json'}

# create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# checks if file extensions is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        c = db.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS tests (answers VARCHAR, submissions VARCHAR)')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def gradeScantron(answers, scantron):
    '''
        Grades the submitted scantron
        Returns a tuple as (score, correctedJson)
    '''
    score = 0
    graded = {}
    for question in answers['answer_keys']:
        if answers['answer_keys'][question] == scantron['answers'][question]:
            score += 2
        graded[question] = {'actual': scantron['answers'][question], 'expected': answers['answer_keys'][question]}
    
    return (score, graded)

def validateJson(json):
    '''
        Validates the json answers
        Must be integer: Alpha format
    '''
    if len(json) < 50:
        return False
    
    valid = ['A','B','C','D','E']
    for key in json:
        if not key.isdigit() or json[key] not in valid:
            return False
    
    return True

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

@app.route('/api/tests', methods = ['POST'])
def createTest():
    cur = get_db().cursor()
    tests = request.json

    if not validateJson(tests['answer_keys']):
        return jsonify("invalid answer key format"), 400

    cur.execute('INSERT INTO tests VALUES(?, ?)', (json.dumps(tests), '[]'))
    get_db().commit()
    tests['test_id'] = cur.lastrowid
    tests['submissions'] = []

    return tests, 201

@app.route('/api/tests/<id>', methods = ['GET'])
def getTest(id):
    cur = get_db().cursor()
    cur.execute('SELECT rowid, answers, submissions FROM tests WHERE rowid=%s' % str(id))
    result = cur.fetchone()

    id, answers, submissions = result
    answers = json.loads(answers)
    answers['test_id'] = id
    answers['submissions'] = json.loads(submissions)

    return answers

@app.route('/api/tests/<id>/scantrons', methods = ['POST'])
def submitScantron(id):
    if 'file' not in request.files:
        return jsonify("No file part"), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify("No file selected"), 400
    
    if not allowed_file(file.filename):
        return jsonify("file extension now allowed"), 400
    
    filename = secure_filename(file.filename)
    if not os.path.exists('%s/%s' % (UPLOAD_FOLDER, id)):
        os.makedirs('%s/%s' % (UPLOAD_FOLDER, id))

    file.save(os.path.join('%s/%s' % (app.config['UPLOAD_FOLDER'], id), filename))

    cur = get_db().cursor()
    # scantron = request.json
    with open('files/%s/%s' % (id, filename), 'r') as f:
        scantron = json.load(f)

    if not validateJson(scantron['answers']):
        return jsonify("invalid answer key format"), 400

    cur.execute('SELECT rowid, answers, submissions FROM tests WHERE rowid=%s' % str(id))
    result = cur.fetchone()
    id, answers, submissions = result
    answers = json.loads(answers)
    submissions  = json.loads(submissions)
    score, compared = gradeScantron(answers, scantron)

    # keep in mind the actual index is len - 1
    graded = {
        'scantron_id' : len(submissions) + 1,
        'scantron_url': '%s%s/%s' % (request.host_url, id, filename),
        'name': scantron['name'],
        'score': score,
        'result': compared
    }

    submissions.append(graded)
    cur.execute('UPDATE tests SET submissions=\'%s\' WHERE rowid=%s' % (json.dumps(submissions), str(id)))
    get_db().commit()

    return graded, 201

@app.route('/<id>/<filename>', methods= ['GET'])
def downloadFile(id, filename):
    directory = os.path.join(app.root_path, app.config['UPLOAD_FOLDER']) + '/%s' % id
    return send_from_directory(directory=directory, filename=filename)