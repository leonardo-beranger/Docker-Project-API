import requests
import logging

BASE_URL = 'https://dummyjson.com/'

logger = logging.getLogger('loja')

def get_products():

    try:
        result = requests.get(BASE_URL+"products")
    except requests.exceptions.RequestException as e:
        logger.error(f"Falhou em get products: {e}")

    if result.status_code != 200:
        logger.error(f'Não baixou - status_code: {result.status_code}')
        return None

    return result.text

def get_carts():

    try:
        result = requests.get(BASE_URL+"carts")
    except requests.exceptions.RequestException as e:
        logger.error(f"Falhou em get carts: {e}")

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
