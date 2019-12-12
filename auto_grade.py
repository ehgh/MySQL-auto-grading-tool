import pymysql as mdb
import os
import warnings
import subprocess
import re
from timeit import default_timer as timer
#ignore warnings
warnings.filterwarnings("ignore")

#convert dates to strings
conv = mdb.converters.conversions.copy()
conv[10] = str

#connect to server
conn = mdb.connect(user = 'root', conv = conv, password = <your_mysql_password>)
cursor = conn.cursor()

def load_DB_from_file(filename):
    #start = timer()
    print('loading database {}'.format(filename))
    fd = open(filename, 'r')
    sqlFile = fd.read()
    fd.close()
    sqlCommands = sqlFile.split(';')

    for command in sqlCommands:
        try:
            if command.strip() != '' and command[0] != '/':
                cursor.execute(command)
        except IOError:
            print("Command skipped")
    conn.commit()

def execute_solution_from_file(filename):

    #load all databases for the first time
    load_databases()

    solution = []

    fd = open(filename, 'r')
    sqlFile = fd.read()
    fd.close()
    sqlCommands = sqlFile.split(';')

    for command in sqlCommands:
        skip_command_flag = False
        try:
            if command.strip() != '':
                cursor.execute(command)
                result = cursor.fetchall()
                #result = set([item for item in result])   #if you need to compare actual tables
                for skip_command in skip_command_list:
                    if re.search(skip_command, command.lower()):
                        skip_command_flag = True
                        break
                if skip_command_flag:
                    continue
                solution.append(result)
        except IOError:
            print("Command skipped")
    return solution

def execute_scripts_from_file(filename, solution):
    print('filename:{}'.format(filename))
    #flag if a table is altered in database
    altered_table_flag = False
    #output file for grade notes
    grade_notes = open(os.path.join(file_dir, 'grade_notes', filename.split('/')[-1]), 'w+')
    #add a line to overwrite with grades
    grade_notes.write('                    \n')
    #reading sql file 
    fd = open(filename, 'r')
    sqlFile = fd.read()
    fd.close()
    sqlCommands = sqlFile.split(';')
    #copy for debug purposes
    sqlCommandsCopy = sqlCommands.copy()

    number_of_queries = 0
    #check if there is correct number of queries
    for command in sqlCommands:
        skip_command_flag = False
        if 'alter' in command.lower():
            altered_table_flag = True
        if command.strip() == '':
            sqlCommands.remove(command)
            sqlCommandsCopy.remove(command)  #debug
            continue
        else:
            for skip_command in skip_command_list:
                if re.search(skip_command, command.lower()):
                    skip_command_flag = True
                    break
            if skip_command_flag:
                sqlCommandsCopy.remove(command)  #debug
                continue
        number_of_queries += 1
    
    #check if number of queries match the number of sections
    if number_of_queries != len(solution):
        
        #debug the unmatching number of queries
        '''
        query_num = 0
        print('#################')
        print('###### of queries: {}/{}'.format(number_of_queries, len(solution)))
        print('#################')
        print('filename : {}'.format(filename))
        for item in sqlCommandsCopy:
          query_num += 1
          print('$$$$$$$$query num: {}'.format(query_num))
          print(item)
        subprocess.run(['subl', filename], check=True)
        input('enter')
        '''
        # end of debug
        grade_notes.write('number of queries does not match the number of problem sections')
    
    #run script if number of queries match
    else:
        cursor.execute("SET sql_mode=(SELECT REPLACE(@@sql_mode, 'ONLY_FULL_GROUP_BY', ''));")
        sections_correctness = []
        part_num = 0
        #number of sections per each problem (first element is always 0)
        sections_per_question = [0, <number_of_sections_per_problem>]
        for command in sqlCommands:
            skip_command_flag = False
            try:
                if command.strip() != '':
                    cursor.execute(command)
                    result = cursor.fetchall()
                    #skip command if it is not query of problem
                    #note that commands might include comments so we cannot
                    #reverse the for loop
                    for skip_command in skip_command_list:
                      if re.search(skip_command, command.lower()):
                        skip_command_flag = True
                        break
                    if skip_command_flag:
                      continue
                    grade_notes.write('\n#section {}'.
                        format((part_num - sections_per_question[0]) % 
                            sections_per_question[1] + 1) + '\n')
                    #result = set([item for item in result])
                    if len(result) == len(solution[part_num]):
                      sections_correctness.append(1)
                      grade_notes.write('correct output\n')
                    else:
                      sections_correctness.append(0.4)
                      grade_notes.write('wrong output\n')
            except IOError:
                grade_notes.write('\n#section {}'.
                    format((part_num - sections_per_question[0]) % 
                        sections_per_question[1] + 1) + '\n')
                grade_notes.write('Command skipped\n')
                sections_correctness.append(0)
            except Warning:
                pass
            except mdb.ProgrammingError as e:
                grade_notes.write('\n#section {}'.
                    format((part_num - sections_per_question[0]) % 
                        sections_per_question[1] + 1) + '\n')
                grade_notes.write('Got error {!r}, errno is {}'.
                    format(e, e.args[0]) + '\n')
                sections_correctness.append(0.4)
            except mdb.InternalError as e:
                grade_notes.write('\n#section {}'.
                    format((part_num - sections_per_question[0]) % 
                        sections_per_question[1] + 1) + '\n')
                grade_notes.write('Got error {!r}, errno is {}'.
                    format(e, e.args[0]) + '\n')
                sections_correctness.append(0.4)
            if command.strip() != '':
                part_num += 1
                if len(sections_per_question) > 1 and not skip_command_flag:
                    if part_num == sections_per_question[0] + sections_per_question[1]:
                        sections_per_question[1] += sections_per_question[0]
                        del(sections_per_question[0])
        grade = sum([a * b for a, b in zip(grade_ruberic, sections_correctness)])
        print('grade: {}/120'.format(grade))
        grade_list.append(grade)
        grade_notes.seek(0)
        grade_notes.write(str(grade))
    grade_notes.close()
    if altered_table_flag:
        load_databases()

#run once for loading database
#or when a table is altered in some query
def load_databases():
    #list all databases to load here
    load_DB_from_file(<database_file.sql>)
    


print('&' * 200)

#constants
#list of points for sequence of queries
grade_ruberic = [<list_of_points>]
grade_ruberic = [float(item) for item in grade_ruberic]


#commands to skip while running the script

skip_command_list = ['use.{1,5}' + <database_name>, #list all databases in assignment
                     'show.{1,5}databases',
                     'alter',
                     'update',
                     'create.{1,2}table',
                     'sql_mode']
skip_command_list = [item.lower() for item in skip_command_list]

#list of submission files
#directory for each section/class
file_dir = 's1'
file_list = os.listdir(os.path.join(file_dir, 'submissions'))
#remove irrelevant files
if ".DS_Store" in file_list:
  file_list.remove(".DS_Store")
#create directory for grades files
if not os.path.isdir(os.path.join(file_dir, 'grade_notes')):
  os.mkdir(os.path.join(file_dir, 'grade_notes'))

#get solution
#make sure solution file is named to 'Solution.sql'
solution = execute_solution_from_file('Solution.sql')
#initiate values
grade_list = []
file_cnt = 0
total_file_cnt = len(file_list)

for filename in file_list:
  file_cnt += 1
  print('*'* 70)
  print('file # : {}/{}'.format(file_cnt,total_file_cnt))
  filename = os.path.join(file_dir, 'submissions', filename)
  execute_scripts_from_file(filename, solution)

print('Average grade', sum(grade_list)/float(len(grade_list)))

conn.close()
