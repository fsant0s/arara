#!/usr/bin/env python
"""
Exemplo básico de um sistema de recomendação usando o framework NEURON.

Este script demonstra como configurar um sistema simples de recomendação
composto por dois neurônios:
1. UserProfiler: Analisa as preferências do usuário com base nas entradas
2. Recommender: Gera recomendações com base no perfil do usuário

Os neurônios são coordenados por um RouterNeuron.
"""

import logging
import os
from typing import Any, Dict

from neuron.capabilities import EpisodicMemoryCapability, ReflectionCapability
from neuron.clients import ClientWrapper
from neuron.neurons import Neuron, RouterNeuron, User

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_environment() -> None:
    """
    Configurar variáveis de ambiente a partir do arquivo .env se não estiverem definidas.

    Importante ter as chaves API configuradas.
    """
    if os.path.exists(".env"):
        logger.info("Carregando variáveis de ambiente do arquivo .env")
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if not os.environ.get(key):
                            os.environ[key] = value
                            logger.debug(f"Definindo {key}={value}")
                    except ValueError:
                        logger.warning(f"Ignorando linha inválida no .env: {line}")


def create_neuron_system() -> Dict[str, Any]:
    """
    Criar o sistema de neurônios para recomendação.

    Returns:
        Dict[str, Any]: Um dicionário contendo todos os componentes do sistema
    """
    # Verificar qual provedor de LLM usar com base nas variáveis de ambiente
    # Prioridade: Groq > OpenAI
    if os.environ.get("GROQ_API_KEY"):
        client = ClientWrapper(provider="groq", model="llama3-70b-8192")
        logger.info("Usando Groq como provedor de LLM")
    elif os.environ.get("OPENAI_API_KEY"):
        client = ClientWrapper(provider="openai", model="gpt-4o")
        logger.info("Usando OpenAI como provedor de LLM")
    else:
        logger.error("Nenhuma API key válida encontrada. Configure as variáveis de ambiente.")
        raise ValueError("API keys não configuradas")

    # Criar o neurônio de perfil de usuário
    user_profiler = Neuron(
        name="UserProfiler",
        description="Analisa as preferências e contexto do usuário com base nas entradas.",
        llm_config=True,
    )
    user_profiler.client_cache = client
    user_profiler.update_system_message(
        """
    Você é um analisador de perfil de usuário. Sua função é analisar as preferências,
    interesses e contexto do usuário com base nas entradas que eles fornecem.

    Extraia informações úteis como:
    - Domínio do interesse (filmes, livros, produtos, etc.)
    - Preferências específicas (gêneros, características, etc.)
    - Limitações ou restrições
    - Contexto relevante

    Retorne um JSON estruturado com estas informações.
    """
    )

    # Adicionar capacidade de memória para lembrar das interações anteriores
    user_profiler.add_capability(EpisodicMemoryCapability())

    # Criar o neurônio de recomendação
    recommender = Neuron(
        name="Recommender",
        description="Gera recomendações personalizadas com base no perfil do usuário.",
        llm_config=True,
    )
    recommender.client_cache = client
    recommender.update_system_message(
        """
    Você é um sistema de recomendação especializado. Sua função é gerar recomendações
    personalizadas com base no perfil do usuário fornecido.

    Suas recomendações devem ser:
    - Relevantes para os interesses e preferências do usuário
    - Específicas e actionable
    - Incluir uma breve explicação de por que cada item é recomendado
    - Organizadas por relevância

    Apresente suas recomendações em um formato claro e estruturado.
    """
    )

    # Adicionar capacidades para melhorar as recomendações
    recommender.add_capability(EpisodicMemoryCapability())
    recommender.add_capability(ReflectionCapability())

    # Criar o neurônio roteador para coordenar os outros neurônios
    router = RouterNeuron(
        name="RecommendationRouter",
        description="Coordena o fluxo entre o analisador de perfil e o recomendador.",
        llm_config=True,
    )
    router.client_cache = client
    router.update_system_message(
        """
    Você é um coordenador de sistema de recomendação. Sua função é:

    1. Receber consultas e solicitações do usuário
    2. Encaminhar para o UserProfiler para análise do perfil
    3. Encaminhar o perfil analisado para o Recommender
    4. Retornar as recomendações finais para o usuário

    Mantenha o contexto da conversa entre as diferentes etapas.
    """
    )

    # Criar o objeto de usuário
    user = User(name="ExampleUser")

    return {
        "client": client,
        "user_profiler": user_profiler,
        "recommender": recommender,
        "router": router,
        "user": user,
    }


def process_user_query(system: Dict[str, Any], query: str) -> str:
    """
    Processar uma consulta do usuário através do sistema de recomendação.

    Args:
        system: O sistema de neurônios
        query: A consulta do usuário

    Returns:
        str: A resposta de recomendação
    """
    logger.info(f"Processando consulta: {query}")

    # Enviar a consulta do usuário para o roteador
    router = system["router"]
    user = system["user"]

    response = router.receive(query, user)

    # O roteador decide internamente para qual neurônio enviar a mensagem
    # e encaminha para o UserProfiler
    user_profiler = system["user_profiler"]
    profile_analysis = user_profiler.receive(query, router)
    logger.info(f"Análise de perfil: {profile_analysis}")

    # Enviar a análise do perfil para o recomendador
    recommender = system["recommender"]
    recommendations = recommender.receive(profile_analysis, router)
    logger.info(f"Recomendações geradas")

    # O roteador recebe as recomendações e retorna para o usuário
    final_response = router.generate_reply(recommendations)

    return final_response


def main() -> None:
    """Função principal para demonstrar o sistema de recomendação."""
    setup_environment()

    try:
        # Criar o sistema de neurônios
        system = create_neuron_system()

        print("\n===== Sistema de Recomendação NEURON =====\n")
        print("Digite 'sair' para encerrar o programa.")

        while True:
            query = input("\nO que você está procurando hoje? ")

            if query.lower() in ["sair", "exit", "quit"]:
                break

            if not query.strip():
                continue

            try:
                response = process_user_query(system, query)
                print("\n" + response)
            except Exception as e:
                logger.error(f"Erro ao processar consulta: {e}")
                print(f"\nOcorreu um erro ao processar sua consulta: {e}")

        print("\nObrigado por usar o sistema de recomendação NEURON!")

    except Exception as e:
        logger.error(f"Erro na inicialização do sistema: {e}")
        print(f"Erro na inicialização do sistema: {e}")


if __name__ == "__main__":
    main()
