
import logging.config
import threading
import traceback
import serial
import time
import json
from ...util.color import color
from ..connections import serial_exp as ex
# from ..util.customException import *


"""
     0, conexão ok
    -1, porta ocupada
    -2, conexão inexistente
    -3, conexão perdida durante a comunicação

"""

# logging.config.fileConfig(r'C:\Users\osche\OneDrive\Documentos\GitHub\Rose_ADP\engine\data\log\config\log.ini', disable_existing_loggers=False)

class new(object):
    
    def __init__(self, name, port, baudrate, **kwargs):
        self.name = name
        self.port = port
        self.baudrate = baudrate
        self.code = -1
        self.serial = None
        self.reconnect = 0
        self.kwargs = kwargs

        self.codes = {
            0: ["conexão ok.", 'S'],
            -1: [f"porta [{self.port}] está ocupada!",'W'],
            -2: ["conexão inexistente!", 'E'],
            -3: ["conexão perdida durante a comunicação!", 'W'],
        }
        self.lock = threading.Lock()
        # try:
        #     self.open(self.port, self.baudrate, 3)
        # except ex.serialclosed:
        #     self.reopen()
        # if not self.isAlive():
        #     raise ex.serialclosed#(self.name, port=self.port, baudrate=self.baudrate, code=self.code)
    def start(self):
        try:
            self.open(self.port, self.baudrate, 3)
        except ex.serialclosed:
            self.reopen()
        if not self.isAlive():
             raise ex.serialclosed

    def reopen(self, limit=5, timer=2.5):
        self.reconnect +=1
        print(color(f"{self.name} não conseguiu estabeler conexão, tentanto pela [{self.reconnect}º] vez..", 'W'))
        if self.reconnect <= limit:
            if isinstance(self.serial, serial.serialwin32.Serial):
                self.close()
            # print(color(f"{self.name} não conseguiu estabeler conexão, tentanto pela [{self.reconnect}º] vez..", 'W'))
            
            try:
                self.open(self.port, self.baudrate, 3)
            except ex.serialclosed:
                t0 = time.monotonic() + timer
                while time.monotonic() < t0:
                    pass
                self.reopen(limit, timer)
        return self.isAlive()

    def open(self, port, baudrate, timeout):
        print(color(f"{self.name} está conectando...", 'I'))
        try:
            self.serial = serial.Serial(port, baudrate, timeout=timeout)
        except serial.serialutil.SerialException as exp:
            if "FileNotFoundError" in str(exp):
                self.code = -2
            elif 'Acesso negado.' in str(exp):
                self.code = -1
        else:
            print(color(f"{self.name} está confirmando a conexão...", 'I'))
            t0 = time.monotonic() + timeout
            while time.monotonic() < t0 and not self.isAlive():
                pass
            self.code = 0
        self.codePrint(self.code)
        if self.code != 0:
            raise ex.serialclosed#(self.name, port=self.port, baudrate=self.baudrate, code=self.code)
        else:
            self.reconnect = 0

    def isAlive(self):
        try:
            return self.serial.isOpen()
        except AttributeError:
            return False

    def codePrint(self,code):
        print(color(self.name+" >> "+self.codes[code][0],self.codes[code][1]))

    def statusCode(self):
        return self.code

    def close(self):
        self.serial.close()

    def clear(self):
        try:
            self.serial.flush()
            self.serial.flushInput()
            self.serial.flushOutput()

        except serial.serialutil.SerialException:
            if self.kwargs.get('reconnect'):
                    self.reopen()

    def send(self, command, **kargs):
        # Verifica se é possivel enviar dados através da conexão informada.
        if self.isAlive():
            self.lock.acquire(1)
            try:
                self.clear()

                
                # Verifica se é um unico comando
                if isinstance(command, str):
                    self.serial.write(
                        str(command + '{0}'.format('\n')).encode('ascii'))
                    # print('Enviado o comando: ' + command)
                # Verifica se é uma lista de comandos
                if isinstance(command, list):
                    for linha in command:
                        self.serial.write(
                            str(linha + '{0}'.format('\n')).encode('ascii'))

                # Verifica se é uma lista de comandos do tipo "dicionário".
                if isinstance(command, dict):
                    for linha in command:
                        self.serial.write(
                            str(command[linha] + '{0}'.format('\n')).encode('ascii'))
                
                strr = []
                if command.startswith('G0'):
                    print("\n"*2, '-'*5, 'Comando de movimentação recebido', '-'*5, '\n'*2)
                elif command.startswith('M41'):
                    print("\n"*2, '-'*5, 'Comando de parada recebido', '-'*5, '\n'*2)
                # Lê, decodifica e processa enquanto houver informação no buffer de entrada.
                while True:
                    b = self.serial.readline()
                    string_n = b.decode()
                    strr.append(string_n.rstrip())

                    # if b == b'':
                    #     print("b:", b, type(b))
                    #     print("string_n:", string_n, type(string_n))
                    #     print("string_n.rstrip():", string_n.rstrip(),
                    #         type(string_n.rstrip()))
                    #     break
                    if self.serial.inWaiting() == 0:
                        break

                    # if b == b'' or b == None or b is None:
                    #     self.code = -3
                    #     self.close()
                    #     raise ex.serialnotrespond#(self.name, port=self.port, baudrate=self.baudrate, code=self.code)

                # Limpa o buffer.
                
                # Se requisitado, retorna aquilo que foi recebido após o envio dos comandos.
                if kargs.get('echo'):
                    return strr

                return True
            except (serial.serialutil.SerialException, ex.serialnotrespond, ex.serialclosed):
                if self.kwargs.get('reconnect'):
                    if not self.reopen():
                        raise
                else:
                    raise
            finally:
                self.clear()
                self.lock.release()
                        
            # Avisa que o comando não pode ser enviado, pois a conexão não existe.
        else:
            if self.kwargs.get('reconnect'):
                    if not self.reopen():
                        raise ex.serialclosed#(self.name, port=self.port, baudrate=self.baudrate, code=self.code)
            return False
        #     return ["Comando não enviado, falha na conexão com a serial."]

# if __name__ == '__main__':
#     ardu = new_connection("nome", "com4", 9600)