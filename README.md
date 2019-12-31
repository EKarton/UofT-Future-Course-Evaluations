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

## Local Installation:

### Pre-requisites:
Ensure that you have:
1. Local instance of Apache Spark
2. Python 3
3. Unix computer

### Step 0: Install libraries
1. In the root folder of the project, run ```pip3 install -r requirements.txt```

### Step 1: Scrapping course evaluations
1. In the ```Data Scraper``` folder, copy the file ```.env-template```, and rename the copied file to ```.env```.
2. Open the ```.env``` file and replace the contents to your Utorid and your Utorid password.
     - For instance, if your utorid is ```lfirstname``` and your utorid password is ```123```, then your ```.env``` file should look like:
          ```
          UTOR_ID=lfirstname
          PASSWORD=123
          ```
2. In the terminal, run ```python3 main.py```. It will dump the scrapped course evaluations to a csv file named ```raw-data.csv```.

### Step 2: Process the data:
1. In the ```Data Processor``` folder, create a folder called ```data```
2. Copy the csv file ```Data Scraper/raw-data.csv``` to the ```Data Processor/data/``` folder
3. In the terminal, change directories to the ```Data Processor``` folder, and run ```spark-submit pre-process.py```

### Step 3: Dump the processed data to the database
1. In the ```Data Processor``` folder, copy the file ```.env-template```, and rename the copied file to ```.env```.
2. In the ```.env``` file, replace the contents to your DB credentials with WRITE permissions
3. In the terminal, run ```python3 database-populator.py```

### Step 4: Train the ML model
1. In the ```ML Model``` folder, run the command ```python3 ml.py```

### Step 5: Run the Web API
1. In the ```Web Api``` folder, copy the file ```.env-template```, and rename the copied file to ```.env```.
2. In the ```.env``` file, replace the contents to your DB credentials with READ permissions
3. In the ```Web Api``` folder, run the command ```python3 app.py```

### Step 6: Running the Chrome Extension:
1. Open Google Chrome without web security
2. Go to ```chrome://extensions```
3. Drag and drop the ```Chrome Extensions``` folder to that webpage
4. Go to ```https://timetable.iit.artsci.utoronto.ca/```
5. Load some courses on the webpage
6. On the top of the browser, there will be a warning sign about loading unsafe scripts. Click on it and allow loading unsafe scripts
7. Reload the page
8. Load some courses. It should now show the predicted course ratings.