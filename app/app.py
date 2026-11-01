#!/usr/bin/env python3

import sys
import os
import logging
from datetime import datetime, timezone

from log import setup_logging
from help import config_help
from cliente import get_products, get_carts, save_produto, save_carts

logger = logging.getLogger('loja')

if __name__ == '__main__':

    # Sem ":" no nome, que o Windows não aceita, para funcionar em pasta compartilhada
    file_sufix = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

    json_path = '/home/doctor_dock/'
    logs_path = json_path

    if os.environ.get('PRODUCTION'):
        logs_path = '/data/logs'
        json_path = '/data/json'

    setup_logging(os.path.join(logs_path, "loja.log"))

    help = config_help()

    if (not help.produtos) and (not help.carts):
        logger.error("Precisa executar com --produtos ou --carts")
        sys.exit(1001)

    if help.produtos:
        logger.info("Baixando produtos")
        save_produto(os.path.join(json_path, "produtos_"+file_sufix+".json"))

    if help.carts:
        logger.info("Baixando carts")
        save_carts(os.path.join(json_path, "carts_"+file_sufix+".json"))