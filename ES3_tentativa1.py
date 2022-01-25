#!/usr/bin/env python
# coding: utf-8

# # Dados obtidos em www.simcosta.furg.br

# In[2]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

data_path = os.getcwd() + '/dados' # precisa limpar o cabecalho desses arquivos


# In[3]:


def passa_data(data):
    return datetime.strptime(data, '%Y %m %d %H %M %S')


# In[4]:


def trata_dado(path):
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


# In[5]:


def teste_serie_temporal(df, delta_time = 24*7):
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


# In[7]:


def ajusta_dado(csv_path):
    dado = pd.read_csv(csv_path)
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


# In[ ]:


# botar isso mais pra cima

def aproveitamento(dataframe, variavel):

    total = dataframe.notnull().sum()[variavel]
    total_tempo = dataframe.notnull().sum()['EE']
    flag = dataframe.notnull().sum()['jump_flag']
    crisis = dataframe.notnull().sum()['jump_crisis']
    perc_flag = round(flag*100/total, 2)
    perc_crisis = round(crisis*100/total, 2)
    perc_datas = round(total*100/total_tempo, 2)

    print("De %s valores, %s foram marcados com a flag de pulo (%s%s).\n%s valores foram marcados com a flag de crise (%s%s)."
          % (str(total), str(flag),str(perc_flag), '%', str(crisis), str(perc_crisis), "%"))


# In[8]:


# limiar de HS eh de 20m
# res HS = 0.01 -> acho que vou aproximar pra uma casa decimal so, fica mais facil de cortar dados espurios
# e talvez fique melhor discretizado

# se ficar mais de um dia sem dado, eu caracterizo como um GAP e "recorto" a serie temporal
# 24h - 1 ponto por h - 24 pontos

# WMO define um desvpad de 4* a media, entao vou usar esse cara aqui tbm
dado = pd.read_csv(data_path + '/' + os.listdir(data_path)[0])

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


# In[9]:


media = dado.mean()
desvpad = dado.std()
evento_extremo = media + 4*desvpad


# In[10]:


evento_extremo_line = np.zeros(42881) # como eu cheguei nesse valor?
for i in range(len(evento_extremo_line)):
        evento_extremo_line[i] = evento_extremo


# In[10]:


dado['EE'] = evento_extremo_line


# In[11]:


############################################################


# In[12]:


dados_nan = dado.isnull().where(dado['Hsig'].isnull() == True).dropna() # me da um DF com as datas de nan


# In[13]:


col_jump_flag = np.empty(len(dado['Hsig']))
col_jump_flag[:] = np.nan


for i in range(len(dado['Hsig'])):
    if dado['Hsig'][i] >= evento_extremo[0] and abs(dado['Hsig'][i-1] - dado['Hsig'][i]) > desvpad['Hsig']: # a diferenca do valor extremo eh um desvpad
        col_jump_flag[i] = dado['Hsig'][i]
        #print(i)
        
dado['jump_flag'] = col_jump_flag


# In[14]:


col_jump_flag = np.empty(len(dado['Hsig']))
col_jump_flag[:] = np.nan


for i in range(len(dado['Hsig'])):
    if dado['Hsig'][i] >= 0 and abs(dado['Hsig'][i-1] - dado['Hsig'][i]) > desvpad['Hsig']: # a diferenca do valor extremo eh um desvpad
        col_jump_flag[i] = dado['Hsig'][i]
        #print(i)
        
dado['jump_flag'] = col_jump_flag


# In[15]:


# se for salto de 2 sigma, eh dado em crise

col_jump_crisis = np.empty(len(dado['Hsig']))
col_jump_crisis[:] = np.nan


for i in range(len(dado['Hsig'])):
    if dado['Hsig'][i] >= 0 and abs(dado['Hsig'][i-1] - dado['Hsig'][i]) > 2*desvpad['Hsig']: # a diferenca do valor extremo eh um desvpad
        col_jump_crisis[i] = dado['Hsig'][i]
        #print(i)
        
dado['jump_crisis'] = col_jump_crisis


# In[20]:


dado.notnull().sum()[:]


# In[89]:


aproveitamento(dado, 'Hsig')


# In[14]:


##########################################################


# In[11]:


teste_serie_temporal(dado)


# In[48]:


teste_serie_temporal(dado,1) # considerando o espaco de 1h, que seria a manutencao, tem um valor mto grande de 
################################## falhas na serie temporal


# In[49]:


serie1 = dado[:datetime(2017,8,25,23,55,0)]


# In[50]:


