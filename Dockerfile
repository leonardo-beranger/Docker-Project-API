# Será um Docker multi-stage

# Multi-stage permite separar o que é comum (build) do que é específico de cada
# ambiente (desenvolvimento, produção), reaproveitando camadas e evitando
# ferramentas de dev na imagem final.

# 1° estágio: Esse estágio se refere a camada Build (desenvolvimento e produção)
# Tudo o que for comum aos dois ambientes fica aqui.
# O "AS build" dá um nome ao estágio para ser referenciado depois (FROM build)
# e para o devcontainer.json escolher o alvo (target).
FROM python:3.15.0-bookworm AS build

# Garantindo atualização da imagem
# Atualiza o índice de pacotes do apt antes de instalar qualquer coisa.
RUN apt-get update
# O -y responde "sim" automaticamente, já que o build não é interativo.
# O cron permite agendar a execução de scripts dentro do container.
RUN apt-get install cron -y
# Criando usuario, como a imagem é baseado em um debian, esse caminho padrão possui o bash
# O -m cria o diretório home (/home/doctor_dock) e o -s define o shell de login.
# Usar um usuário comum, em vez de root, é uma boa prática de segurança.
RUN useradd -m -s /usr/bin/bash doctor_dock

# Camada de desenvolvimento
# Aproveitando o estágio anterior
# Herda tudo do estágio "build" (pacotes, cron e usuário já criados) e
# adiciona apenas o que é específico de desenvolvimento.
# Este é o estágio apontado em "target": "development" no devcontainer.json.
FROM build AS development

# A partir daqui, os comandos rodam como doctor_dock (não mais root).
# Isso faz o $HOME e o ~ apontarem para /home/doctor_dock, e o venv criado
# abaixo já nasce com as permissões corretas.
USER doctor_dock

# Cria o ambiente virtual, isolando as dependências do projeto das do Python do sistema.
# Fica em /home/doctor_dock/venv, o mesmo caminho do python.defaultInterpreterPath
# configurado no devcontainer.json.
RUN python -m venv $HOME/venv

# Ativa o venv automaticamente em todo terminal bash aberto no container,
# evitando rodar "source venv/bin/activate" manualmente a cada sessão.
RUN echo "source $HOME/venv/bin/activate" >> ~/.bashrc


# Stage - produção
# Também herda do estágio "build", e não de "development": assim a imagem final
# não carrega nada do ambiente de desenvolvimento.
# Para gerar esta imagem: docker build --target production -t docker-project-api .
FROM build AS production

# Garantindo o usuário root
# Os passos a seguir escrevem em /app, /data e /etc/cron.d, que exigem root.
USER root

# Diferente do desenvolvimento, em que o código é montado pelo devcontainer,
# em produção o código precisa estar dentro da imagem.
COPY app/ /app/
COPY requirements.txt /app
COPY scripts/*.sh /app
# Os arquivos em /etc/cron.d são lidos automaticamente pelo cron.
COPY scripts/mycrontab /etc/cron.d

# /data guarda o que precisa sobreviver ao container. O VOLUME faz o Docker
# manter esse diretório fora da camada de escrita do container.
RUN mkdir -p /data
VOLUME ["/data"]

# A aplicação roda como doctor_dock, que precisa ser dono dos diretórios em que escreve.
# A forma exec (lista JSON) executa o comando direto, sem passar por um shell.
# Atenção: alterar /data depois do VOLUME só tem efeito com o BuildKit; o builder
# legado descarta essas mudanças.
RUN ["chown", "-R", "doctor_dock:doctor_dock", "/app"]
RUN ["chown", "-R", "doctor_dock:doctor_dock", "/data"]
# Garante a permissão de execução, que pode se perder quando o build é feito no Windows.
RUN ["chmod", "+x", "/app/entrypoint.sh"]
RUN ["chmod", "+x", "/app/run.sh"]

# Muda para doctor_dock para que o venv e os pacotes pertençam a esse usuário.
USER doctor_dock

# O venv é chamado pelo caminho completo porque cada RUN abre um shell novo,
# então um "source activate" não valeria para o comando seguinte.
RUN python -m venv $HOME/venv
RUN $HOME/venv/bin/pip install -r /app/requirements.txt

# Volta para root porque o daemon do cron precisa dele para iniciar. O job em si
# roda com o usuário informado em scripts/mycrontab.
USER root
# Inicia o cron e mantém o container vivo acompanhando o arquivo de log.
ENTRYPOINT ["/app/entrypoint.sh"]