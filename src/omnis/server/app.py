from threading import Thread

from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO, send
from waitress import serve

from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
#from ..camera.device import new_camera as camera
from engineio.payload import Payload
import json
Payload.max_decode_packets = 500

class Server(object):
    def __init__(self, app_ip, app_port, report_time, **kargs):
        """
            ### Parameters
            @app_ip :\n
                - type -> (str)\n
                - ip from socketio connection\n
                    'localhost' or '127.0.0.1' also work.

            @app_port :\n
                - type -> (int)\n
                - port from socketio connection (0000:9999)\n

            @report_time : int
            - After 'n' seconds, server run a background Thread.\n
                Backgorund Thread: report all avaliable threads, and if they are running or not. 

            Raises
            ------
            - ServerCrash
                - [description]
            - ServerLosingConection
                - [description]
            - ServerStopResponse
                - [description]
        """
        #Thread.__init__(self)
        # self.app = Flask(__name__, static_folder = f"{buildfolder}/static",
        #                         template_folder = buildfolder)

        self.ip = app_ip
        self.port = app_port
        self.report_time = report_time

        self.thread = None
        self.thread_lock = Lock()
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'secret!'
        self.socketio = SocketIO(self.app, async_mode=None, async_handlers=True)
        self.functions = kargs.get("functions")
        self.cameras = kargs.get("cameras")
        self.process = {}
        self.defineRoutes()
    def start(self):
        
        print("rodando....")
        self.socketio.run(self.app, host=self.ip, port=self.port)
        print("parou!")

    def addCamera(self, nome, valor):
        self.cameras[nome] = valor
    
    def removeCamera(self, nome):
        self.cameras.pop(nome)

    def addFunction(self, name, function):
        self.functions[name] = function

    def removeFunction(self, name):
        self.functions.remove(name)

    def stop(self):
        serve.graceful_shutdown()

    def stopped(self):
        return self._stop_event.is_set()

    def shutdown_server(self):
        self.socketio.stop()
        return "Server stopped"

    def defineRoutes(self):
        app = self.app
        socketio = self.socketio
        def background_thread():
            """Example of how to send server generated events to clients."""
            while True:
                update = {}
                for k, v in self.process.items():
                    update[k] = {"alive": v.is_alive()}
                socketio.emit('my_response',
                            {'data': json.dumps(update, indent=2, ensure_ascii=False)})
                socketio.sleep(self.report_time)


        @app.route('/')
        def index():
            return render_template('index.html', async_mode=socketio.async_mode)


        @socketio.event
        def my_event(message):
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('my_response',
                {'data': message['data'], 'count': session['receive_count']})


        @socketio.event
        def my_broadcast_event(message):
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('my_response',
                {'data': message['data'], 'count': session['receive_count']},
                broadcast=True)
        
        @socketio.event
        def trigger_this(message):
            print(message)
            try:
                function = self.functions[message["command"]]
                thread = Thread(target=function, args=(), kwargs={})
                self.process[message["command"]] = thread
                thread.start()
                
                emit('my_response',
                    {'data': "ok", 'count': session['receive_count']})
            except TypeError:
                emit('my_response',
                    {'data': "Nenhuma função foi definida...", 'count': session['receive_count']})
            except KeyError:
                emit('my_response',
                    {'data': f"A função [{message['command']}] não está acessivel", 'count': session['receive_count']})


        @socketio.event
        def join(message):
            join_room(message['room'])
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('my_response',
                {'data': 'In rooms: ' + ', '.join(rooms()),
                'count': session['receive_count']})


        @socketio.event
        def leave(message):
            leave_room(message['room'])
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('my_response',
                {'data': 'In rooms: ' + ', '.join(rooms()),
                'count': session['receive_count']})


        @socketio.on('close_room')
        def on_close_room(message):
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                                'count': session['receive_count']},
                to=message['room'])
            close_room(message['room'])


        @socketio.event
        def my_room_event(message):
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('my_response',
                {'data': message['data'], 'count': session['receive_count']},
                to=message['room'])


        @socketio.event
        def disconnect_request():
            @copy_current_request_context
            def can_disconnect():
                disconnect()

            session['receive_count'] = session.get('receive_count', 0) + 1
            # for this emit we use a callback function
            # when the callback function is invoked we know that the message has been
            # received and it is safe to disconnect
            emit('my_response',
                {'data': 'Disconnected!', 'count': session['receive_count']},
                callback=can_disconnect)


        @socketio.event
        def my_ping():
            emit('my_pong')


        @socketio.event
        def connect():
            global thread
            with self.thread_lock:
                if self.thread is None:
                    thread = socketio.start_background_task(background_thread)
            emit('my_response', {'data': 'Connected', 'count': 0})


        @socketio.on('disconnect')
        def test_disconnect():
            print('Client disconnected', request.sid)

        # @app.route('/')
        # def index():
        #     """Video streaming home page."""
        #     return render_template('index.html')

        @app.route('/video_feed/<camera>')
        def video_feed(camera):
            try:
                return Response(getattr(self.cameras[camera], "stream")(),
                                mimetype='multipart/x-mixed-replace; boundary=frame')
            except KeyError:
                return f"{camera} is offline or disabled"

        @app.route('/kill_<camera>')
        def kill_camera(camera):
            try:
                getattr(self.cameras[camera], "stop")()
                self.removeCamera(camera)
            except KeyError:
                return f"{camera} is offline or disabled"
            return "Kill successfully"
        
        @app.route('/kill_server')
        def kill_server():
            for camera in self.cameras.values():
                camera.stop()
                #self.removeCamera(nome)
            return self.shutdown_server()
            



