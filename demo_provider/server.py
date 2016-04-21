from flask import Flask, request, make_response
import os
import shutil
import base64

app = Flask(__name__)

UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__file__)) + "/files"
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)


@app.route('/')
def home():
    return "working"


@app.route('/put', methods=["POST"])
def put():
    if len(request.files) == 0:
        return "", 400
    filename, file = request.files.items()[0]
    with open(os.path.join(UPLOAD_FOLDER, filename), 'w+') as out:
        out.write(base64.b64encode(file.read()))
    # file.save(os.path.join(UPLOAD_FOLDER, filename))
    return ""


@app.route('/get/<filename>')
def get(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        return "", 400
    try:
        return make_response(base64.b64decode(open(path, 'r').read()))
    except Exception as e:
        print "there was an error"
        print e
        return "", 400


@app.route('/delete/<filename>')
def delete(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        return "", 400
    try:
        os.remove(path)
        return ""
    except:
        return "", 400


@app.route('/wipe')
def wipe():
    try:
        for the_file in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, the_file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        return ""
    except:
        return "", 400

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
