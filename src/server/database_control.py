"""
 * Componente Curricular: 
 * Autor: Esdras Abreu, Guilherme Nobre e Kevin Cerqueira
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

import os
import json
import uuid
from datetime import datetime
import platform

# Classe para controlar a base de dados.
class DatabaseControl:
	
	# Base de dados das medições
	db_measure_path = ''
	
	# Diretorio do programa
	directory = ''
	
	# Construtor
	def __init__(self):
		self.directory = os.path.dirname(os.path.realpath(__file__))
		self.db_measure_path = '/database/measures.json'
		if(platform.system() != 'Linux'):
			self.db_measure_path = '\\database\\measures.json'
	
	# Cadastra nova medicao
	def insert_measure(self, data):
		
		# Atribuindo um novo ID para o paciente
		new_id = int(self.get_last_id(self.db_measure_path)) + 1
		time_measure = str(datetime.now())
		new_data = {'id': new_id, 'uuid': str(uuid.uuid4()), 'H': data['H'], 'T': data['T'], 'P': data['P'], 'L': data['T'], 'datetime': time_measure}
		
		# Pega todas as medicoes e adiciona a nova no final delas
		current_data = self.get_all(self.db_measure_path)
		current_data[str(new_id)] = new_data
		with open(self.directory + self.db_measure_path, 'w', encoding='utf-8') as db_write:
			json.dump(current_data, db_write, ensure_ascii=False, indent=4)
		return new_id
	
	# Retornar o último ID cadastrado para determinado arquivo.
	def get_last_id(self, db_file):
		last_id = -1 # Retorna -1 caso não tenha nada.
		with open(self.directory + db_file, 'r', encoding='utf-8') as db_read:
			data = json.load(db_read)
			for id in data:
				last_id = id
		return last_id
	
	# Retornar todos os dados de um determinado arquivo.
	def get_all(self, db_file):
		with open(self.directory + db_file, 'r', encoding='utf-8') as db_read:
			# print(json.load(db_read))
			return json.load(db_read)
		return None
	
	# Retornar um dado caso exista de um determinado arquivo, caso não retorna vazio.
	def get(self, db_file, id):
		with open(self.directory + db_file, 'r', encoding='utf-8') as db_read:
			data_read = json.load(db_read)
			for index in data_read:
				if(str(index) == str(id)):
					return data_read[str(id)]
		return None
	
	# Retorna as 10 últimas medições
	def get_last_qntd(self, count):
		measures = self.get_all(self.db_measure_path)
		qntd = len(measures)
		if(qntd <= count):
			return measures
		last_10 = []
		for measure in list(measures)[-count:]:
			last_10.append(measures[measure])
		return last_10
	
	# Retorna todos os pacientes de um determinado medico
	def get_all_measures(self):
		return self.get_all(self.db_measure_path)
	
	# Retorna um paciente de um determinado medico
	def get_measure(self, id_measure):
		return self.get(self.db_measure_path, id_measure)
	
	# Deleta uma medida por ID.
	def delete_measure(self, id_measure):
		path = self.directory + self.db_measure_path
		with open(path, 'r', encoding='utf-8') as db_read:
			data_read = json.load(db_read)
			data_read.pop(str(id_measure))
			with open(path, 'w', encoding='utf-8') as db_write:
				json.dump(data_read, db_write, ensure_ascii=False, indent=4)
			return True
		return False
		
if __name__ == '__main__':
	c = DatabaseControl()
	# c.insert_measure({"H": "100", "T": "100", "P": "100", "L": "100"})
	print(c.get_last_qntd(10))