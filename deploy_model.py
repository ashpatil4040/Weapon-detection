import torch
import numpy as np
import cv2
import pafy
from time import time
import time
import sqlite3
import datetime
import smtplib
import imghdr
import threading
import playsound
from email.message import EmailMessage


class ObjectDetection:
    """
    Class implements Yolo5 model to make inferences on a youtube video using OpenCV.
    """
    
    def __init__(self, out_file):
        """
        Initializes the class with youtube url and output file.
        :param url: Has to be as youtube URL,on which prediction is made.
        :param out_file: A valid output file name.
        """
        #self._URL = url
        self.model = self.load_model()
        self.classes = self.model.names
        self.out_file = out_file
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("\n\nDevice Used:",self.device)


    def get_video_from_url(self):
        play = pafy.new(self._URL).streams[-1]
        assert play is not None
        return cv2.VideoCapture(play.url)


    def send_email(self,s_email,path,today,tt):
        Sender_Email = "weapondetection4@gmail.com"
        Reciever_Email = s_email
        Password = 'omvystwbziwxxtmx'

        newMessage = EmailMessage()
        newMessage['Subject'] = "Weapon Detected in a Camera"
        newMessage['From'] = Sender_Email
        newMessage['To'] = Reciever_Email
        newMessage.set_content(f'Weapon Has been detected in camera on {today} at {tt[11:18]}')

        with open(f'static/{path}', 'rb') as f:
            image_data = f.read()
            image_type = imghdr.what(f.name)
            image_name = f.name

        newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(Sender_Email, Password)
            smtp.send_message(newMessage)

    def thread_voice_alert(self):
        playsound.playsound('siren.mp3')


    def load_model(self):
        """
        Loads Yolo5 model from pytorch hub.
        :return: Trained Pytorch model.
        """
        model = torch.hub.load('D:\Python course\python projects\my_weapon_detection\yolov5', 'custom', source ='local',
                               path='best.pt', force_reload=True)
        return model


    def score_frame(self, frame):
        """
        Takes a single frame as input, and scores the frame using yolo5 model.
        :param frame: input frame in numpy/list/tuple format.
        :return: Labels and Coordinates of objects detected by model in the frame.
        """
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)
     
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord


    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        return self.classes[int(x)]


    def plot_boxes(self, results, frame, previous_time, current_email,current_camera_username):
        """
        Takes a frame and its results as input, and plots the bounding boxes and label on to the frame.
        :param results: contains labels and coordinates predicted by model on the given frame.
        :param frame: Frame which has been scored.
        :return: Frame with bounding boxes and labels ploted on it.
        """
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = cord[i]
            if row[4] >= 0.7:
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                bgr = (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
                cv2.putText(frame, self.class_to_label(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bgr, 2)
                if (time.time() - previous_time >= 30) :
                    previous_time = time.time()
                    tt = time.ctime(time.time())
                    today = datetime.date.today()
                    today = today.strftime("%m/%d/%y")
                    conn = sqlite3.connect('WeaponDetection.db')
                    cursor = conn.cursor()
                    sql1="SELECT COUNT(*) FROM history"
                    cursor.execute(sql1)
                    ress = cursor.fetchall()
                    conn.commit()
                    path = f'saved_frames/{current_email}{ress[0][0]}.jpg'
                    cv2.imwrite(f'static/saved_frames/{current_email}{ress[0][0]}.jpg', frame)
                    sql = f"INSERT INTO history (client_email,camera_username,date,time,pic_path) VALUES (?,?,?,?,?)"
                    rec = (current_email, current_camera_username, today, tt[11:19], path)
                    cursor.execute(sql,rec)
                    conn.commit()
                    conn.close()

                    t = threading.Thread(target=self.send_email, args=(current_email,path,today,tt))
                    t.start()

                    s = threading.Thread(target=self.thread_voice_alert, args=())
                    s.start()



                #previous_time=time()
                #cv2.putText(frame, label + " {0:.1%}".format(confidence), (x, y - 20), font, 3, color, 3)
        return frame, previous_time


    def ex(self, frame,previous_time,current_email,current_camera_username):
        start_time = time.time()
        # out = cv2.VideoWriter(self.out_file, four_cc, 20, (x_shape, y_shape))
        results = self.score_frame(frame)
        frame,previous_time = self.plot_boxes(results, frame,previous_time,current_email,current_camera_username)
        # cv2.imshow('YOLO', frame)
        end_time = time.time()
        #fps = 1 / np.round(end_time - start_time, 3)
        print(end_time - start_time)
        # out.write(frame)
        return frame, previous_time



