import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, flash, request
from flask_socketio import SocketIO
from flask_socketio import send, emit
from random import random
import time
from threading import Thread, Event

		
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
async_mode = "eventlet"

socketio = SocketIO(app, async_mode=async_mode)
thread = None

def background_thread():                                                        
    while True:  
		file = open("temp.txt", "r")
		number = int(file.read())
		seconds = int(number / 30);
		output = str(seconds) + " seconds"                                                             
		socketio.emit('message', {'waittime': output})                        
		time.sleep(1)   

@socketio.on('message')
def handle_message(message):
	print('Message: ' + message)
	send(message, broadcast=True)

@socketio.on('json')
def handle_json(json):
	send(json, json=True)

@socketio.on('my event')
def handle_my_custom_event(json):
	emit('my response', json, broadcast=True)

@socketio.on('connect')                                                         
def connect():                                                                  
    global thread                                                               
    if thread is None:                                                          
        thread = socketio.start_background_task(target=background_thread)   
	
@app.route('/home.html')
def index():
    return render_template('home.html')

@app.route('/alerts.html')
def alerts():
    return render_template('alerts.html')

@app.route('/saved.html')
def saved():
    return render_template('saved.html')

@app.route('/searchresults.html')
def search():
    return render_template('searchresults.html')

@app.route('/newalert.html')
def newalert():
    return render_template('newalert.html')

@app.route('/Engineering5')
def engineering5():
    return render_template('e5.html')

@app.route('/categories.html')
def category():
    return render_template('categories.html')

@app.route('/271 West')
def restaurant():
    return render_template('business.html',name="271 West")

@app.route('/restaurants.html')
def restaurant111():
    return render_template('restaurants.html',name="Restaurants")

@app.route('/fastfood.html')
def page1():
    return render_template('restaurants.html',name="Fast Food")

@app.route('/coffee.html')
def page2():
    return render_template('restaurants.html',name="Coffee")

@app.route('/nightclubs.html')
def page3():
    return render_template('restaurants.html',name="Nightclubs")

@app.route('/bars.html')
def page4():
    return render_template('restaurants.html',name="Bars")

@app.route('/museums.html')
def page5():
    return render_template('restaurants.html',name="Museums")

@app.route('/attractions.html')
def page6():
    return render_template('restaurants.html',name="Attractions")

@app.route('/Bao Sandwich')
def page7():
    return render_template('business.html',name="Bao Sandwich")

@app.route('/Bauer Kitchen')
def restaurant3():
    return render_template('business.html',name="Bauer Kitchen")

@app.route('/Bhimas Warung')
def restaurant4():
    return render_template('business.html',name="Bhimas Warung")

@app.route('/Charcoal Steak House')
def restaurant5():
    return render_template('business.html',name="Charcoal Steak House")

@app.route('/Fork and Cork Grill')
def restaurant6():
    return render_template('business.html',name="Fork and Cork Grill")

@app.route('/Ken Sushi')
def restaurant7():
    return render_template('business.html',name="Ken Sushi")

@app.route('/Chainsaw')
def restaurant8():
    return render_template('business.html',name="Chainsaw")

@app.route('/The Yeti')
def restaurant9():
    return render_template('business.html',name="The Yeti")

@app.route('/Kinkaku')
def restaurant10():
    return render_template('business.html',name="Kinkaku")

@app.route('/Taco Farm')
def restaurant11():
    return render_template('business.html',name="Taco Farm")
		
if __name__ == '__main__':
	socketio.run(app)
