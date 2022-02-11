import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta


def passa_data(data):
	'''
	Adequa o formato de data para ser utilizado no dataframe 
	'''
	return datetime.strptime(data, '%Y %m %d %H %M %S')


def trata_dado(path):
	'''
	Gera um dataframe a partir dos dados ja no formato adequado, o argumento que ele utiliza e o caminho para os dados
	'''

	dado = pd.read_csv(path)
    
	Ano = dado['YEAR'].apply(str)
	Mes = dado['MONTH'].apply(str)
	Dia = dado['DAY'].apply(str)
	Hora = dado['HOUR'].apply(str)
	Minuto = dado['MINUTE'].apply(str)
	Segundo = dado['SECOND'].apply(str)
	dado['DATA'] = (Ano + ' ' + Mes + ' ' + Dia + ' ' + Hora + ' ' + Minuto + ' ' + Segundo).apply(passa_data)
	dado = dado.set_index('DATA')
	del(dado['YEAR'])
	del(dado['MONTH'])
	del(dado['DAY'])
	del(dado['HOUR'])
	del(dado['MINUTE'])
	del(dado['SECOND'])
    
	return dado


def teste_serie_temporal(df, delta_time = 24*7):
	'''
	Realiza um teste para verificar se existem buracos na serie temporal, a variacao do tempo default eh dada como uma semana
	'''
	counter = 0
	falhas = []
	for i in range(len(df.index)):
		if df.index[i] > df.index[i-1] + timedelta(hours=delta_time):
			falhas.append((df.index[i-1], df.index[i]))
#             print('Inicio da falha temporal: ' + str(df.index[i-1]))
#             print('Fim da falha na serie temporal ' + str(df.index[i]))
		counter += 1
	print('Foram encontradas ' + str(counter) +' falhas na serie temporal.')
	return falhas


def aproveitamento(dataframe, variavel):
	'''
	verifica a quantidade de dados marcados com as flags de pulo
	'''

	total = dataframe.notnull().sum()[variavel]
	total_tempo = dataframe.notnull().sum()['EE_'+variavel]
	flag = dataframe.notnull().sum()['jump_flag']
	crisis = dataframe.notnull().sum()['jump_crisis']
	perc_flag = round(flag*100/total, 2)
	perc_crisis = round(crisis*100/total, 2)
	perc_datas = round(total*100/total_tempo, 2)

	print("De %s valores, %s foram marcados com a flag de pulo (%s%s).\n%s valores foram marcados com a flag de crise (%s%s)."
	% (str(total), str(flag),str(perc_flag), '%', str(crisis), str(perc_crisis), "%"))
          
    
    
def jump_flag(dataframe, variavel ,desvpad):
	'''
	verifica se existem variacoes de um desvio padrao de uma medicao para a outra
	'''

	col_jump_flag = np.empty(len(dataframe[variavel]))
	col_jump_flag[:] = np.nan

	for i in range(len(dataframe[variavel])):
		if abs(dataframe[variavel][i-1] - dataframe[variavel][i]) > desvpad[variavel]: # a diferenca do valor extremo eh um desvpad
			col_jump_flag[i] = dataframe[variavel][i]
        #print(i)
        
	dataframe['jump_flag'] = col_jump_flag
    
    
def jump_crisis(dataframe, variavel ,desvpad, n=2):
	'''
	verifica se existem variacoes de n desvios padroes de uma medicao para a outra
	'''

	col_jump_crisis = np.empty(len(dataframe[variavel]))
	col_jump_crisis[:] = np.nan


	for i in range(len(dataframe[variavel])):
		if abs(dataframe[variavel][i-1] - dataframe[variavel][i]) > n*desvpad[variavel]: # a diferenca do valor extremo sao n desvpad
			col_jump_crisis[i] = dataframe[variavel][i]
        
	dataframe['jump_crisis'] = col_jump_crisis
    
    
def evento_extremo(dataframe, variavel = 'Hsig', jf = True, jc = True):
	'''
	define um valor de evento extremo, considerando a serie temporal toda, automaticamente gera as jump flags, caso nao explicitado para deixar de faze-lo
	'''
	media = dataframe.mean()
	desvpad = dataframe.std()
	evento_extremo = media + 4*desvpad
    
	evento_extremo_line = np.zeros(len(dataframe))
	for i in range(len(evento_extremo_line)):
		evento_extremo_line[i] = evento_extremo[variavel]
    
		dataframe['EE_' + variavel] = evento_extremo_line
    
	if jf:
		jump_flag(dataframe, variavel, desvpad)
	if jc:
		jump_crisis(dataframe, variavel, desvpad)
        
        
        
def recorta_serie_temporal(datas, dataframe):
	'''
	dado uma lista de datas em tuplas, recorta o dataframe nessas datas. 
	eh necessario fornecer uma data de inicio e uma data de fim para o corte que estejam 		dentro dos dados medidos.
	'''
	dfs = [] # lista pra appendar todos os dataframes
	for i in range(len(datas)):
		if i == 0:
			serie = dataframe[:datas[0][0]]
		elif i == len(datas)-1:
 			serie_extra = dataframe[datas[i-1][1]:datas[i][0]]
 			serie = dataframe[datas[i][1]:]
 			dfs.append(serie_extra)
		else: 
			serie = dataframe[datas[i-1][1]:datas[i][0]]
		dfs.append(serie)
	return(dfs)
    
    
def dado_repetido(df, variavel, n):
	'''
	checa se existem n dados repetidos na serie temporal
	'''
	counter = 0
	ini = False
	retorno = []
	for i in range(len(df[variavel])):
		if df[variavel][i-1] == df[variavel][i]:
			counter += 1
			if not ini:
				ini = i
		else:
			if counter == n:
				retorno.append((df.index[ini], df.index[i]))
				ini = False
				counter = 0
            
	return retorno 
