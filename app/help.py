import argparse

def config_help():
    parser = argparse.ArgumentParser(description="Programa para baixar dados de loja")

    parser.add_argument("--produtos", action="store_true", help="Salva produtos")
    parser.add_argument("--carts", action="store_true", help="Salva carts")

    return parser.parse_args()