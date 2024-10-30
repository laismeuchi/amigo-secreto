import random
import pywhatkit
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def read_participants(file_path):
    return pd.read_excel(file_path)


def assign_secret_friends(participants):
    logging.info("Iniciando o Sorteio...")
    while True:
        drawn = participants[:]
        random.shuffle(drawn)
        if all(participants[i]['Telefone'] != drawn[i]['Telefone'] for i in range(len(participants))):
            return drawn
        logging.info("Tivemos pessoas tirando ela mesma.. refazendo o sorteio")


def send_messages(df_drawn):
    for index in df_drawn.index:
        participant_name = df_drawn['Participante'][index]
        participant_phone = "+55" + str(df_drawn['Telefone'][index])
        friend_name = df_drawn['Amigo Secreto'][index]
        friend_city = df_drawn['Amigo Secreto Cidade'][index]

        message = f"""Olá *{participant_name}*!
        Chegou o resultado do sorteio de *Amigo Secreto das Flores* 💐🌷🌿
        Seu amigo(a) secreto é
        .
        .
        .
        .
        .
        *{friend_name}* que mora em *{friend_city}*
        """
        logging.info(f"Enviando mensagem para {participant_phone}")
        pywhatkit.sendwhatmsg_instantly(participant_phone, message, wait_time=15, tab_close=True)


if __name__ == '__main__':
    logging.info("Iniciando script...")
    df_participants = read_participants('Amigo Secreto do Viveiro.xlsx')

    logging.info("Iniciando sorteio...")
    participants = df_participants.to_dict('records')
    drawn = assign_secret_friends(participants)
    logging.info("Sorteio realizado...")

    df_drawn = pd.DataFrame({
        'Participante': [p['Participante'] for p in participants],
        'Telefone': [p['Telefone'] for p in participants],
        'Cidade': [p['Cidade'] for p in participants],
        'Amigo Secreto': [d['Participante'] for d in drawn],
        'Amigo Secreto Telefone': [d['Telefone'] for d in drawn],
        'Amigo Secreto Cidade': [d['Cidade'] for d in drawn],
    })

    output_file = 'Amigo Secreto do Viveiro - Resultado.xlsx'
    df_drawn.to_excel(output_file, index=False)

    logging.info("Enviando mensagens...")
    send_messages(df_drawn)
    logging.info("Mensagens enviadas.")
