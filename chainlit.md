# Bem-vindo ao ARARA! 🦜💬

Olá, desenvolvedor(a)! 👋

Este é o **ARARA**, um framework modular de orquestração de agentes baseado em LLMs (Modelos de Linguagem de Grande Escala), voltado para interações inteligentes com múltiplos agentes especializados. Ele é utilizado em contextos educacionais e institucionais, como o grupo de pesquisa HIAAC.

---

## 🔍 Sobre o Projeto

O ARARA organiza e coordena conversas entre os seguintes agentes:

- **student**: agente silencioso que observa e inicia a interação.
- **AraraBot**: agente de conversa geral para assuntos diversos e informais.
- **meeting_agent**: responde perguntas *somente* sobre reuniões da HIAAC com base em documentos do Google Docs.
- **website**: responde perguntas *somente* sobre pesquisadores do HIAAC com base no site oficial.

Esses agentes são gerenciados por um **Orquestrador**, que determina qual agente deve responder, seguindo uma lógica de transições autorizadas entre os participantes.

---

## 🔐 Privacidade e Segurança

> 🔒 **Importante:** Nenhuma informação pessoal ou de conversa é armazenada.

Seus dados **não são salvos**, **registrados**, nem utilizados para qualquer outro fim.
O ARARA roda localmente com suas credenciais e apenas acessa conteúdos públicos ou permitidos via ferramentas como Google Docs e WebCrawler.

---

## 🧭 Como Usar

A interação ocorre por mensagens via interface Chainlit.
Você envia uma pergunta, e o ARARA coordena os agentes para gerar a melhor resposta com base no conteúdo e nos especialistas disponíveis.

Para alterar comportamentos ou adicionar novos agentes, edite os arquivos Python do projeto, especialmente os que definem os agentes e o módulo principal (`main_module`).
