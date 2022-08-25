from flask import send_from_directory
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import render_template
from url_utils import get_base_url
import os
import torch

port = 12345
base_url = get_base_url(port)

if base_url == '/':
    app = Flask(__name__)
else:
    app = Flask(__name__, static_url_path=base_url+'static')
    
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

model = torch.hub.load("ultralytics/yolov5", "custom", path = 'best.pt', force_reload=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
@app.route(f'{base_url}', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))

    return render_template('index.html')

@app.route(f'{base_url}/uploads/<filename>')
def uploaded_file(filename):
    here = os.getcwd()
    image_path = os.path.join(here, app.config['UPLOAD_FOLDER'], filename)
    results = model(image_path, size=416)
#     if len(results.pandas().xyxy) >= 1:
    save_dir = os.path.join(here, app.config['UPLOAD_FOLDER'])
    results.save(save_dir=save_dir)
    def and_syntax(alist):
            if len(alist) == 1:
                alist = "".join(alist)
                return alist
            elif len(alist) == 2:
                alist = " and ".join(alist)
                return alist
            elif len(alist) > 2:
                alist[-1] = "and " + alist[-1]
                alist = ", ".join(alist)
                return alist
            else:
                return
    if (len(list(results.pandas().xyxy[0]['confidence'])) and len(list(results.pandas().xyxy[0]['name']))) >= 1:
        confidences = list(results.pandas().xyxy[0]['confidence'])
        format_confidences = []
        for percent in confidences:
            format_confidences.append(str(round(percent*100)) + '%')
            format_confidences = and_syntax(format_confidences)
            labels = list(results.pandas().xyxy[0]['name'])
            labels = set(labels)
            labels = [weapon.capitalize() for weapon in labels]
            labels = and_syntax(labels)
            return render_template('2.html', confidences=format_confidences, labels=labels, old_filename=filename, filename=filename)
#     print("after if")
    elif (len(list(results.pandas().xyxy[0]['confidence'])) and len(list(results.pandas().xyxy[0]['name']))) == 0:
        found = False
        return render_template('2.html', labels='No Weapons', old_filename=filename, filename=filename)
    
@app.route(f'{base_url}/uploads/<path:filename>')
def files(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# define additional routes here
# for example:
# @app.route(f'{base_url}/team_members')
# def team_members():
#     return render_template('team_members.html') # would need to actually make this page

if __name__ == '__main__':
    # IMPORTANT: change url to the site where you are editing this file.
    website_url = 'cocalc8.ai-camp.dev'
    print(f'Try to open\n\n    https://{website_url}' + base_url + '\n\n')
    app.run(host = '0.0.0.0', port=port, debug=True)