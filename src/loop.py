#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#----------------------------------------------------------------------------
# Created By  : Igor Usunariz
# Created Date: 2022/04/20
# version ='2.0'
# Mail = 'i.usunariz.lopez@gmail.com'
#
# ---------------------------------------------------------------------------
# 
# PARENT LOOP MODULE
#
# Dependencies
# json, message
#
# ---------------------------------------------------------------------------

from os import path as ospath
from os import makedirs, remove
from sys import platform, exc_info, argv

from copy import deepcopy
import queue

from time import time, sleep
from datetime import datetime
import json

from message import send_message

class loop():
	def __init__(self, *args):
    	# EXTERNAL PARAMETERS
		if len(args) > 0:
			self.get_external_parameters(args[0])

    	# PARENT CONFIGURATION
		self.parent_configuration()

		# CHILD CONFIGURATION
		self.configuration()

		# GET PATHS
		self.get_paths()

		# READ EXTERNAL CONFIGURATION FILE (if exists)
		self.external_configuration()	

		# FINISH CONFIGURATION (functions requiring child_configuration data)
		self.finish_configuration()

		# LAUNCH MAIN LOOP
		self.main_loop()

	# CONFIGURATION
	def get_external_parameters(self, args):
		self.external = {
			'name': None,
			'conf_file': None,
		}

		self.log_queue = list()

		# Definimos un flag para indicar que ya ha sido configurado de forma externa (así podemos asignar prioridades)
		configured = False

    	# Desde CMD => Recorremos argv y buscamos valores con flag (-x), y en función del flag guardamos el valor en su correspondiente parámetro
		try:
			for i in range(1, len(argv), 2):
				flag = argv[i]
				param = argv[i+1]
				if flag[0] == '-':
					if flag == '-n':
						self.external['name'] = param
						message = f"CMD - External name parameter found: {param}"
						self.log_queue.append(message)
					elif flag == '-c':
						self.external['conf_file'] = param
						message = f"CMD - External configuration file parameter found: {param}"
						self.log_queue.append(message)
				
				# Ponemos a true el flag de que ya ha sido configurado el loop
				configured = True
		except Exception as e:
			self.log_queue.append(f"CMD ARGV parameters error:\n  - {e}")
			configured = False

    	# Desde Python => Recorremos args y buscamos valores con flag (-x), y en función del flag guardamos el valor en su correspondiente parámetro
		if not configured:
			try:
				for i in range(0, len(args), 2):
					flag = args[i]
					param = args[i+1]
					if flag[0] == '-':
						if flag == '-n':
							self.external['name'] = param
							message = f"PYTHON - External name parameter found: {param}"
							self.log_queue.append(message)				
						elif flag == '-c':
							self.external['conf_file'] = param
							message = f"PYTHON - External configuration file parameter found: {param}"
							self.log_queue.append(message)

				# Ponemos a true el flag de que ya ha sido configurado el loop				
				configured = True
			except Exception as e:
				self.log_queue.append(f"PYTHON ARGS parameters error:\n  - {e}")
				configured = False

	def parent_configuration(self):
		# INIZIALIZATION
		self.config = {
			'name': self.external['name'],
			'conf_file': self.external['conf_file'],
			'debug': False,
		}

		# CHECK NAME
		if self.config['name'] is None: self.config['name'] = 'loop'

		# QUEUE
		self.config['queue'] = {}
		self.config['queue']['maxsize'] = 10

		# LOOP TIMING AND ITERATIONS
		self.config['loop'] = {
			'timing': 1,
			'max_it': float('inf'),
		}

		# STATE MACHINE
		self.config['state_machine'] = ['initialize', 'run', 'error', 'exit_req', 'exit']

		# SUBSTATE MACHINE
		self.config['substate_machine'] = []
		
		# PARENT VERBOSE
		self.verbose = True
	
	def configuration(self):
    	# Polimorphic method
		pass

	def finish_configuration(self):
    	# GET TAG
		self.get_tag()

		# PUBLISH CONFIGURATION
		self.publish_parent_configuration()
		self.publish_configuration()
    		
	def external_configuration(self):
    	# Comprobamos si hemos definido un archivo de configuración por defecto
		if not self.config['conf_file'] is None:
			# Obtenemos el nombre del archivo de configuración externo a utilizar	
			conf_file = f"{self.paths['config']}{self.paths['sep']}{self.config['conf_file']}"

			if ospath.isfile(conf_file):
				# Guardamos en el log el archivo usado
				message = f"Configuration file found: {self.config['conf_file']}"
				self.log_queue.append(message)

				# Leemos el archivo -> SIEMPRE EN FORMATO JSON
				with open(conf_file) as jsonfile:
					config = json.load(jsonfile)

				# Recorremos cada key en el archivo de configuración
				for cfg in config:
					if cfg in self.config.keys():
						# Si esa key pertenece a self.config, comprobamos si es un diccionario (para anidar bucles)
						if isinstance(config[cfg], dict):
							# Si SI es un diccionario, recorremos cada key dentro del diccionario
							for key in config[cfg]:
								if key in self.config[cfg].keys():
									# Si la key del diccionario existe en la correspondiente en self.config[cfg], asignamos su valor
									self.config[cfg][key] = config[cfg][key]
						else:
							# Si NO es un diccionario, asignamos el valor directamente (ya sabemos que existe)
							self.config[cfg] = config[cfg]

	def publish_parent_configuration(self):
		self.log_queue.append(f"{self.config['name'].upper()} application launched!")
		self.log_queue.append(f"Tag: {self.config['tag']}")
		self.log_queue.append(f"Debug mode: {self.config['debug']}")
		self.log_queue.append(f"Configuration LOOP: Total of {self.config['loop']['max_it']} iterations with timing of {self.config['loop']['timing']} seconds")

	def publish_configuration(self):
    	# Polimorphic method
		pass

	def get_tag(self):
		self.config['tag'] = ''

	# PATHS
	def get_paths(self):
		# Initialize dictionary
		self.paths = {}

		# GET PATH SEPARATOR (depending on Operating System)
		if platform == 'win32':
			self.paths['sep'] = '\\'
		elif platform == 'linux':
			self.paths['sep'] = '/'

		# ROOT PATH
		self.paths['root'] = ospath.abspath(__file__).split(self.paths['sep'])[0:-2]

		# APP PATH (partimos de self.paths['root'])
		self.paths['app'] = deepcopy(self.paths['root'])
		self.paths['app'].append(self.config['name'])

		# LOGS PATH (partimos de self.paths['app'])
		self.paths['logs'] = deepcopy(self.paths['app'])
		self.paths['logs'].append('logs')

		# CONFIG PATH
		self.paths['config'] = deepcopy(self.paths['app'])
		self.paths['config'].append('config')

		# Obtenemos los paths particulares de la aplicacion
		self.get_app_paths()

		# Construimos el path en formato string
		self.build_paths()

		# Creamos la estructura de carpetas
		self.create_folder_structure()

	def get_app_paths(self):
    	# Polimorphic method
		pass

	def build_paths(self):
    	# Recorremos todos los almacenados en self.paths y los construimos contra self.paths_sep
		for path in self.paths:
    		# Evitamos el separador
			if not path == 'sep':
				self.paths[path] = self.paths['sep'].join(self.paths[path])

				message = f"Path - {path.upper()}: {self.paths[path]}"
				self.log_queue.append(message)
	
	# FOLDERS
	def create_folder_structure(self):
    	# Recorremos los paths
		for path in self.paths:
    		# Evitamos crear carpetas para 'sep' y 'root'
			if not path in ['sep', 'root']:
				# Comprobamos si existe la carpeta, y en caso de que no, la creamos
				if not ospath.exists(self.paths[path]):
					makedirs(self.paths[path])

	# QUEUE
	def create_queue(self):
		self.queue = queue.Queue(maxsize = self.config['queue']['maxsize'])

	def check_queue(self):
		# Comprobamos la queue de mensajes
		messages = []
		try:
			# Get all messages
			while True:
    			# Leemos el mensaje y lo procesamos
				messages.append(self.queue.get_nowait())
				self.check_message(messages[-1])
		except Exception  as e:
			# When no message is in queue, exception is raised
			pass

		ret_val = messages

		return ret_val
	
	def check_message(self, message):
		# Common actions
		if message.action == 'write_log':
			self.dump_log(timestamp = message.timestamp, sender = message.sender, payload = message.payload, level = message.level)
		elif message.action == 'error':
			self.set_next_state('error')

	# MAIN LOOP
	def main_loop(self):
		# Before main loop
		self.main_loop_initialization()

		# Main loop
		while not self.state_machine['exit']:
			self.main_loop_execution()

		# After main loop
		self.main_loop_exit()

	def main_loop_initialization(self):
		# CREATE QUEUE
		self.create_queue()

		# CREATE LOG
		self.open_log()

		# DEFINE STATE MACHINE, SUBSTATE MACHINE AND LOOP VARIABLES
		self.state_machine = {
			'previous': '', 
			'current': '',
			'next': '',
			'exit_req': False,
			'exit': False
		}

		self.substate_machine = {
			'previous': '', 
			'current': '',
			'next': '',
		}

		self.loop = {
			'timing': {
				'ini': time(),
				'ini_it': None,
				'state': None,
				'it': None,
				'total': None,
			},
			'it': 0,
		}

		self.set_next_state('initialize')

	def main_loop_execution(self):
    	# Update ini main loop
		self.main_loop_update_ini()

		# Check for messages in queue
		self.check_queue()

		# Execute current state
		self.main_loop_exec_state()

		# Update end main loop
		self.main_loop_update_end()

	def main_loop_exit(self):
		timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
		payload = f"(INFO) Succesfully exited from application! Total duration time of {self.loop['timing']['total']} seconds"

		self.dump_log(timestamp = timestamp, sender = self.config['name'], payload = payload)

		self.close_log()

	def main_loop_update_ini(self):
		# Get initial time
		self.loop['timing']['ini_it'] = time()

		# Update State machine state
		self.state_machine['current'] = self.state_machine['next']
		self.substate_machine['current'] = self.substate_machine['next']

		# Update it counter
		if not self.state_machine['current'] in ['exit_req', 'exit']:
			self.loop['it'] += 1

	def main_loop_exec_state(self):
		try:
			aux_state = 'self.' + self.state_machine['current'] + '()'
			exec(aux_state)

		except Exception as e:
			self.error_handler(e)

	def main_loop_exec_substate(self):
		try:
			aux_substate = 'self.' + self.substate_machine['current'] + '()'
			exec(aux_substate)

		except Exception as e:
			self.error_handler(e)
			
	def main_loop_update_end(self):
    	# Update state time
		self.loop['timing']['state'] = round(time() - self.loop['timing']['ini_it'], 3)

		# Comprobamos si hay que esperar (si el tiempo de ejecución del estado es menor que el umbral y no queremos salir)
		if (self.loop['timing']['state'] < self.config['loop']['timing']) and (not self.state_machine['current'] in ['exit_req', 'exit']):
			# Calculamos el tiempo a esperar
			wait_time = round(self.config['loop']['timing'] - self.loop['timing']['state'], 3)

			# Esperamos
			sleep(wait_time)

		# Actualizamos el estado anterior
		self.state_machine['previous'] = self.state_machine['current']
		self.substate_machine['previous'] = self.substate_machine['current']
			
		# Check for iteration counter exit
		if self.loop['it'] >= self.config['loop']['max_it']: 
			self.state_machine['exit_req'] = True

		# Check for external reset or stop request
		if self.check_external_request('restart'): self.set_next_state('initialize', forced = True)
		if self.check_external_request('stop'): self.set_next_state('exit_req', forced = True)

		# Check exit_req flag
		if (self.state_machine['exit_req']) and (not self.state_machine['next'] == 'exit'): self.set_next_state('exit_req')

		# Update it and total time
		self.loop['timing']['it'] = round(time() - self.loop['timing']['ini_it'], 3)
		self.loop['timing']['total'] = round(time() - self.loop['timing']['ini'], 3)

		# Message update_end
		message = f"Iteration {self.loop['it']} of {self.config['loop']['max_it']} => SM: {self.state_machine['current'].upper()} / SubSM: {self.substate_machine['current'].upper()} => Total Time: {self.loop['timing']['total']} sec (state: {self.loop['timing']['state']}, loop: {self.loop['timing']['it']} sec)"
			
		self.write_log(message)

	# STATE MACHINE NEXT STATE MANAGER
	def set_next_state(self, state, forced = False):
		if state in self.config['state_machine']:
			self.state_machine['next'] = state

			message = f"Next state set to \'{state.upper()}\'"
			if forced:
				message += ' (forced)'

			self.write_log(payload = message)

	def set_next_substate(self, substate):
		if substate in self.config['substate_machine']:
			self.substate_machine['next'] = substate

		message = f"Next substate set to \'{substate.upper()}\'"
		self.write_log(payload = message)

	def check_external_request(self, action):
		# Creamos la ruta del archivo
		file_name = f"{action}_{self.config['name']}_{self.config['tag']}.ctrl".replace('_.', '.')
		file = f"{self.paths['app']}{self.paths['sep']}{file_name}"

		# Comprobamos si el archivo existe
		ret_val = ospath.exists(file)
		if ret_val:
			# Si existe, lo borramos
			remove(file)

		return ret_val

	# STATE MACHINE LOGIC
	def initialize(self):
    	# Polimorphic method
		pass

	def run(self):
		# Not edit
		self.main_loop_exec_substate()

	def error(self):
    	# Polimorphic method
		pass

	def exit_req(self):
    	# Polimorphic method

		# Salimos de la aplicación
		self.set_next_state('exit')

	def exit(self):		
		self.state_machine['exit'] = True

	# LOG
	def open_log(self):
    	# Obtenemos el nombre del archivo de log
		dt = self.get_now_str().replace('/', '').replace(':', '').replace(' ', '_')
		self.config['log_file'] = f"log_{self.config['name']}_{self.config['tag']}_{dt}.log".replace('__', '_')

		# Creamos el archivo de log
		log_path = f"{self.paths['logs']}{self.paths['sep']}{self.config['log_file']}"
		self.log = open(log_path, 'a')

		# Leemos la cola de logs de inicialización
		self.read_log_queue()

	def read_log_queue(self):
		for log in self.log_queue:
			self.write_log(log)

	def write_log(self, payload, sender = None, level = 'INFO'):
		if sender is None:
			sender = self.config['name']

		# Instanciamos sin enviar un mensaje (tipo Message)
		message = send_message(queue = None, action = 'write_log', payload = payload, sender = sender, level = level)

		# Lo escribimos en log
		self.dump_log(timestamp = message.timestamp, sender = message.sender, payload = message.payload, level = message.level)

	def dump_log(self, timestamp, sender, payload, level):
		log = f"{timestamp} -> {sender.upper()}\t=> ({level.upper()}) "

		log += payload
		log += '\n'

		self.log.write(log)

		if self.verbose:
			print(log)

		# Flush the log file and return the result
		self.log.flush()

	def close_log(self):
		# Intentamos cerrar el log. Si ya esta cerrado devolverá error
		try:
			self.log.close()
		except:
			pass

	# ERROR HANDLER
	def error_handler(self, e = None):
		exc_type, exc_value, exc_traceback = exc_info() # most recent (if any) by default

		traceback_details = {
							'filename': exc_traceback.tb_frame.f_code.co_filename,
							'sm'	  : self.state_machine['current'],
							'subsm'   : self.substate_machine['current'],
							'function': exc_traceback.tb_frame.f_code.co_name,
							'lineno'  : exc_traceback.tb_lineno,
							'msg'	  : exc_value,
							}
		
		traceback_details['filename'] = traceback_details['filename'].split('\\')[-1]

		message = f"{traceback_details['filename']} - SM: \'{traceback_details['sm']}\' - SUBSM: \'{traceback_details['subsm']}\' -> {traceback_details['function']}, Line {traceback_details['lineno']} => {traceback_details['msg']}\n\t - {e}"

		if self.verbose:
			print(message)
    
		self.write_log(payload = message, level = 'ERROR')

		send_message(queue = self.queue, action = 'error', payload = e)

	# AUXILIAR FUNCTIONS
	def get_now_str(self):
		return str(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

	
if __name__ == '__main__':
	x = loop()