serie2 = dado[datetime(2018,1,30,6,25):datetime(2018,9,2,21,23)]


# In[52]:


serie3 = dado[datetime(2018,10,24,11,23): datetime(2019,9,12,10,53)]


# In[53]:


serie4 = dado[datetime(2020,12,17,21,51,40):]


# In[56]:


import matplotlib.dates as mdates

fig = plt.figure(figsize=(24,12))

ax = fig.add_subplot(111)
ax.plot(serie1['Hsig'][:], marker = 'o', color = 'green', linestyle = 'none')
ax.plot(serie2['Hsig'][:], marker = 'o', color = 'red', linestyle = 'none')
ax.plot(serie3['Hsig'][:], marker = 'o', color = 'yellow', linestyle = 'none')
ax.plot(serie4['Hsig'][:], marker = 'o', color = 'purple', linestyle = 'none')


# ax.plot(dado['EE'][:], marker = '.', color = 'blue', linestyle = 'none')
#ax.plot(dado['jump_flag'][:], marker = 'o', color = 'yellow', linestyle = 'none')
#ax.plot(dado['jump_crisis'][:], marker = 'o', color = 'red', linestyle = 'none')

#plt.axhline(y=2.980402, color='blue', linestyle='-') # limite de evento extremo

ax.grid()
ax.set_ylabel('Hs (m)', fontsize = 20)

################################# data #######################

# Major ticks every 6 months.
fmt_half_year = mdates.MonthLocator(interval=6)
ax.xaxis.set_major_locator(fmt_half_year)

# Minor ticks every month.
fmt_month = mdates.MonthLocator()
ax.xaxis.set_minor_locator(fmt_month)

# Text in the x axis will be displayed in 'YYYY-mm' format.
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))


ax.tick_params(axis='both', which='major', labelsize=20, size=10)
ax.tick_params(axis='both', which='minor', size=5)

ax.set_xlim(datetime(2016,5,1), datetime(2021,10,1))



###########################################################################

plt.title('Dados suspeitos marcados', fontsize = 40)


# In[58]:


import matplotlib.dates as mdates

fig = plt.figure(figsize=(24,12))

ax = fig.add_subplot(111)
ax.plot(dado['Hsig'][:], marker = 'o', color = 'purple', linestyle = 'none')


# ax.plot(dado['EE'][:], marker = '.', color = 'blue', linestyle = 'none')
#ax.plot(dado['jump_flag'][:], marker = 'o', color = 'yellow', linestyle = 'none')
#ax.plot(dado['jump_crisis'][:], marker = 'o', color = 'red', linestyle = 'none')

#plt.axhline(y=2.980402, color='blue', linestyle='-') # limite de evento extremo

ax.grid()
ax.set_ylabel('Hs (m)', fontsize = 20)

################################# data #######################

# Major ticks every 6 months.
fmt_half_year = mdates.MonthLocator(interval=6)
ax.xaxis.set_major_locator(fmt_half_year)

# Minor ticks every month.
fmt_month = mdates.MonthLocator()
ax.xaxis.set_minor_locator(fmt_month)

# Text in the x axis will be displayed in 'YYYY-mm' format.
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))


ax.tick_params(axis='both', which='major', labelsize=20, size=10)
ax.tick_params(axis='both', which='minor', size=5)

ax.set_xlim(datetime(2016,5,1), datetime(2021,10,1))



###########################################################################

plt.title('Dados suspeitos marcados', fontsize = 40)


# In[16]:


# fazer histograma com essas alturas


# In[17]:


fig = plt.figure(figsize=(24,12))
plt.title('Histograma das ondas', fontsize=16)
ax = fig.add_subplot(111)
bins=np.arange(0.5, 5, 0.5)
counts, brings, patches = ax.hist(dado['Hsig'], bins= bins, facecolor='yellow', edgecolor='grey', label = 'Hs(m)')
ax.set_xticks(bins)
bin_centers=np.diff(bins) + bins[:-1] - 0.25
for count, x in zip(counts, bin_centers):
    percent = '%0.1f%%' % (100*float(count) / counts.sum())
    ax.annotate(percent, xy= (x,0), weight = 'bold', xycoords=('data', 'axes fraction'),xytext= (0,15),
                textcoords='offset points', va = 'top', ha='center', fontsize=18, color = 'red')
ax.legend(loc="upper right", fontsize=18)
plt.grid()


# In[18]:


dado['Hsig'].kurtosis() # distribuicao que nao for gaussiana


# In[19]:


dado['Hsig'].skew() # tende a cair mais pro lado direito do que pro lado esquerdo na media


# In[ ]:




