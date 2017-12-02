CourseMe
========

Web based platform for pooling educational resources and customising online courses.


Initial environment setup
>>cd {whatever directory}
>>git clone https://github.com/BigPoppaG/CourseMe.git
>>virtualenv venv
>>venv\scripts\activate.bat   (windows - different for Mac etc)
>>cd courseme
>>pip install -r requirements.txt
>>python run.py db upgrade
>>python run.py test_data
>>python run.py test
>>python run.py runserver

Have a go at logging in with email teacher1@server.fake and password 111111.

Hopefully the site is pretty clear even though some parts are not formatted at all well yet.
To get a feel for the site you could try: Viewing a lecture. Creating a lecture from a YouTube video. Creating a course and adding lectures to it. Defining a new learning objective and defining a scheme of work. Creating a group of students. Viewing the progress for a group of students through a scheme of learning objectives. Creating a question and selecting a set of questions for printing.



Switching into working environment using virtuaslenv-wrapper
>>workon courseme
