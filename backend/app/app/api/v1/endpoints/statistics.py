# -*- coding: utf-8 -*-
from os import getenv
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, status
from langsmith import Client
from langsmith.schemas import Run

from app.schemas.message_schema import FeedbackLangchain, FeedbackSourceBaseLangchain, IFeedback
from app.schemas.response_schema import IGetResponseBase, create_response

router = APIRouter()


@router.post(
    "/feedback",
    response_model=FeedbackLangchain,
    status_code=status.HTTP_201_CREATED,
    summary="Send user feedback",
    description="Sends user feedback to the Langsmith API for tracking and evaluation purposes.",
    responses={
        201: {"description": "Feedback successfully created"},
        404: {"description": "Run not found"},
        500: {"description": "Langsmith API error"}
    }
)
async def send_feedback(
    feedback: IFeedback,
) -> FeedbackLangchain:
    """
    Send feedback to the Langsmith API.
    
    Parameters:
    - **feedback**: Feedback data including message_id, conversation_id, score, and comments
    
    Returns:
    - Feedback object as stored in Langsmith
    
    Raises:
    - HTTPException 404: If the run associated with the message_id is not found
    - HTTPException 500: If there's an error communicating with Langsmith API
    """
    client = Client()
    try:
        runs: List[Run] = list(
            client.list_runs(
                project_name=getenv("LANGCHAIN_PROJECT"),
                filter=f'has(tags, "message_id={feedback.message_id}")',
                execution_order=1,
            )
        )
        
        if not runs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No run found for message_id: {feedback.message_id}"
            )
            
        run: Run = runs[0]

        if feedback.previous_id:
            client.delete_feedback(feedback.previous_id)

        feedback_res = client.create_feedback(
            run.id,
            feedback.key,
            score=feedback.score,
            comment=feedback.comment,
            source_info={
                "user": feedback.user,
                "conversation_id": feedback.conversation_id,
                "message_id": feedback.message_id,
                "settings_version": feedback.settings.version if feedback.settings is not None else "N/A",
            },
        )

        feedback_pydanticv2 = FeedbackLangchain(
            **feedback_res.model_dump(),  # Updated from dict() to model_dump() for Pydantic v2
            feedback_source=(
                FeedbackSourceBaseLangchain(**feedback_res.feedback_source.model_dump()) if feedback_res.feedback_source else None
            ),
        )
        return feedback_pydanticv2
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending feedback: {str(e)}"
        )

# Ajouter après l'endpoint send_feedback

@router.get(
    "/feedback/stats",
    response_model=IGetResponseBase[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get feedback statistics",
    description="Retrieves aggregated statistics about user feedback for the application.",
    responses={
        200: {"description": "Statistics successfully retrieved"},
        500: {"description": "Langsmith API error"}
    }
)
async def get_feedback_stats() -> IGetResponseBase[Dict[str, Any]]:
    """
    Get aggregated statistics about user feedback.
    
    Returns:
    - Dictionary containing feedback statistics:
      - total_feedback_count: Total number of feedback entries
      - average_score: Average score across all feedback
      - feedback_by_key: Breakdown of feedback counts by key
    
    Raises:
    - HTTPException 500: If there's an error communicating with Langsmith API
    """
    client = Client()
    try:
        # Get all feedback for the project
        all_feedback = list(client.list_feedback(
            project_name=getenv("LANGCHAIN_PROJECT")
        ))
        
        # Calculate statistics
        total_count = len(all_feedback)
        
        # Calculate average score (only for feedback with scores)
        scores = [f.score for f in all_feedback if f.score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Count feedback by key
        feedback_by_key = {}
        for f in all_feedback:
            if f.key not in feedback_by_key:
                feedback_by_key[f.key] = 0
            feedback_by_key[f.key] += 1
        
        stats = {
            "total_feedback_count": total_count,
            "average_score": avg_score,
            "feedback_by_key": feedback_by_key
        }
        
        return create_response(data=stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving feedback statistics: {str(e)}"
        )

# Ajouter après les autres endpoints

@router.get(
    "/system/health",
    response_model=IGetResponseBase[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="System health check",
    description="Checks the health of various system components and services.",
    responses={
        200: {"description": "Health check completed"},
        500: {"description": "Error checking system health"}
    }
)
async def system_health_check() -> IGetResponseBase[Dict[str, Any]]:
    """
    Check the health of various system components.
    
    Returns:
    - Dictionary containing health status of different components:
      - database: Status of the PostgreSQL database
      - redis: Status of the Redis server
      - langsmith: Status of the Langsmith connection (if enabled)
      - ollama: Status of Ollama connection (if enabled)
    
    Each component has:
    - status: "healthy", "degraded", or "unavailable"
    - details: Additional information about the component status
    """
    from app.db.session import engine
    from app.api.deps import get_redis_store
    from app.core.config import settings
    import sqlalchemy as sa
    import redis
    import httpx
    
    health_status = {}
    
    # Check database
    try:
        with engine.connect() as connection:
            connection.execute(sa.text("SELECT 1"))
        health_status["database"] = {
            "status": "healthy",
            "details": "Connection successful"
        }
    except Exception as e:
        health_status["database"] = {
            "status": "unavailable",
            "details": f"Connection failed: {str(e)}"
        }
    
    # Check Redis
    try:
        redis_store = get_redis_store()
        redis_store.ping()
        health_status["redis"] = {
            "status": "healthy",
            "details": "Connection successful"
        }
    except redis.RedisError as e:
        health_status["redis"] = {
            "status": "unavailable",
            "details": f"Connection failed: {str(e)}"
        }
    
    # Check Langsmith if enabled
    if getenv("LANGCHAIN_API_KEY"):
        try:
            client = Client()
            # Just try to list projects to check connection
            list(client.list_projects(limit=1))
            health_status["langsmith"] = {
                "status": "healthy",
                "details": "Connection successful"
            }
        except Exception as e:
            health_status["langsmith"] = {
                "status": "unavailable",
                "details": f"Connection failed: {str(e)}"
            }
    
    # Check Ollama if enabled
    if settings.OLLAMA_ENABLED:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.OLLAMA_URL}/api/tags")
                if response.status_code == 200:
                    health_status["ollama"] = {
                        "status": "healthy",
                        "details": f"Connected to Ollama, models available: {len(response.json().get('models', []))}"
                    }
                else:
                    health_status["ollama"] = {
                        "status": "degraded",
                        "details": f"Connected but returned status code {response.status_code}"
                    }
        except Exception as e:
            health_status["ollama"] = {
                "status": "unavailable",
                "details": f"Connection failed: {str(e)}"
            }
    
    # Overall system status
    statuses = [component["status"] for component in health_status.values()]
    if all(status == "healthy" for status in statuses):
        overall = "healthy"
    elif "unavailable" in statuses:
        overall = "degraded"
    else:
        overall = "operational with issues"
    
    health_status["overall"] = overall
    
    return create_response(data=health_status)
