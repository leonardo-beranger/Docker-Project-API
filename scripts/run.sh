#!/bin/sh

mkdir -p /data/logs
mkdir -p /data/json

export PRODUCTION=1
/home/doctor_dock/venv/bin/python /app/app.py --produtos --carts

# Mantém as 720 coletas mais recentes de cada tipo: 30 dias, com uma coleta por hora.
# Limita por quantidade, e não por idade, para uma API fora do ar não apagar o histórico.
# O horário no nome faz a ordem alfabética ser também a ordem cronológica.
for tipo in produtos carts; do
    ls -1r /data/json/"$tipo"_*.json 2>/dev/null | tail -n +721 | xargs -r rm -f --
done