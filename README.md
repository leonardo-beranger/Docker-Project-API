# Docker Project API

Coleta dados de produtos e carrinhos da [API do DummyJSON](https://dummyjson.com/) em um container Docker agendado com cron, e grava o resultado em JSON para uso em análises.

O projeto consome uma API externa. Ele não expõe nenhum endpoint próprio.

## Tecnologias

- Python 3.15 e `requests`
- Docker com build multi-stage
- cron
- VS Code com as extensões Python, Dev Containers e Container Tools

## Estrutura

```text
.
├── app/
│   ├── app.py          # ponto de entrada; lê os argumentos e define os caminhos
│   ├── cliente.py      # chama a API do DummyJSON e grava os JSON
│   ├── help.py         # argumentos --produtos e --carts
│   └── log.py          # log em stderr e em arquivo rotativo
├── docker_project/     # cofre do Obsidian com as notas do projeto
├── scripts/
│   ├── entrypoint.sh   # inicia o cron e acompanha o log
│   ├── mycrontab       # agendamento: a cada minuto
│   └── run.sh          # cria as pastas e executa o app.py
├── Dockerfile
└── requirements.txt
```

## Imagem Docker

| Estágio | Herda de | Para que serve |
|---|---|---|
| `build` | `python:3.15.0-bookworm` | Base comum: instala o cron e cria o usuário `doctor_dock` |
| `development` | `build` | Cria o venv e o ativa no bash; o código vem do devcontainer |
| `production` | `build` | Copia código e scripts, instala as dependências e define o `ENTRYPOINT` |

## Como usar

Gere a imagem de produção:

```bash
docker build --target production -t docker-project-api .
```

Inicie o container com um volume para `/data`:

```bash
docker run -d --name docker-project-api -v docker_project_data:/data docker-project-api
```

O cron executa a coleta a cada minuto. Para disparar uma coleta manual:

```bash
docker exec -u doctor_dock docker-project-api /app/run.sh
```

Acompanhe o log:

```bash
docker logs -f docker-project-api
```

Liste os arquivos gerados, que ficam em `/data/json`:

```bash
docker exec docker-project-api ls /data/json
```

### Argumentos do `app.py`

| Argumento | Efeito |
|---|---|
| `--produtos` | Baixa e salva os produtos |
| `--carts` | Baixa e salva os carrinhos |

É preciso informar pelo menos um. Cada arquivo recebe o horário UTC no nome, como `produtos_<timestamp>.json`.

### Variáveis de ambiente

| Variável | Efeito |
|---|---|
| `PRODUCTION` | Quando definida, grava em `/data/logs` e `/data/json` e usa o nível `INFO` em vez de `DEBUG`. O `run.sh` já a define. |

## Problemas conhecidos

- A imagem e o agendamento pelo cron ainda não foram testados em um container.
- O `.devcontainer/devcontainer.json` citado no Dockerfile ainda não está no repositório.

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE).
