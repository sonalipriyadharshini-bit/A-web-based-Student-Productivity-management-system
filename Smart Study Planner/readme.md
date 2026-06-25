Web Based Student Productivity Management System
📚 Project Overview

The Web Based Student Productivity Management System is a web application designed to help students improve productivity, manage academic tasks, organize study schedules, track habits, and monitor progress in a single platform.

The system provides an easy-to-use interface for students to plan their activities efficiently and develop better study habits through productivity tools such as task management, timetable scheduling, habit tracking, and a Pomodoro timer.

🎯 Objectives
Improve student productivity and time management.
Organize academic tasks and schedules effectively.
Track study habits and progress.
Encourage focused learning through the Pomodoro Technique.
Provide a centralized platform for academic planning.
✨ Features
🔐 User Authentication
User Registration
User Login
Secure Authentication using Firebase
Session Management
📋 Task Management
Add Tasks
Edit Tasks
Delete Tasks
Mark Tasks as Completed
View Pending and Completed Tasks
📅 Timetable Scheduling
Create Study Timetables
Update Schedules
Manage Daily and Weekly Plans
⏰ Pomodoro Timer
Focus Session Timer
Short Break Timer
Long Break Timer
Productivity Enhancement
📈 Progress Tracking
Monitor Completed Tasks
Track Productivity Performance
View Progress Statistics
🎯 Habit Tracking
Create Daily Habits
Track Habit Completion
Monitor Consistency
👤 User Profile Management
Update Personal Information
Manage Account Settings
🛠️ Technologies Used
Technology	Purpose
HTML	Structure of Web Pages
CSS	Styling and Layout
JavaScript	Client-Side Functionality
Python	Backend Development
Flask	Web Framework
Firebase Authentication	User Authentication
SQLite	Database Management
🏗️ System Architecture
User
  │
  ▼
Frontend (HTML, CSS, JavaScript)
  │
  ▼
Flask Backend
  │
  ├── Firebase Authentication
  │
  └── SQLite Database
📂 Project Structure
student-productivity-management-system/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── tasks.html
│   ├── timetable.html
│   ├── habits.html
│   └── profile.html
│
├── database/
│   └── student_productivity.db
│
├── app.py
├── requirements.txt
├── README.md
└── config.py
⚙️ Installation
1. Clone the Repository
git clone https://github.com/your-username/student-productivity-management-system.git
2. Navigate to the Project Directory
cd student-productivity-management-system
3. Create a Virtual Environment
python -m venv venv
4. Activate the Virtual Environment
Windows
venv\Scripts\activate
Linux / MacOS
source venv/bin/activate
5. Install Required Packages
pip install -r requirements.txt
6. Run the Application
python app.py
7. Open in Browser
http://127.0.0.1:5000
🗄️ Database Design
Users Table
Field	Type
user_id	Integer
name	Text
email	Text
password	Text
Tasks Table
Field	Type
task_id	Integer
user_id	Integer
task_name	Text
deadline	Date
status	Text
Habits Table
Field	Type
habit_id	Integer
user_id	Integer
habit_name	Text
completion_status	Text
Timetable Table
Field	Type
timetable_id	Integer
user_id	Integer
subject	Text
schedule_time	Text
🚀 Future Enhancements
AI-based Study Recommendations
Attendance Tracking
Goal Setting Module
Notification System
Mobile Application Support
Cloud Database Integration
Data Analytics Dashboard
📸 Screenshots

Add screenshots of:

Login Page
Registration Page
Dashboard
Task Manager
Timetable Scheduler
Habit Tracker
Pomodoro Timer

Example:

![Dashboard](screenshots/dashboard.png)
👩‍💻 Author

Sonali Priyadharshini
MCA Student

📄 License

This project is developed for educational and academic purposes.