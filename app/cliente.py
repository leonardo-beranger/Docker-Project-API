import requests
import logging

BASE_URL = 'https://dummyjson.com/'

logger = logging.getLogger('loja')

def get_products():

    try:
        # limit=0 faz a API devolver todos os itens, e não só os 30 do padrão
        result = requests.get(BASE_URL+"products?limit=0")
    except requests.exceptions.RequestException as e:
        logger.error(f"Falhou em get products: {e}")
        return None

    if result.status_code != 200:
        logger.error(f'Não baixou - status_code: {result.status_code}')
        return None

    return result.text

def get_carts():

    try:
        # limit=0 faz a API devolver todos os itens, e não só os 30 do padrão
        result = requests.get(BASE_URL+"carts?limit=0")
    except requests.exceptions.RequestException as e:
        logger.error(f"Falhou em get carts: {e}")
        return None

    if result.status_code != 200:
        logger.error(f'Não baixou - status_code: {result.status_code}')
        return None

    return result.text

def can_write(file_path):
    
    try:
        with open(file_path, 'w') as f:
            pass
        return True
    except IOError as e:
        logger.error(f"Erro de entrada e saída: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return False
    

def save_produto(file_path):

    if data := get_products():
        if can_write(file_path):
            with open(file_path, 'w') as f:
                f.write(data)
            logger.info(f"Produtos salvos em: {file_path}")

def save_carts(file_path):

    if data := get_carts():
        if can_write(file_path):
            with open(file_path, 'w') as f:
                f.write(data)
            logger.info(f"Carts salvos em: {file_path}")
