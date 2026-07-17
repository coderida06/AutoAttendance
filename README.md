# AutoAttendance
Taking attendance is one of those things that seems small but ends up wasting a lot of time. For a classroom of around 60 students, it takes about 25 minutes every day. That's more than 12 hours every month spent just calling out names.

So I made this for my school St. Xavier's High School Kolhapur, for classes 5th to 10th.(each grade has 3 divisions- A B and C)

AutoAttendance is a Python application that uses OpenCV and face recognition to automatically mark attendance. Just register each student's face once, enter their name and class, and set up a webcam at the school entrance or classroom. As students walk in, the program recognizes them and marks them present.

Once attendance is complete, it generates a PDF report containing the present and absent students for every class and section.

✨ Features
Face recognition using OpenCV
Student registration system
Organized by classes (5A to 10C)
Automatic attendance marking
Prevents duplicate attendance
Modern CustomTkinter interface
PDF attendance reports
Present & absent lists for every class
Simple and easy to use


🛠 Built With
Python
OpenCV
face_recognition
dlib
CustomTkinter
Pillow
ReportLab


📂 How it works
Run collect.py
Enter the student's name and class.
Capture their face.
Repeat for all students.
Run attendance.py
Students walk past the camera.
Click Done once everyone has entered.
A PDF attendance report is generated automatically.

This project was built because I wanted to solve an actual problem in schools instead of making another basic computer vision project. It was also a great way to learn more about OpenCV, face recognition, GUI development, and putting everything together into one complete application.

Now all my school has to do is register each student's face once, set up a webcam, and attendance takes care of itself.

Made by Rida.
