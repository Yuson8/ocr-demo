from flask import Flask, render_template, request, url_for, redirect, send_from_directory
import os
import uuid
from cnocr import CnOcr

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index(): 
    # 如果有已上传的图片，则显示它
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    if uploaded_files:
        latest_file = max(uploaded_files, key=lambda x: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], x)))
        ocr = CnOcr()
        info = ocr.ocr(os.path.join(app.config['UPLOAD_FOLDER'], latest_file))
        text = ''
        if info :
            for i in range(len(info)):
                text = text + "\n" + info[i]['text']
        return render_template('index.html', image_url=url_for('uploaded_file', filename=latest_file), current_text=text)
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查是否有文件被上传
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    # 如果用户没有选择文件，则浏览器会提交一个空文件
    if file.filename == '':
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('index'))
@app.route('/uploads/<filename>')  
def uploaded_file(filename):  
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)  
@app.route('/delete', methods=['POST'])
def delete_file():
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    if uploaded_files:
        latest_file = max(uploaded_files, key=lambda x: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], x)))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], latest_file))
    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True,host="0.0.0.0",port=80)
