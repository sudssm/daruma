from flask import Flask, request, jsonify
import os
import sys
import shutil

app = Flask(__name__)

UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__file__)) + "/files"


@app.route('/')
def home():
    return jsonify(connected=True)


@app.route('/put', methods=["POST"])
def put():
    if len(request.files) == 0:
        return jsonify(success=False)
    filename, file = request.files.items()[0]
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify(success=True)


@app.route('/get/<filename>')
def get(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        return jsonify(error="File does not exist")
    try:
        return jsonify(data=open(path, 'r').read())
    except:
        return jsonify(error="Could not read")


@app.route('/delete/<filename>')
def delete(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        return jsonify(error="File does not exist")
    try:
        os.remove(path)
        return jsonify(success=True)
    except:
        return jsonify(success=False)


@app.route('/wipe')
def wipe():
    try:
        for the_file in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, the_file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        return jsonify(success=True)
    except:
        return jsonify(success=False)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        print "Create", UPLOAD_FOLDER, "first!"
        sys.exit()
    app.run(debug=True)
