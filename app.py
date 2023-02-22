from re import DEBUG, sub
from flask import Flask, render_template, request, redirect, send_file, url_for
from werkzeug.utils import secure_filename, send_from_directory
import os
import subprocess
import shutil
import pandas as pd


app = Flask(__name__)


uploads_dir = os.path.join(app.instance_path, 'uploads')
app_dir = os.path.dirname(app.instance_path)

os.makedirs(uploads_dir, exist_ok=True)

@app.route("/")
def hello_world():
    return render_template('index.html')


def sort_with_digits(s, ascending = True):
    lines = s.strip().split('\n')
    df = pd.DataFrame({'Lines': lines})
    df2 = df.Lines.str.strip().str.split(' ', expand=True).rename(columns={0: 'Numbers', 1: 'Text'})
    df['Numbers'] = df2['Numbers'].astype(float)
    df['Text'] = df2['Text'].str.strip()
    df.sort_values(['Numbers', 'Text'], ascending = ascending, inplace=True)
    return df.Lines


@app.route("/detect", methods=['POST'])
def detect():
    if not request.method == "POST":
        return
    video = request.files['video']
    video.save(os.path.join(uploads_dir, secure_filename(video.filename)))
    name = video.filename.split('.')[0]
    labels_dir = os.path.join(app_dir, 'static', 'labels')
    if os.path.exists(labels_dir):
        shutil.rmtree(labels_dir)

    subprocess.run("ls")
    # run the detect.py file with parameters
    subprocess.run(['python3', 'detect.py', '--source', os.path.join(uploads_dir, secure_filename(video.filename)), '--save-txt']) 

    file_list = os.listdir(labels_dir) # get all label files
    result_dir = os.path.join(app_dir, 'static') # save combined result to this directory
    file_path = os.path.join(result_dir, name+'_result.txt') # combined text file path
    
    # overwrite existed text file
    if os.path.exists(file_path):
        os.remove(file_path)

    count = 0 # initialize a variable to count rows in the file
    with open(file_path,'w') as file: 
        for f in file_list:
            if(name in f):
                substr1_split = f.split('.')[0].split('_')
                frame = substr1_split[len(substr1_split)-1] # last element of substr arry = frame number
                with open(os.path.join(labels_dir, f)) as input_file:
                    for line in input_file: # iterate each line in all label files
                        count = count + 1 # counting rows in the text file, increment count as we go thru line
                        file.write(frame+' ') # write frame number  
                        file.write(line)
    file.close()

    # sort text file with frame number
    with open(file_path, 'r') as f:
        s = f.read()
    lines = sort_with_digits(s, ascending = True)
    os.remove(file_path)
    with open(file_path,'w') as file:   
        for line in lines:
            file.write(line+"\n")
            
    obj = secure_filename(video.filename) # video file name. For instance, street_vid.mp4
    print('OBJ ',obj)
    data = obj + ":" + str(count) # return file name and count of rows as data to ---> index.js file
    return data

@app.route("/opencam", methods=['GET'])
def opencam():
    print("here")
    subprocess.run(['python3', 'detect.py', '--source', '0'])
    return "done"
    
