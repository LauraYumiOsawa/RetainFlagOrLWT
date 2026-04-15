import argparse
import signal
import sys
import time
from datetime import datetime

import paho.mqtt.client as mqtt


def now() -> str:
    return datetime.now().strftime("%H:%M:%S")


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[{now()}] Conectado. reason_code={reason_code}")

    if userdata["mode"] == "monitor":
        topic = userdata["topic"]
        client.subscribe(topic, qos=1)
        print(f"[{now()}] Monitorando: {topic}")
    else:
        status_topic = userdata["topic"]
        client.publish(status_topic, payload="online", qos=1, retain=True)
        print(f"[{now()}] Publicado status inicial: online (retain=True)")


def on_message(client, userdata, msg):
    print(
        f"[{now()}] Mensagem recebida | topic={msg.topic} "
        f"| payload={msg.payload.decode(errors='replace')} "
        f"| retain={msg.retain}"
    )


def on_disconnect(client, userdata, reason_code, properties=None):
    print(f"[{now()}] Desconectado. reason_code={reason_code}")


def build_client(client_id: str, userdata: dict, keepalive: int) -> mqtt.Client:
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=client_id,
        userdata=userdata,
        clean_session=True,
    )
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    if userdata["mode"] == "device":
        client.will_set(
            userdata["topic"],
            payload="offline",
            qos=1,
            retain=True,
        )
        print(f"[{now()}] LWT configurado: topic={userdata['topic']} payload=offline")

    return client


def main():
    parser = argparse.ArgumentParser(description="Demonstração de MQTT LWT")
    parser.add_argument("--host", default="localhost", help="Broker MQTT")
    parser.add_argument("--port", type=int, default=1883, help="Porta do broker")
    parser.add_argument(
        "--topic",
        default="devices/device01/status",
        help="Tópico de status",
    )
    parser.add_argument(
        "--mode",
        choices=["device", "monitor"],
        required=True,
        help="device publica status e configura LWT; monitor apenas observa",
    )
    parser.add_argument("--client-id", default=None, help="Client ID MQTT")
    parser.add_argument("--keepalive", type=int, default=10, help="Keepalive MQTT")
    args = parser.parse_args()

    client_id = args.client_id or f"{args.mode}-client"
    userdata = {"mode": args.mode, "topic": args.topic}
    client = build_client(client_id, userdata, args.keepalive)

    def shutdown(*_):
        print(f"\n[{now()}] Encerrando de forma limpa...")
        if args.mode == "device":
            client.publish(args.topic, payload="offline-clean", qos=1, retain=True)
            print(f"[{now()}] Publicado status offline-clean antes de desconectar")
        client.disconnect()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f"[{now()}] Conectando em {args.host}:{args.port} ...")
    client.connect(args.host, args.port, keepalive=args.keepalive)
    client.loop_start()

    try:
        while True:
            if args.mode == "device":
                print(f"[{now()}] Device ativo. Mate o processo abruptamente para disparar o LWT.")
            time.sleep(5)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
