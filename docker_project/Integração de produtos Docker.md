# Descrição do projeto

Integrar informações obtidas de uma API do DummyJson utilizando um container docker e disponibilizar as informações para uso de análises.

**Ferramentas:** Python + Docker + VsCode

**Extensão VsCode:** 
- Python
- Dev Container
- Container Tools

**API da DummyJson:** 
- Get all products: 'https://dummyjson.com/products'
- Get all carts: 'https://dummyjson.com/carts'

**Etapas:**
- 1ª Qual base imagem docker será base do projeto? 
	- Python: https://hub.docker.com/_/python - 3.15.0-bookworm
- 2ª No diretório principal:
|----docker_project
|--|___ .devcontainer
    |___ devcontainer.json
|--|___ app
    |___ app.py
|--|___ docker_project (cofre obsedian)
|--|___ scripts
|--|___ Dockerfile (multistage - pesquisar na internet)

---

# Estado atual (31/10/2026)

**Repositório:** https://github.com/leonardo-beranger/Docker-Project-API

O GitHub não aceita espaços no nome, por isso "Docker Project API" virou `Docker-Project-API`.

## Estrutura real

```text
docker_project/
├── app/
│   ├── app.py          # ponto de entrada; lê os argumentos e define os caminhos
│   ├── cliente.py      # chama a API do DummyJSON e grava os JSON
│   ├── help.py         # argumentos --produtos e --carts
│   └── log.py          # log em stderr e em arquivo rotativo
├── docker_project/     # este cofre do Obsidian
├── scripts/
│   ├── entrypoint.sh   # inicia o cron e acompanha o log
│   ├── mycrontab       # agendamento: a cada minuto
│   └── run.sh          # cria as pastas e executa o app.py
├── Dockerfile
└── requirements.txt
```

A pasta `.devcontainer` citada nas etapas acima não existe no projeto, embora o Dockerfile faça referência ao `devcontainer.json`.

## Estágios do Dockerfile

| Estágio | Herda de | Para que serve |
|---|---|---|
| `build` | `python:3.15.0-bookworm` | Base comum: instala o cron e cria o usuário `doctor_dock` |
| `development` | `build` | Cria o venv e o ativa no bash; o código vem do devcontainer |
| `production` | `build` | Copia código e scripts, instala as dependências e define o `ENTRYPOINT` |

O estágio `development` não entra na imagem de produção, porque os dois herdam de `build` de forma independente.

## Fluxo em produção

1. O `ENTRYPOINT` executa `entrypoint.sh` como root, já que o daemon do cron precisa disso.
2. O cron lê `/etc/cron.d/mycrontab` e dispara `run.sh` a cada minuto.
3. `run.sh` define `PRODUCTION=1` e executa `app.py --produtos --carts` com o Python do venv.
4. `app.py` baixa os produtos e os carrinhos e grava um JSON para cada um, com o horário UTC no nome.
5. Os logs vão para `/data/logs/loja.log`, com rotação em 10 KB e 3 backups.

## Comandos

```bash
docker build --target production -t docker-project-api .
docker run -d --name docker-project-api -v docker_project_data:/data docker-project-api
docker logs -f docker-project-api
```

Para disparar uma coleta manual, sem esperar o cron:

```bash
docker exec -u doctor_dock docker-project-api /app/run.sh
```

## Problemas encontrados na revisão

Foram encontrados lendo o código. O build e a execução ainda não foram testados, porque o Docker estava desligado.

- [ ] `scripts/mycrontab`: o usuário está como `docker_doc`, mas o criado no Dockerfile é `doctor_dock`. O job agendado não roda.
- [ ] `scripts/entrypoint.sh`: acompanha `/data/logs/loj.log`, mas o arquivo gerado é `loja.log`. Os logs não aparecem no `docker logs`.
- [ ] `scripts/run.sh`: usa `mkdir ~p` em vez de `mkdir -p`. Cria uma pasta chamada `~p` e dá erro quando as pastas já existem.
- [ ] `app/app.py`: em produção, os JSON vão para `/home/doctor_dock/`, e não para `/data/json`. Eles ficam fora do volume e se perdem junto com o container.
- [ ] `app/cliente.py`: se a requisição falhar, `result` fica indefinido e o programa quebra com `UnboundLocalError`.
- [ ] `app/cliente.py`: `can_write` retorna `None` em `IOError`, sem o `return False`.
- [ ] `app/cliente.py`: a API do DummyJSON devolve 30 itens por padrão, então "get all" não traz tudo sem `limit` e `skip`.
- [ ] `scripts/mycrontab`: em build feito no Windows, o arquivo pode chegar com modo `0755`, que o cron do Debian costuma rejeitar. Vale um `chmod 0644` no Dockerfile, a confirmar no teste.
- [ ] Criar a pasta `.devcontainer` com o `devcontainer.json`.

## Próximos passos

- Corrigir a lista acima e testar o build de ponta a ponta.
- Definir como as análises vão consumir os JSON do volume `/data`.
