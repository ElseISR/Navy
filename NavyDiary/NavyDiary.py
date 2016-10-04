# -*- coding: utf-8 -*-
"""
    Navy Diary
    ~~~~~~
    A simple diary that include the next functionalities:
		1. Adding new event.
		2. Modifying event.
		3. Deleting event.
		4. Searching event by date.
		5. Searching event by subject.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from shutil import copyfile

# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'NavyDiary.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

		
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/exportdb', methods=['GET', 'POST'])
def exportdb():    
    if not copyfile(os.path.join(app.root_path, 'NavyDiary.db'),os.path.join(app.root_path, 'NavyDiary_BU.db')):
        flash("All the events were exported successfully (NavyDiary_BU.db)")		
        return redirect(url_for('show_entries'))
    else:
        flash("Failed to export the events")		
        return redirect(url_for('show_entries'))

		
@app.route('/importdb', methods=['GET', 'POST'])
def importdb():
    if os.path.isfile(os.path.join(app.root_path, 'NavyDiary_BU.db')):
        copyfile(os.path.join(app.root_path, 'NavyDiary_BU.db'),os.path.join(app.root_path, 'NavyDiary.db'))
        flash("All the events were imported successfully")		
        return redirect(url_for('show_entries'))
    else:
        flash("Failed to import the events")		
        return redirect(url_for('show_entries'))

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select * from entries order by ydate asc,mdate asc,ddate asc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/search_by_subject', methods=['GET', 'POST'])
def search_by_subject():
    db = get_db()
    cur = db.execute("select * from entries where subject=? order by id desc",[request.form['subject']])
    entries = cur.fetchall()
    if not entries:
        flash("Not found")        
        return render_template('SearchPage.html')
    else:
        return render_template('show_entries.html', entries=entries)    

@app.route('/search_by_content', methods=['GET', 'POST'])
def search_by_content():
    db = get_db()
    cur = db.execute("select * from entries where text=? order by id desc",[request.form['text']])
    entries = cur.fetchall()
    if not entries:
        flash("Not found")        
        return render_template('SearchPage.html')
    else:
        return render_template('show_entries.html', entries=entries)


@app.route('/search_by_date', methods=['GET', 'POST'])
def search_by_date():
    if NumericValidate(request.form['date']):
    	DList=map(int,request.form['date'].split("/"))       
        if datesrangeValidate(DList):	
            db = get_db()
            cur = db.execute("select * from entries where ddate=? and mdate=? and ydate=? order by id desc",[DList[0], DList[1], DList[2]])
            entries = cur.fetchall()
            if not entries:
                flash("Not found")        
                return render_template('SearchPage.html')
            else:
                return render_template('show_entries.html', entries=entries)
        else:
            flash("Invalid dates")        
            return render_template('SearchPage.html')
    else:
           	flash("Invalid dates")        
	    	return render_template('SearchPage.html')

def datesrangeValidate(tmpList):
        if not tmpList[0] or tmpList[1] or tmpList[2]:
            if tmpList[0]>0 and tmpList[0]<=31 and tmpList[1]>0 and tmpList[1]<=12 and tmpList[2]>0 and tmpList[2]<=3000:
                return True
            else:
                return False
        else:
            return False

def NumericValidate(tmp):
    try:
        if tmp.count("/")==2:   
            tmpList=tmp.split("/")
            map(int,tmpList)
            return True
        else:
            return False
    except ValueError:
        return False
	
@app.route('/search_by_dates_range', methods=['GET', 'POST'])
def search_by_dates_range():
    if NumericValidate(request.form['FDate']) and NumericValidate(request.form['TDate']):
    	FDList=map(int,request.form['FDate'].split("/"))
        TDList=map(int,request.form['TDate'].split("/"))
        if datesrangeValidate(FDList) and datesrangeValidate(TDList):	
            db = get_db()
            if FDList[2]<TDList[2]:
                cur = db.execute("select * from entries where ydate>=? and ydate<=? order by id desc",[FDList[2], TDList[2]])
            elif FDList[2]==TDList[2] and FDList[1]<TDList[1]:
                cur = db.execute("select * from entries where mdate>=? and mdate<=? and ydate=? order by id desc",[FDList[1], TDList[1],FDList[2]])		
            elif FDList[2]==TDList[2] and FDList[1]==TDList[1] and FDList[0]<TDList[0]:
                cur = db.execute("select * from entries where ddate>=? and ddate<=? and mdate=? and mdate=? and ydate=? and ydate=? order by id desc",[FDList[0], TDList[0], TDList[1], TDList[1], TDList[2], TDList[2]])	
            else:
	    		flash("Not Found")    	
		    	return render_template('SearchPage.html')
            entries = cur.fetchall()
            if not entries:
                flash("Not found")        
                return render_template('SearchPage.html')
            else:
                return render_template('show_entries.html', entries=entries)            
        else:
            flash("Invalid dates")        
            return render_template('SearchPage.html')
    else:
           	flash("Invalid dates")        
	    	return render_template('SearchPage.html')
		
@app.route('/search', methods=['GET', 'POST'])
def search():
    return render_template('SearchPage.html')    

@app.route('/add_page', methods=['GET', 'POST'])
def add_page():
    return render_template('AddPage.html')       		

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()    
    cur = db.execute("select * from entries")
    entries = cur.fetchall()
    if NumericValidate(request.form['date']):
        DList=map(int,request.form['date'].split("/"))       
        if datesrangeValidate(DList):	            
            db.execute('insert into entries (ddate, mdate, ydate, subject, text) values (?, ?, ?, ?, ?)',[DList[0], DList[1], DList[2], request.form['subject'], request.form['text']])            
            db.commit()
            flash('New event was added successfully')
            return redirect(url_for('show_entries'))
        else:
            flash("Invalid date")        
            return render_template('AddPage.html')
    else:
           	flash("Invalid date")        
	        return render_template('AddPage.html')

@app.route('/update', methods=['GET', 'POST'])
def update():
    db = get_db()
    cur = db.execute("select * from entries WHERE id=?",[request.form['id']])
    entries = cur.fetchall()
    if NumericValidate(request.form['date']):
        DList=map(int,request.form['date'].split("/"))       
        if datesrangeValidate(DList):	            
            db.execute("update entries set ddate=?, mdate=?, ydate=?, subject=?, text=? where id=?",[DList[0], DList[1], DList[2], request.form['subject'], request.form['text'], request.form['id']])    
            db.commit()
            flash('The event was updated successfully')
            return redirect(url_for('show_entries'))
        else:
            flash("Invalid date")        
            return render_template('modifypage.html', entries=entries)
    else:
           	flash("Invalid date")        
	        return render_template('modifypage.html', entries=entries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/modify', methods=['GET', 'POST'])
def modify():   	
    db = get_db()    
    cur = db.execute("select * from entries WHERE id=?",[request.form['id']])
    entries = cur.fetchall()
    return render_template('modifypage.html', entries=entries)

@app.route('/delete', methods=['POST'])
def delete():   	
    db = get_db()
    db.execute("delete from entries where id=?",[request.form['id']])    
    db.commit()
    flash('The event was deleted successfully')
    return redirect(url_for('show_entries'))
 	

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))