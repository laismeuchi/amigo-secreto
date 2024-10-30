# Amigo Secreto

Projeto para sorteio de Amigo Secreto e envio dos resultados por WhatsApp.

## Demanda

Minha mãe tem um viveiro onde ela vende vários tipos de plantas, desde flores até árvores frutíferas.

Ao longo dos anos ela consegui clientes em várias cidades da região e a venda realizada para esses clientes é realizada por WhatsApp e depois, 1 vez por mês, meu pai vai até essas cidades fazer as entregas aos clientes.

Também existe um grupo de WhatsApp em que os clientes que participam podem acompanhar os produtos disponíveis, além de trocar experiência sobre cultivos e cuidados com suas plantas.

Com o tempo, os clientes passaram a se conhecer pelo grupo e interagir bastante, o que levou ela a ideia de esse ano fazer um amigo secreto entre os clientes que quiserem participar.
A ideia é fazer o sorteio entre os clientes e depois durante as entregas, os presentes seriam enviados aos participantes.

Então ela me pediu uma forma de fazer esse sorteio entre os clientes das várias cidades e enviar por WhatsApp o resultado de cada participante.
Deveria ser uma coisa bem simples pois a maioria dos cliente só sabem usar o WhatsApp.


## Solução

### Sorteio

O sorteio é realizado com base na planilha preenchida com Nome, Telefone e Cidade do Participante.

![Screenshot 2024-10-30 174740](https://github.com/user-attachments/assets/00ee603f-fc46-48d7-b18e-4aa036e0b56a)


A planilha é lida para um _dataframe_ do [Pandas](https://pandas.pydata.org/). É feita uma cópia desse _dataframe_ em que é aplicado a função _suffle_ da biblioteca [_random_](https://docs.python.org/3/library/random.html) que embralha a lista de participantes.
Também é realizada uma validação para ver se algum participante tirou ele mesmo e se esse for o caso, é realizado um novo sorteio até que não tenha esses casos.

``` python
def assign_secret_friends(participants):
    logging.info("Iniciando o Sorteio...")
    while True:
        drawn = participants[:]
        random.shuffle(drawn)
        if all(participants[i]['Telefone'] != drawn[i]['Telefone'] for i in range(len(participants))):
            return drawn
        logging.info("Tivemos pessoas tirando ela mesma.. refazendo o sorteio")
```

Este foi o exemplo de um resultado de sorteio:

![Screenshot 2024-10-30 190342](https://github.com/user-attachments/assets/dcd4b311-4aba-4848-bb8b-fcaf00071290)


Como o número de participantes é pequeno essa solução atende, mas em casos de muitos participantes essa seria uma parte do código a ser ajustada para melhor desempenho.

### Envio das mensagens 

Pensando na simplicidade, resolvi utilizar a opção de [Click to Chat](https://faq.whatsapp.com/5913398998672934/?helpref=uf_share) do WhatsApp em que é possível enviar uma mensagem para um número diretamente do navegador.
Foi então que encontrei a biblioteca [pywhatkit](https://pypi.org/project/pywhatkit/) que faz o encapsulamento de toda a parte de abrir o navegador e utilizar o *Click to Chat* e fechar a aba.

A função _sendwhatmsg_instantly_ faz o envio da mensagem instaneamente para o telefone indicado. O parâmetro _wait_time_ especifica o tempo em segundos que a mensagem será enviada após a abertura do navegador e o _tab_close=True_ fecha a aba depois que enviar a mensagem.

``` python
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
```

### Demonstração

Aqui deixo um vídeo de demonstração da execução do sorteio e envio de mensagens:


## *_Disclaimer_*

O WhatsApp possui uma série de restrições de envio de mensagens em grande escala principalmente utilizando contas pessoais. Fique atento a essas regras!
