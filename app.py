from flask import Flask,render_template, request, jsonify, url_for, redirect, abort
from flask_pymongo import PyMongo
import shortid
import re

app = Flask(__name__)
mongodb = PyMongo(app)

def validate_url(url):
    regex = re.compile('^((ht|f)tps?):\/\/[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:\/~\+#]*[\w\-\@?^=%&\/~\+#])?$', re.IGNORECASE)
    return regex.match(url)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<string:short_id>')
def jump(short_id):
    record = mongodb.db.short_urls.find_one_or_404({'_id': short_id})
    return redirect(record['url'])


@app.route('/gen', methods=['POST'])
def generate_short():
    url = request.values.get('url')
    if not validate_url(url):
        abort(500)
    record = mongodb.db.short_urls.find_one({'url': url})
    if not record:
        record = {
            '_id': shortid.generate(),
            'url': url
        }
        mongodb.db.short_urls.insert_one(record)
    return jsonify(url_for('jump', short_id=record['_id'], _external=True))

if __name__ == '__main__':
    app.run()
