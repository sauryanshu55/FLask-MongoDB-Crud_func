from flask import Flask, render_template, redirect
from pymongo import MongoClient
from classes import *

# config system

##database password=YHhs6oJHj3W0X14z
app = Flask(__name__)
client = MongoClient('mongodb+srv://sauryanshu55:YHhs6oJHj3W0X14z@cluster1.ayogdp8.mongodb.net/test')
db = client.TaskManager


"""
If name and TaskID not found, creates one for you
"""
if db.settings.find({'name': 'task_id'}).count() <= 0:
    print("task_id Not found, creating....")
    db.settings.insert_one({'name':'task_id', 'value':0})


"""
Searches for value given in the frontend, then if found, updates it
"""
def updateTaskID(value):
    task_id = db.settings.find_one()['value']
    task_id += value
    db.settings.update_one(
        {'name':'task_id'},
        {'$set':
            {'value':task_id}
        })

"""
Gets input about from the frontend from the ids="task_id","shortner" and "priority" and creates db entry. Redirectes to root URL as return URL
"""
def createTask(form):
    title = form.title.data
    priority = form.priority.data
    shortdesc = form.shortdesc.data
    task_id = db.settings.find_one()['value']
    
    task = {'id':task_id, 'title':title, 'shortdesc':shortdesc, 'priority':priority}

    db.tasks.insert_one(task)
    updateTaskID(1)
    return redirect('/')

"""
Searches for key from the form inoput in the front end. If exists then deletes it, else removes the "title" from the db entry
"""
def deleteTask(form):
    key = form.key.data
    title = form.title.data

    if(key):
        print(key, type(key))
        db.tasks.delete_many({'id':int(key)})
    else:
        db.tasks.delete_many({'title':title})

    return redirect('/')


"""
similar to updateTaskID, differtent in that it changes the contents of the short description parameter
"""
def updateTask(form):
    key = form.key.data
    shortdesc = form.shortdesc.data
    
    db.tasks.update_one(
        {"id": int(key)},
        {"$set":
            {"shortdesc": shortdesc}
        }
    )

    return redirect('/')


"""
Resets the opened database if the endpoint is reached"""
def resetTask(form):
    db.tasks.drop()
    db.settings.drop()
    db.settings.insert_one({'name':'task_id', 'value':0})
    return redirect('/')



"""
Read root, directs to templates/home.html. Uses GET,POST methods to create as well as request HTTP
"""
@app.route('/', methods=['GET','POST'])
def main():
    # form creaion
    cform = CreateTask(prefix='cform')
    dform = DeleteTask(prefix='dform')
    uform = UpdateTask(prefix='uform')
    reset = ResetTask(prefix='reset')

    # response
    if cform.validate_on_submit() and cform.create.data:
        return createTask(cform)
    if dform.validate_on_submit() and dform.delete.data:
        return deleteTask(dform)
    if uform.validate_on_submit() and uform.update.data:
        return updateTask(uform)
    if reset.validate_on_submit() and reset.reset.data:
        return resetTask(reset)


    docs = db.tasks.find()
    data = []
    for i in docs:
        data.append(i)

    return render_template('home.html', cform = cform, dform = dform, uform = uform, \
            data = data, reset = reset)
