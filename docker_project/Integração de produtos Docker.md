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
│   ├── mycrontab       # agendamento: a cada hora
│   └── run.sh          # cria as pastas, executa o app.py e limpa coletas antigas
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
2. O cron lê `/etc/cron.d/mycrontab` e dispara `run.sh` a cada hora, no minuto 0.
3. `run.sh` define `PRODUCTION=1` e executa `app.py --produtos --carts` com o Python do venv.
4. `app.py` baixa os produtos e os carrinhos e grava um JSON para cada um em `/data/json`, com o horário UTC no nome.
5. Os logs vão para `/data/logs/loja.log`, com rotação em 10 KB e 3 backups.
6. `run.sh` mantém as 720 coletas mais recentes de cada tipo (30 dias) e apaga as demais. O volume fica limitado a cerca de 370 MB, e o limite por quantidade evita que uma API fora do ar apague o histórico.

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

- [x] `scripts/mycrontab`: o usuário estava como `docker_doc`, mas o criado no Dockerfile é `doctor_dock`. O job agendado não rodava.
- [x] `scripts/entrypoint.sh`: acompanhava `/data/logs/loj.log`, mas o arquivo gerado é `loja.log`. Agora usa `tail -F`, que continua acompanhando o log depois da rotação.
- [x] `scripts/run.sh`: usava `mkdir ~p` em vez de `mkdir -p`.
- [x] `app/app.py`: em produção, os JSON iam para `/home/doctor_dock/`. Agora vão para `/data/json`, dentro do volume.
- [x] `app/cliente.py`: se a requisição falhava, `result` ficava indefinido e o programa quebrava com `UnboundLocalError`.
- [x] `app/cliente.py`: `can_write` retornava `None` em `IOError`.
- [x] `app/cliente.py`: a API devolve 30 itens por padrão. Agora usa `limit=0`, que traz todos os itens.
- [x] `Dockerfile`: `chmod 0644` no `mycrontab`, porque o build no Windows pode copiar o arquivo com modo `0755`.
- [x] `scripts/mycrontab` e `scripts/run.sh`: o cron rodava a cada minuto, sem limpeza, e gerava cerca de 740 MB por dia. Agora roda a cada hora, com retenção de 720 coletas.
- [ ] Criar a pasta `.devcontainer` com o `devcontainer.json`.

## Próximos passos

- Montar o relatório no Power BI lendo os JSON de `C:\dados\docker_project\json`, a pasta do Windows ligada a `/data` com `-v`.

## Teste em container (31/10/2026)

Imagem de produção construída (1,63 GB) e executada com bind mount. O cron disparou nos minutos 01:42 e 01:43 UTC, os logs apareceram em `docker logs` e os JSON chegaram à pasta do Windows com 194 produtos e 208 carrinhos.

## Teste da retenção (01/11/2026)

Imagem de teste executada em volume separado, sem usar a pasta do Power BI.

- Com 725 coletas antigas de cada tipo mais uma nova, `run.sh` deixou 720 de cada tipo, removeu as mais antigas e não tocou em um arquivo de outro tipo.
- Com a agenda trocada temporariamente para cada minuto, só no container de teste, o cron executou `run.sh` e manteve as 720 coletas. A execução no minuto 0 não foi observada.
- Sem rede, a coleta falhou e os arquivos existentes continuaram no volume.

**Limite para linha temporal:** os JSON coletados em 31/10 e 01/11, com cerca de 20 horas de diferença, têm o mesmo hash SHA-256. Enquanto a API devolver os mesmos dados, uma série temporal fica plana, mesmo com o histórico guardado.
