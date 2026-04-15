# MQTT - LWT e Retain Flag

## Objetivo
Compreender e demonstrar, na prática, o funcionamento do **Last Will and Testament (LWT)** e do **Retain Flag** no protocolo MQTT, destacando principalmente **quando usar cada um** e **os impactos em sistemas IoT reais**.

---

## 1. Quando usar **LWT**

O **Last Will and Testament (LWT)** é usado quando você precisa que o broker publique automaticamente uma mensagem caso um cliente MQTT se desconecte de forma inesperada.
Use **LWT** para representar **estado de presença/saúde do cliente**, não para guardar configuração ou último valor de sensor.
### Exemplo:
- Um gateway IoT publica `status/gateway01 = online` quando conecta e configura no broker um LWT: 'tópico: `status/gateway01`' e 'payload: `offline`'
	-  Nesse caso, se o gateway cair por falta de energia, travamento ou perda abrupta de rede, o broker publica `offline` automaticamente.

### Impactos do LWT em um sistema IoT real
**Impactos positivos:**
- detecção rápida de falha;
- melhora o monitoramento operacional;
- facilita alarmes, dashboards e manutenção;
- ajuda automações dependentes do estado do dispositivo.

**Impactos negativos:**
- LWT não substitui telemetria nem heartbeat bem definido;
- se o `keepalive` for muito alto, a detecção de queda demora;
- se estiver mal modelado, pode gerar falso entendimento de indisponibilidade temporária de rede;
- exige definição clara de tópicos de status.

---

## 2. Quando usar **Retain Flag**

O **Retain Flag** faz o broker guardar a **última mensagem** publicada em um tópico e entregá-la imediatamente a novos assinantes.
Use **Retain** para representar **último estado válido conhecido**, não eventos transitórios.
### Exemplo real
Um dispositivo publica: 'tópico: `casa/sala/lampada/status`' e 'payload: `ligada`' com '`retain = true`'
- Nesse caso, qualquer cliente que assinar esse tópico depois recebe `ligada` imediatamente, mesmo que a publicação tenha ocorrido antes.

### Impactos do Retain em um sistema IoT real
**Impactos positivos:**
- novos consumidores recebem estado instantaneamente;
- reduz tempo de sincronização;
- simplifica inicialização de painéis e supervisórios;
- evita esperar um novo ciclo de publicação para saber o estado atual.

**Impactos negativos:**
- retain pode entregar valor antigo se ninguém atualizar o tópico;
- não é histórico, apenas a última mensagem;
- usar retain em tópicos errados pode causar confusão operacional;
- em tópicos de evento, geralmente **não** faz sentido reter.

---

## 3. Diferença entre LWT e Retain


### Resumo direto

### LWT
**LWT** é essencial para monitoramento de disponibilidade e reação a falhas. Basicamente avisa que algo caiu. 
- dispara em caso de **desconexão inesperada**;
- comunica falha/ausência do cliente;
- é uma ação do broker baseada na conexão.

### Retain
**Retain** é essencial para sincronização rápida de estado entre produtores e consumidores. Basicamente guarda o último estado.
- guarda a **última mensagem** do tópico;
- entrega esse valor para novos assinantes;
- é uma característica da mensagem publicada.


Usados corretamente, os dois melhoram observabilidade, robustez e previsibilidade do sistema MQTT.

---

## 5. Exemplo de arquitetura real

Um dispositivo pode usar:

- `devices/device01/status`  
  - `online` ao conectar  
  - `offline` via LWT ao cair  
  - publicado com retain para que novos clientes saibam o status atual

- `devices/device01/temperature`  
  - último valor de temperatura  
  - publicado com retain

Assim:
- o sistema sabe se o dispositivo está ativo;
- e também sabe o último valor conhecido.

---

## 6. Códigos de demonstração

Os arquivos incluídos nesta entrega são:

- `requirements.txt`
- `lwt.py`
- `retain.py`

### Instalação
```bash
# Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 7. Como testar
### LWT
#### Terminal 1
```bash
python lwt.py --mode monitor
```

#### Terminal 2
```bash
python lwt.py --mode device
```

O modo `device`:
- conecta ao broker;
- publica `online`;
- registra um LWT com payload `offline`;
- fica rodando até ser encerrado abruptamente.

Para demonstrar o LWT:
- feche o processo à força;
- ou mate o terminal do processo;
- ou derrube a conexão.

O monitor verá a mensagem `offline` publicada pelo broker.

### Retain

#### Publicar estado retido
```bash
python retain.py --mode publish --value ligado
```

#### Assinar o tópico
```bash
python retain.py --mode subscribe
```

Mesmo que o subscriber conecte depois, ele recebe imediatamente o último valor retido.
#### Limpar mensagem retida
```bash
python retain.py --mode clear
```
