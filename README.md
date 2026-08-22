# Bolha Pessoal — Alexa Skill (Gemini)

Skill de voz para Alexa (invocação: "bolha pessoal") que responde perguntas usando a
API do Gemini. Alexa-hosted skill, integração via `urllib` puro (sem SDK do Gemini).

## Estrutura

```
skill.json                          → manifesto da skill
interactionModels/custom/pt-BR.json → modelo de interação (intents, samples)
lambda/lambda_function.py           → handlers da Alexa + chamada ao Gemini
lambda/utils.py                     → utilitário auxiliar (presigned URL do S3, do template padrão)
lambda/requirements.txt             → dependências (ask-sdk-core)
```

## Configuração

1. Copie `.env.example` para `.env` e preencha com sua própria chave do Gemini:
   ```
   cp .env.example .env
   ```
2. Instale as dependências:
   ```
   pip install -r lambda/requirements.txt
   ```

## Nota sobre o `.env`

Este projeto está publicado como Alexa-hosted skill, que não suporta variáveis de
ambiente nativamente. A versão publicada de fato no Code tab do Alexa Developer
Console mantém a chave como constante local (fora deste repositório); esta cópia
pública lê a chave via `os.environ`, como boa prática — mesmo que a execução real na
Alexa não injete essa variável automaticamente.

## Demonstração

O código depende do runtime do Alexa Skills Kit (eventos, sessão, slots) — não é
pensado pra ser executado standalone com `python lambda_function.py`. A validação de
funcionamento foi feita pelo simulador do Alexa Developer Console e por testes de voz
direto no dispositivo Echo pessoal.

**Vídeo**: Interação com a Alexa skill respondendo perguntas via Gemini API

https://github.com/user-attachments/assets/0d18c030-db07-45ec-9378-7c5daac10bc9
