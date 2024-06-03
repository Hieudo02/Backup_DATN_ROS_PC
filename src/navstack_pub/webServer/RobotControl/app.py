#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from PIL import Image
import os
import rospy
import threading
import signal
from std_msgs.msg import String

UPLOAD_FOLDER = '/home/hieudo/datn_navbot/src/navstack_pub/webServer/RobotControl/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
v_r = 1.0
v_l = 1.0
MAX_SPEED = 0.3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_pgm(image_path):
    with Image.open(image_path) as img:
        gray_img = img.convert('L')
        binary_img = gray_img.point(lambda p: p > 128 and 255)
        pgm_path = image_path.rsplit('.', 1)[0] + '.pgm'
        binary_img.save(pgm_path)
    return pgm_path

@app.route('/', methods=['GET', 'POST'])
def index():
    global v_r
    global v_l 
    global MAX_SPEED
    if request.method == 'POST':
        if 'file' in request.files and 'resolution' in request.form:
            file = request.files['file']
            resolution = request.form['resolution']
            if file.filename != '' and allowed_file(file.filename):
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)
                
                pgm_filename = convert_to_pgm(filename)

                points = []
                for key in request.form:
                    if key.startswith('points'):
                        index = key[key.find('[')+1:key.find(']')]
                        if key.endswith('[x]'):
                            if len(points) <= int(index):
                                points.append({})
                            points[int(index)]['x'] = request.form[key]
                        elif key.endswith('[y]'):
                            if len(points) <= int(index):
                                points.append({})
                            points[int(index)]['y'] = request.form[key]

                print('Uploaded file:', pgm_filename)
                print('Resolution:', resolution)
                print('Points:', points)
                return jsonify({'url': url_for('uploaded_file', filename=file.filename)})
        
        if request.json and 'direction' in request.json:
            data = request.json
            direction = data['direction'] 
            print('Received direction:', direction)
            if direction == 'w':
                message = f"{v_r * MAX_SPEED},{v_l * MAX_SPEED}"
                pub.publish(message)
            elif direction == 'a':
                message = f"{v_r * MAX_SPEED},{v_l * (-1.0) * MAX_SPEED}"
                pub.publish(message)
            elif direction == 'x':
                message = f"{v_r * (-1.0) * MAX_SPEED},{v_l * (-1.0) * MAX_SPEED}"
                pub.publish(message)
            elif direction == 'd':
                message = f"{v_r * (-1.0) * MAX_SPEED},{v_l * MAX_SPEED}"
                pub.publish(message)
            elif direction == 's':
                pub.publish("0,0")

            # increase    
            elif direction == 'e':
                MAX_SPEED *= 1.1
                print("Currently speed: ", MAX_SPEED)
            # decrease
            elif direction == 'r':
                MAX_SPEED *= 0.9
                print("Currently speed: ", MAX_SPEED)

            return jsonify({'status': 'success'})
        return jsonify({'status': 'failure'})
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def flask_thread():
    app.run(host='0.0.0.0', port=5000)

def signal_handler(sig, frame):
    print("Shutting down...")
    os._exit(0)

def main():
    global pub
    signal.signal(signal.SIGINT, signal_handler)

    rospy.init_node('web_server_control', anonymous=True)
    pub = rospy.Publisher('manual_control', String, queue_size=10)

    flask_thread_instance = threading.Thread(target=flask_thread)
    flask_thread_instance.start()

    rospy.spin()
    flask_thread_instance.join()

if __name__ == '__main__':
    main()