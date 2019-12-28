# UofT-Course-Evaluations-Dataset
Stores the dataset of past course evaluations

# NOTES:
Do NOT USE virtualenv to create your virtual environment
To run the main.py, run spark-submit main.py 

Install requirements: pip3 install -r requirements.txt

# Part One:
Task:
- Given a course and a professor name, predict its difficulty and workload

What should it predict?
- Predicted difficulty of a course and instructor
- Predicted workload of a course and instructor

What should be displayed?
- Graph of course and difficulty per year (over time) with predicted difficulty via linear regression
- Graph of course and workload per year (over time) with predicted workload via linear regression

# Part Two:
- We need to compute predicted scores for all courses from the UofT Timetable Page based on part one
- Then, the user will need to select what they want to see (difficulty and/or workload and/or enthusiasm, etc)
  - There is a max. 2 categories to select from
- Then we ask the user what they want to see (i.e, bird courses in a particular department, bird courses by departments, etc)
- Then, we plot them in a graph, color code it based on what they want to see, and cluster them using the EM algorithm.

# Alternative side project:
- Create a chrome extension that will embed ratings on the UofT timetable webpage
- It involves:
  - Displaying the rating of a course
  - Displaying the rating of a course with a professor

- The ratings to be displayed could be:
  - Birdiness
  - Course difficulty
  - Course recommendations
  - etc..

  based on user preference

- The user preference can be changed by settings which are embedded in the UofT timetable webpage
  - Ex: select ratings from: birdiness, course difficulty, etc. or aggregate
  - Ex: sort listings by increasing order of rating, decreasing order of rating, etc.

  This is all embedded as UI elements on the webpage (so the chrome extension will modify the UI)

- Problem: How do you convert ('CSC324H1', 'Liu, D.') to ('CSC324H1', 'David Liu')?
  1. Approach #1: 
     - For each course evaluation, map David Liu to Liu, D.
     - Then, we do a search for 'CSC324H1', 'Liu, D' and it should return 'David Liu'
     - If there are no results, we do a search for department 'CSC' and 'Liu, D'. It should return 'David Liu'
     - If there are no results, we do a search for any course and 'Liu, D.'
