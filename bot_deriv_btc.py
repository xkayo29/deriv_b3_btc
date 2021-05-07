# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import MetaTrader5 as mt5  # pip install MetaTrader5
import pandas as pd
import numpy as np
import telebot  # pip install pyTelegramBotAPI
from datetime import datetime, time
import time as tm


# %%
# Função para inicializar o MT5 e efetuar login
def login(login, password, servidor):
    mt5.initialize()
    lg = mt5.login(login, password, servidor)
    if lg:
        print(f'Conectado com sucesso...')
    else:
        print(f'Erro na conexção com a conta, erro = {mt5.last_error()}')
        mt5.shutdown()


# %%
# Função que verica a oportunidade de entra apos cruzamento das medias para troca de tendencia e enviar mensagem para o telegram
def cruzamento(tendencia):
    if tendencia[-5] == 'Alta' and tendencia[-2] == 'Baixa':
        return 'Vendido'
    elif tendencia[-5] == 'Baixa' and tendencia[-2] == 'Alta':
        return 'Comprado'
    else:
        return False


# %%
# Função para pegar hora atual do computador e comprar com horario de negociação
def iniciar():
    # Transforma a hora atual do pc em string
    atual = datetime.now().time().strftime('%H:%M:%S')
    # Transforma a string em objeto de datetime para fazer comparação
    atual = datetime.strptime(atual, '%H:%M:%S').time()
    # Cria as variaveis de horario do inicio e fim de funcionamento do mercado
    inicio, fim = time(0, 0, 0), time(23, 59, 59)

    if atual > inicio and atual < fim:
        return True
    else:
        return False


# %%
# Variaveis para o bot do telgram
# '1608254599:AAHK6CdSPPqDIFTLemsZXMtogGO4B8pkCic'
token = '1576500645:AAG3FBifGkzsutPixGbrxnVSPMV9RaqPDUI'
chat_id = '-1001108876977'  # 955453236
# Função para bot do telegram


def bot_telegram(msg, token, chat_id):
    tb = telebot.TeleBot(token)
    tb.send_message(chat_id, msg)
    return f'Mensagem enviada'


# %%
# Chama a função de login
login(1570672, '90576edkF', 'Deriv-Server')


# %%
# Lista de ativos para o laço for
papeis = ['EURUSD', 'USDJPY', 'EURJPY', 'BCHUSD', 'BNBUSD', 'BTCETH', 'BTCLTC', 'BTCUSD', 'DSHUSD', 'EOSUSD', 'ETHUSD',
          'IOTUSD', 'LTCUSD', 'NEOUSD', 'OMGUSD', 'TRXUSD', 'XLMUSD', 'XMRUSD', 'XRPUSD', 'ZECUSD']

# Ativando para envia apenas uma notificação
id_s = []

# %%
while True:

    while iniciar():  # Verifica se a funcao do horario retorna true para iniciar as analise

        # Laço para pecorrer todos os papeis
        for papel in papeis:

            # Baixa os dados do papel
            rates = mt5.copy_rates_from_pos(papel, mt5.TIMEFRAME_M5, 0, 300)

            # Transforma os dados em um dataframe
            df_rates = pd.DataFrame(rates)

            # Converte o time de segundos para data e tempo
            df_rates['time'] = pd.to_datetime(df_rates['time'], unit='s')


# %%
            # Renomea as colunas existente
            df_rates.rename(columns={'time': 'Data', 'open': 'Abertura', 'high': 'Alta', 'low': 'Baixa',
                                     'close': 'Fechamento', 'tick_volume': 'T_volume', 'spread': 'Spread', 'real_volume': 'Volume'}, inplace=True)

            # Transforma a Data em index
            df_rates.set_index('Data', inplace=True)


# %%
            # Criando medias
            df_rates['Lenta'] = df_rates['Fechamento'].rolling(200).mean()
            df_rates['Rapida'] = df_rates['Fechamento'].rolling(100).mean()

            # Limpando dados NaN
            df_rates.dropna(inplace=True)


# %%
            # Criando a condição de tendencia para nova coluna
            condicao = [
                (df_rates['Lenta'] > df_rates['Rapida']),
                (df_rates['Lenta'] < df_rates['Rapida']),
                (df_rates['Lenta'] == df_rates['Rapida'])
            ]
            valor = [
                'Baixa', 'Alta', 'Centralizado'
            ]

            # Criando a coluna de tendecia
            df_rates['Tendencia'] = np.select(condicao, valor)


# %%
            # Iniciando a função da busca por entrada

            if cruzamento(df_rates['Tendencia']) == 'Vendido':
                if papel not in id_s:
                    try:
                        msg = f'{papel} - Entrar vendindo | Preço: {df_rates["Fechamento"].tail(1).values}'
                        bot_telegram(msg, token=token, chat_id=chat_id)
                        id_s.append(papel)
                        print(
                            f'\n*****{papel}*****\n{df_rates.tail(1)}')
                    except:
                        pass
                        # print(
                        # f'Erro ao envia via telegram\n{papel} - Entrar vendindo | #Preço: {df_rates["Fechamento"].tail(1).values}')
                else:
                    pass
            elif cruzamento(df_rates['Tendencia']) == 'Comprado':
                if papel not in id_s:
                    try:
                        msg = f'{papel} - Entrar comprado | Preço: {df_rates["Fechamento"].tail(1).values}'
                        bot_telegram(msg, token=token, chat_id=chat_id)
                        id_s.append(papel)
                        print(
                            f'\n*****{papel}*****\n{df_rates.tail(1)}')
                    except:
                        pass
                        # print(
                        # f'Erro ao envia via telegram\n{papel} - Entrar comprado | #Preço: {df_rates["Fechamento"].tail(1).values}')
                else:
                    pass
            else:
                if papel in id_s:
                    id_s.remove(papel)
            # print(
                # f'\n*****{papel}*****\n{df_rates["Fechamento"].tail(1).values}')
            # tm.sleep(1)

# %%
    else:
        print(f'Fora do horario de negociação')
        break
