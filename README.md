# MySQL-auto-grading
Runs queries from a <*.sql> file and compare the output to <Solution.sql> queries output and create feedback file and grade on queries. 

Here, is the directory setting:
dir:\
    - auto_grade.py\
    - Solution.sql\
    - database.sql files (files to import databases)\
    - s1 (directory for various groups/classes)\
    - s1/submissions (directory for groups of *.sql files that include queries to be tested and graded a.k.a student submissions)\
    - s1/grade_notes (directory to store feedback files created by script)

install required packages:
  - pymysql
  - warnings
  - subprocess
  - timeit


Modify auto_grade.py file to your specific assignment (Parts that need modification in auto_grade.py is marked by <some_modification>) and run:\
  python3 auto_grade.py
