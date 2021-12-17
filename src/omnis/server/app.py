from threading import Thread

from flask import Flask, Response, request, session,copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from flask_cors import CORS

from threading import Lock
from waitress import serve
from engineio.payload import Payload
import json
Payload.max_decode_packets = 500

class Server(object):
    def __init__(self, app_ip, app_port, report_time, buildfolder,**kargs):
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

        self.report_time = report_time
        self.buildfolder = buildfolder
        self.thread_lock = Lock()
        self.port = app_port
        self.thread = None
        self.ip = app_ip
        #, static_folder = f"{self.buildfolder}/static",
        self.app = Flask(__name__, template_folder = self.buildfolder)
        CORS(self.app)
        self.process = {}
        self.defineRoutes()
        self.cameras = kargs.get("cameras")
        self.functions = kargs.get("functions")
        self.app.config['SECRET_KEY'] = 'secret!'
        self.socketio = SocketIO(self.app, async_mode=None, async_handlers=True, cors_allowed_origins='*')
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
                print('Updating all clients')
                socketio.emit('RESPONSE_MESSAGE',
                           {'data': json.dumps(update, indent=2, ensure_ascii=False)})
                # sleep((self.report_time))
                socketio.sleep(self.report_time)


        # @app.route('/')
        # def index():
            print("Initial Page accessed")
            #socketio.emit('echo')
            # return "Bão"
            #return render_template('index.html', async_mode=socketio.async_mode)

    

        @socketio.on('custom_click')
        def custom_click(message):
            print("recebi: ", message)
            print('respondendo')
            emit('RESPONSE_MESSAGE', {"command":"startAutoCheck_success", "data":"ok"})


        @socketio.on('my_event')
        def my_broadcast_event(message):
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('RESPONSE_MESSAGE',
                {'data': message['data'], 'count': session['receive_count']},
                broadcast=True)
        
        @socketio.on('call_function')
        def call_function(message):
            print(message)
            try:
                function = self.functions[message["command"]]
                thread = Thread(target=function)
                self.process[message["command"]] = thread
                thread.start()
                emit('RESPONSE_MESSAGE', {'data': f"{message['command']} started"})
            except TypeError:
                print('None function has ben defined...')
                emit('RESPONSE_MESSAGE',
                    {'data': "None function has ben defined..."})
            except KeyError:
                print("The [{message['command']}] function is not accessible")
                emit('RESPONSE_MESSAGE',
                    {'data': f"The [{message['command']}] function is not accessible"})
            


        @socketio.on('my_event')
        def join(message):
            join_room(message['room'])
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('RESPONSE_MESSAGE',
                {'data': 'In rooms: ' + ', '.join(rooms()),
                'count': session['receive_count']})


        @socketio.on('my_event')
        def leave(message):
            leave_room(message['room'])
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('RESPONSE_MESSAGE',
                {'data': 'In rooms: ' + ', '.join(rooms()),
                'count': session['receive_count']})


        @socketio.on('close_room')
        def on_close_room(message):
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('RESPONSE_MESSAGE', {'data': 'Room ' + message['room'] + ' is closing.',
                                'count': session['receive_count']},
                to=message['room'])
            close_room(message['room'])


        @socketio.on('my_event')
        def my_room_event(message):
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('RESPONSE_MESSAGE',
                {'data': message['data'], 'count': session['receive_count']},
                to=message['room'])


        @socketio.on('my_event')
        def disconnect_request():
            @copy_current_request_context
            def can_disconnect():
                disconnect()

            session['receive_count'] = session.get('receive_count', 0) + 1
            # for this emit we use a callback function
            # when the callback function is invoked we know that the message has been
            # received and it is safe to disconnect
            emit('RESPONSE_MESSAGE',
                {'data': 'Disconnected!', 'count': session['receive_count']},
                callback=can_disconnect)


        @socketio.on('my_event')
        def my_ping():
            emit('my_pong')


        @socketio.on('start_updates')
        def start_updates():
            global thread
            with self.thread_lock:
                print("Recive resquest to starting a threading uptade")
                if self.thread is None:
                    print("updating thread started")
                    thread = socketio.start_background_task(background_thread)
            emit('RESPONSE_MESSAGE', {'data': 'Connected', 'count': 0})


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
            



