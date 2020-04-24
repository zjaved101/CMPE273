from flask import Flask, escape, request, jsonify, g
import sqlite3
import json

app = Flask(__name__)

STUDENTS = ['John Doe', 'Mary Doe', 'Bob Doe']
CLASSES = {}
# TESTID = 0
DATABASE = 'assignment2.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        c = db.cursor()
        # c.execute('CREATE TABLE IF NOT EXISTS tests (id INTEGER PRIMARY KEY, answers VARCHAR, submissions VARCHAR)')
        c.execute('CREATE TABLE IF NOT EXISTS tests (answers VARCHAR, submissions VARCHAR)')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# # update TESTID with the last rowid from database
# with app.app_context():
#     cur = get_db().cursor()
#     cur.execute('SELECT max(id) FROM tests')
#     TESTID = cur.fetchone()[0]
#     print('Currenet TESTID is %s' % TESTID)

def convertStringToList(string):
    list = []
    if not string:
        return list

    split = string.split('+')
    for elem in split:
        list.append(elem)
    
    return list

# DATABASE = connectToDatabase('assignment2.db')
# creates table if it doesn't exist in database
# CURSOR = DATABASE.cursor()
# sql = 'CREATE TABLE IF NOT EXISTS tests (id INTEGER PRIMARY KEY, answers JSON)'
# CURSOR.execute(sql)
# CURSOR.close()

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

@app.route('/api/tests', methods = ['POST'])
def createTest():
    cur = get_db().cursor()
    tests = request.json
    # sql = '%s, %s' % (str(TESTID), json.dumps(tests))
    # cur.execute('INSERT INTO tests VALUES(?, ?, ?)', (str(TESTID), json.dumps(tests), ''))
    cur.execute('INSERT INTO tests VALUES(?, ?)', (json.dumps(tests), '[]'))
    get_db().commit()
    tests['test_id'] = cur.lastrowid
    # TESTID += 1
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
    # answers['submission'] = convertStringToList(submission)
    answers['submissions'] = json.loads(submissions)

    return answers

@app.route('/api/tests/<id>/scantrons', methods = ['POST'])
def submitScantron(id):
    cur = get_db().cursor()
    scantron = request.json

    cur.execute('SELECT rowid, answers, submissions FROM tests WHERE rowid=%s' % str(id))
    result = cur.fetchone()
    id, answers, submissions = result
    answers = json.loads(answers)
    submissions  = json.loads(submissions)
    score, compared = gradeScantron(answers, scantron)

    # keep in mind the actual index is len - 1
    graded = {
        'scantron_id' : len(submissions) + 1,
        'scantron_url': '',
        'name': '',
        'score': score,
        'result': compared
    }

    submissions.append(graded)
    cur.execute('UPDATE tests SET submissions=\'%s\' WHERE rowid=%s' % (json.dumps(submissions), str(id)))
    get_db().commit()

    return graded, 201

def gradeScantron(answers, scantron):
    '''
        Grades the submitted scantron
        Returns a tuple as (score, correctedJson)
    '''
    score = 0
    graded = {}
    for question in answers['answer_keys']:
        if answers['answer_keys'][question] == scantron[question]:
            score += 2
        graded[question] = {'actual': scantron[question], 'expected': answers['answer_keys'][question]}
    
    return (score, graded)