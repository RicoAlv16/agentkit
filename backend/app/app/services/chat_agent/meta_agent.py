# -*- coding: utf-8 -*-
from typing import Callable, List, Optional

from langchain.agents import AgentExecutor
from langchain.base_language import BaseLanguageModel
from langchain.memory import ChatMessageHistory, ConversationTokenBufferMemory
from langchain.schema import AIMessage, HumanMessage

from app.core.config import settings
from app.schemas.agent_schema import AgentConfig
from app.schemas.tool_schema import LLMType
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.router_agent.SimpleRouterAgent import SimpleRouterAgent
from app.services.chat_agent.tools.tools import get_tools
from app.utils.config_loader import get_agent_config


def get_conv_token_buffer_memory(
    chat_messages: List[AIMessage | HumanMessage],
    api_key: str,
) -> ConversationTokenBufferMemory:
    """
    Get a ConversationTokenBufferMemory from a list of chat messages.

    This function takes a list of chat messages and returns a ConversationTokenBufferMemory object.
    It first gets the agent configuration and the language model, and then creates a ConversationTokenBufferMemory
    object. It then iterates over the chat messages, saving the context of the conversation to the memory.

    Args:
        chat_messages (List[Union[AIMessage, HumanMessage]]): The list of chat messages.
        api_key (str): The API key.

    Returns:
        ConversationTokenBufferMemory: The ConversationTokenBufferMemory object.
    """
    agent_config = get_agent_config()
    llm = get_llm(
        agent_config.common.llm,
        api_key=api_key,
    )
    chat_history = ChatMessageHistory()
    memory = ConversationTokenBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        max_token_limit=agent_config.common.max_token_length,
        llm=llm,
        chat_memory=chat_history,
    )

    i = 0
    while i < len(chat_messages):
        if isinstance(
            chat_messages[i],
            HumanMessage,
        ):
            if isinstance(
                chat_messages[i + 1],
                AIMessage,
            ):
                memory.save_context(
                    inputs={"input": chat_messages[i].content},
                    outputs={"output": chat_messages[i + 1].content},  # type: ignore
                )
                i += 1
        else:
            memory.save_context(
                inputs={"input": chat_messages[i].content},
                outputs={"output": ""},
            )
        i += 1

    return memory


def create_meta_agent(
    agent_config: AgentConfig,
    get_llm_hook: Callable[[LLMType, Optional[str]], BaseLanguageModel] = get_llm,
) -> AgentExecutor:
    """
    Create a meta agent from a config.

    This function takes an AgentConfig object and creates a MetaAgent.
    It retrieves the language models and the list tools, with which a SimpleRouterAgent is created.
    Then, it returns an AgentExecutor.

    Args:
        agent_config (AgentConfig): The AgentConfig object.

    Returns:
        AgentExecutor: The AgentExecutor object.
    """
    api_key = agent_config.api_key
    if api_key is None or api_key == "":
        api_key = settings.OPENAI_API_KEY

    llm = get_llm_hook(
        agent_config.common.llm,
        api_key,
    )

    tools = get_tools(tools=agent_config.tools)
    simple_router_agent = SimpleRouterAgent.from_llm_and_tools(
        tools=tools,
        llm=llm,
        prompt_message=agent_config.prompt_message,
        system_context=agent_config.system_context,
        action_plans=agent_config.action_plans,
    )
    return AgentExecutor.from_agent_and_tools(
        agent=simple_router_agent,
        tools=tools,
        verbose=True,
        max_iterations=15,
        max_execution_time=300,
        early_stopping_method="generate",
        handle_parsing_errors=True,
    )


# Ajoutez ces imports si nécessaires
from typing import List, Tuple
from app.api.deps import get_redis_client

async def batch_save_context(memory: ConversationTokenBufferMemory, chat_pairs: List[Tuple[str, str]]):
    """Batch saves chat history instead of inserting one by one."""
    async with redis_pool.pipeline(transaction=True) as pipe:
        for user_msg, ai_msg in chat_pairs:
            pipe.set(f"chat_history:{user_msg}", ai_msg, ex=3600)  # 1-hour TTL
        await pipe.execute()


# Dans la classe qui gère la mémoire de conversation

def adjust_memory_size(self, input_tokens_count: int, max_tokens: int = 4000):
    """Ajuste dynamiquement la taille de la mémoire en fonction de l'entrée utilisateur.
    
    Args:
        input_tokens_count: Nombre de tokens dans l'entrée utilisateur
        max_tokens: Limite maximale de tokens pour la mémoire
    """
    # Calculer combien de messages d'historique nous pouvons garder
    available_tokens = max_tokens - input_tokens_count
    
    # Réduire l'historique si nécessaire
    while self.memory_token_count > available_tokens and len(self.chat_memory.messages) > 2:
        # Supprimer les messages les plus anciens (garder au moins la dernière paire)
        self.chat_memory.messages.pop(0)
        self.chat_memory.messages.pop(0)
        # Recalculer le nombre de tokens
        self.memory_token_count = self._count_tokens_in_memory()
