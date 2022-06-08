"""
 * Componente Curricular: MI Concorrência e Conectividade
 * Autor: 
 *
 * Declaro que este código foi elaborado por mim de forma individual e
 * não contém nenhum trecho de código de outro colega ou de outro autor,
 * tais como provindos de livros e apostilas, e páginas ou documentos
 * eletrônicos da Internet. Qualquer trecho de código de outra autoria que
 * uma citação para o  não a minha está destacado com  autor e a fonte do
 * código, e estou ciente que estes trechos não serão considerados para fins
 * de avaliação. Alguns trechos do código podem coincidir com de outros
 * colegas pois estes foram discutidos em sessões tutorias.
"""
import paho.mqtt.client as mqtt
import json
import sys
import os
import threading
import base64
import re
from collections import deque
from database_control import DatabaseControl

class Subscriber:

	HOST = 'mqtt.eclipseprojects.io'
	PORT = 1883
	
	# Servidor
	server_socket = None
	
	mqtt_server = None
	
	topic = ''
	
	# Controlador da base de dados
	database = None
	
	queue_request = None
	thread_request = None
	
	controllevels = None
	
	close = False
	
	def __init__(self):
		# Iniciando o Server
		self.mqtt_server = mqtt.Client('G02_THEBESTGROUP')
		self.mqtt_server.connect(self.HOST, self.PORT)
		self.topic = 'G02_THEBESTGROUP/MEDICOES'
		self.db_control = DatabaseControl()
		self.queue_request = deque()
		self.thread_request = threading.Thread(target=self.queue)
		self.thread_request.start()
		print('SERVER ON\n')
		self.work()
	
	def on_connect(self, client, userdata, flags, rc):
		self.mqtt_server.subscribe(self.topic)
		print("Connected to a broker!")

	def on_message(self, client, userdata, message):
		print(message.payload.decode())
		self.receptor(message.payload.decode())
	
	# Função principal, onde o servidor irá receber as conexões
	def work(self):
		while not self.close:
			self.mqtt_server.on_connect = self.on_connect
			self.mqtt_server.on_message = self.on_message
			self.mqtt_server.loop_forever()
		
		if(self.close and len(self.queue_request) == 0):
			print('SERVER OFF')
			return sys.exit()
	
	# Trata os dados recebidos
	def receptor(self, request):
		data = None
		
		# Verificando se é realmente o cliente
		if('raspberry' not in request):
			print('Conexão externa.')
			return
		
		if('close' not in request):
			print('Fechando o servidor.')
			self.close = True
			sys.exit()
			
		for index in request:
			if(index == '{'):
				data = json.loads(request[request.find('{') : request.find('}') + 1])
		
		# Adicionando a requisição a fila de requisições
		if(index != None):
			self.queue_request.append({'data': data})
	
	# Consome a fila de requisições
	def queue(self):
		while True:
			if(len(self.queue_request) > 0):
				print('conn: ' + str(len(self.queue_request)))
				request = self.queue_request.popleft()
				self.routing(request['data'])
	
	# Função responsável pelo roteamente, identifica os metodos e as rotas requisitadas
	def routing(self, data):
		print('...')
		print(data)
		print('...')
		if('H' not in data or 'T' not in data or 'P' not in data or 'L' not in data):
			return self.data_not_found()
		return self.insert_measure(data)
	# Envia dados para o cliente em caso de sucesso
	def send_to_client_ok(self, obj):
		response = json.dumps({'success': True, 'data': obj})
		print(response)
		return True
	
	# Envia dados para o cliente em caso de erro
	def send_to_client_error(self, msg):
		response = json.dumps({'success': False, 'error': msg})
		print(response)
		return False
	
	# Caso a rota informada não esteja dentre as disponiveis
	def data_not_found(self):
		return self.send_to_client_error('Nao foram encontrado corretos dados na requisicao')

	# Atualiza todos os atributos de um paciente
	def insert_measure(self, data):
		success = self.db_control.insert_measure(data)
		if(success == False):
			return self.send_to_client_error('Nao foi possivel inserir a medicao.')
		
		return self.send_to_client_ok(success)

if __name__ == '__main__':
	server = Subscriber()
	server.work()
			