import argparse
import sys
import time
from datetime import datetime

import paho.mqtt.client as mqtt


def now() -> str:
    return datetime.now().strftime("%H:%M:%S")


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[{now()}] Conectado. reason_code={reason_code}")
    if userdata["mode"] == "subscribe":
        client.subscribe(userdata["topic"], qos=1)
        print(f"[{now()}] Assinado em: {userdata['topic']}")


def on_message(client, userdata, msg):
    print(
        f"[{now()}] Recebido | topic={msg.topic} "
        f"| payload={msg.payload.decode(errors='replace')} "
        f"| retain={msg.retain}"
    )


def main():
    parser = argparse.ArgumentParser(description="Demonstração de MQTT Retain Flag")
    parser.add_argument("--host", default="localhost", help="Broker MQTT")
    parser.add_argument("--port", type=int, default=1883, help="Porta do broker")
    parser.add_argument("--topic", default="devices/device01/state", help="Tópico MQTT")
    parser.add_argument(
        "--mode",
        choices=["publish", "subscribe", "clear"],
        required=True,
        help="publish envia valor com retain; subscribe observa; clear remove retain",
    )
    parser.add_argument("--value", default="ligado", help="Valor para publish")
    args = parser.parse_args()

    userdata = {"mode": args.mode, "topic": args.topic}
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=userdata)
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[{now()}] Conectando em {args.host}:{args.port} ...")
    client.connect(args.host, args.port, keepalive=10)

    if args.mode == "publish":
        client.loop_start()
        time.sleep(1)
        info = client.publish(args.topic, payload=args.value, qos=1, retain=True)
        info.wait_for_publish()
        print(
            f"[{now()}] Publicado com retain=True | topic={args.topic} | payload={args.value}"
        )
        client.disconnect()
        client.loop_stop()
        return

    if args.mode == "clear":
        client.loop_start()
        time.sleep(1)
        info = client.publish(args.topic, payload="", qos=1, retain=True)
        info.wait_for_publish()
        print(f"[{now()}] Mensagem retida removida do tópico: {args.topic}")
        client.disconnect()
        client.loop_stop()
        return

    if args.mode == "subscribe":
        client.loop_start()
        print(f"[{now()}] Aguardando mensagens. Se existir retain, ela chega imediatamente.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n[{now()}] Encerrando subscriber...")
            client.disconnect()
            client.loop_stop()
            sys.exit(0)


if __name__ == "__main__":
    main()
