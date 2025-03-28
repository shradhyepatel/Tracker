import pandas as pd
import numpy as np
import json 
import file_manager
import datetime as dt  

x = file_manager.files_name()

def today_date():
 today_date = dt.datetime.today().strftime("%Y-%m-%d")
 return today_date

def add_habit_filter(new_habit, habit_type):
   
   a = x['daily']
   y = x['habit_data']

   value = file_manager.add_new_habit(a , y , 'daily_habit' , new_habit , habit_type )

   if value == True:
      return True
   else :
      return "Habit Alredy Exist"
   
def add_default(user_name):
   
    default_habits = {
     "Wake up Time": "Time",
     "Exercise/Workout": "Yes/No",
     "Screen Time": "Time",
     "Study Time": "Time",
}
    file_path = x["system_setting"]
 
    for habit_name in default_habits:

      habit_type = default_habits[habit_name] 
      add_habit_filter(habit_name , habit_type)

      file_manager.user_data(user_name , file_path )

def daily_row_add():

   value = file_manager.load_data(x["daily"])

   check_value  = file_manager.check_journey_start(x["system_setting"])

   if check_value == True:
      empty = file_manager.is_file_empty(x["daily"])

      if empty :
         file_manager.add_today_if_empty(x["daily"] ,  x["system_setting"] ,today_date())

      else :
         y = value.tail(1)['Date'].values[0] == today_date() 

         if y == False:
            file_manager.daily_file_row_add(x["daily"] , x["system_setting"] , today_date())
            update_phase_target()

def habit_update():
   df = file_manager.load_data(x["daily"])
   js = file_manager.load_data(x["habit_data"])

   col = df.columns

   today = df[df['Date'] == today_date()]
   today = today.iloc[0]

   dict = {}

   for i in col :

      currentval = today[i]
      habittype = js["daily_habit"].get(i, None)

      if isinstance(currentval, float) and np.isnan(currentval):
           currentval = None

      dict[i] = {
         "current_val": currentval,
         "habit_type": habittype 
      }
      
   return dict

def updated_habit_js(json_data , file_path):

   if isinstance(json_data, str):
        json_data = json.loads(json_data)

   df = pd.DataFrame([json_data])

   df = df.where(pd.notna(df), "None")

   todaydate = today_date()

   value = file_manager.updated_habit_to_csv(df , file_path , todaydate)

   if value :
      return True
   
def get_phase_target_habit():
    json_file = file_manager.load_data(x["habit_data"])

    daily_habit = json_file.get("daily_habit", {})

    time_based_habits = [key for key, value in daily_habit.items() if value.lower() == "time"]
    numeric_habits = [key for key, value in daily_habit.items() if "numeric value" in value.lower()]

    return time_based_habits, numeric_habits

def update_phase_target_list():
   data = file_manager.load_data(x['habit_data'])

   habit_target = data['phase_target']
   habit_type = data['daily_habit']

   return habit_target , habit_type

def update_phase_target():
   file_manager.phase_target_update_row(today_date())

def check_correct_todo_phase(todo , selected_phase):

   todo = todo.split("\n")
   new_todo = []

   for t in todo:
      t = t.strip()
      if t:
        new_todo.append(t)

   l = len(new_todo)

   if l == 10:
      value = add_phase_todo(new_todo , selected_phase)
      return True
   
   else:
      return False

   
def add_phase_todo(todos , phase):

   phase = int(phase[-1])

   phases_todo = file_manager.load_data(x["phases_todos"])
   system_setting = file_manager.load_data(x["system_setting"])

   empty = file_manager.is_file_empty(x["phases_todos"])
   current_phase = system_setting['current']['current_phase']
   Phase = 0

   if phase == current_phase:
      Phase = current_phase
   
   else:
      Phase = current_phase + 1

   if empty:
      task_id = 1
      Day = 0

   else:
      last_task = phases_todo.iloc[-1]
      task_id = last_task["Task ID"] + 1
      Day = 0

   todolist = []

   for day in todos:
    Day += 1
    day = day.split(",")

    for task in day:
      task = task.strip()

      if task:
        todolist.append({
            "Phase": Phase,
            "Day": Day,
            "Task ID": task_id, 
            "Task": task,  
            "Completed": False
        })
      task_id += 1

   file_manager.save_to_csv(todolist , x["phases_todos"])

def is_valid_string(s):
    
    if '\n' in s:
        return "The task contains multiple lines."
    
    elif ',' in s:
        return "The task contains commas."
    
    elif len(s) > 20:
        return "The task exceeds 20 characters."
    
    return True

def edit_phase_todo(task , phase , day):

   phases_todo = file_manager.load_data(x["phases_todos"])

   last_row = phases_todo.iloc[-1]
   task_id = last_row["Task ID"] + 1

   phase = int(phase[-1])

   tolist = []

   z = is_valid_string(task)

   if z:
      task.strip()
      tolist.append({
         "Phase" : phase,
         "Day" : day,
         "Task ID" : task_id,
         "Task Description" : task,
         "Completed" : False })
   
   value = file_manager.save_to_csv(tolist , x["phases_todos"])

   return value