# -*- coding: utf-8 -*-
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union
from uuid import UUID

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field, StrictBool, StrictFloat, StrictInt

from app.schemas.common_schema import QueryBase

LangchainMessage = Union[
    AIMessage,
    HumanMessage,
    SystemMessage,
]


class ICreatorRole(
    str,
    Enum,
):
    SYSTEM = "system"
    USER = "user"
    AGENT = "agent"


class IChatMessage(QueryBase):
    role: ICreatorRole
    content: str

    def to_langchain(
        self,
    ) -> LangchainMessage | None:
        match self.role:
            case ICreatorRole.SYSTEM:
                return SystemMessage(content=self.content)
            case ICreatorRole.USER:
                return HumanMessage(content=self.content)
            case ICreatorRole.AGENT:
                return AIMessage(content=self.content)
            case _:
                return None


class UserSettings(BaseModel):
    data: dict[
        str,
        Any,
    ]
    version: Optional[int] = None


class IChatQuery(QueryBase):
    messages: list[IChatMessage]
    api_key: Optional[str] = None
    conversation_id: UUID
    new_message_id: UUID
    user_email: str
    settings: Optional[UserSettings] = None


class IFeedback(QueryBase):
    conversation_id: UUID
    message_id: UUID
    user: str
    score: int
    comment: str
    key: str
    settings: Optional[UserSettings] = None
    previous_id: Optional[str] = None


SCORE_TYPE = Union[StrictBool, StrictInt, StrictFloat, None]
VALUE_TYPE = Union[Dict, StrictBool, StrictInt, StrictFloat, str, None]


class FeedbackSourceBaseLangchain(BaseModel):
    type: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class FeedbackLangchain(BaseModel):
    """Schema for getting feedback, copy of langchain Feedback type (pydantic v2)."""

    id: UUID
    created_at: datetime
    modified_at: datetime
    run_id: UUID
    key: str
    score: SCORE_TYPE = None  # En Pydantic v2, utilisez Field(default=None) pour plus de clarté
    value: VALUE_TYPE = None  # En Pydantic v2, utilisez Field(default=None) pour plus de clarté
    comment: Optional[str] = None
    correction: Union[str, dict, None] = None
    feedback_source: Optional[FeedbackSourceBaseLangchain] = None
    
    # Ajoutez model_config pour remplacer Config en v2
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "created_at": "2023-01-01T00:00:00Z",
                    "modified_at": "2023-01-01T00:00:00Z",
                    "run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "key": "correctness",
                    "score": 1.0,
                    "comment": "This response is correct"
                }
            ]
        }
    }
