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