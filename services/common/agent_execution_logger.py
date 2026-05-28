"""
Agent Execution Logger Service

Logs agent executions to the database for audit and analysis.
"""

import uuid
from typing import Optional, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.database import get_db_session
from shared.models.demo_models import AgentExecutionHistory


class AgentExecutionLogger:
    """
    Logs agent executions to the database for audit trail and analysis.
    
    This service:
    - Logs all agent executions with input/output data
    - Tracks performance metrics (latency, tokens, cost)
    - Maintains audit trail for optimization
    - Enables analysis of agent behavior over time
    """
    
    async def log_execution(
        self,
        agent_name: str,
        agent_type: str,
        action: str,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        execution_time_ms: Optional[int] = None,
        tokens_used: Optional[int] = None,
        cost_usd: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        client_id: Optional[str] = None,
        campaign_id: Optional[str] = None
    ):
        """
        Log an agent execution to the database.
        
        Args:
            agent_name: Name of the agent (e.g., "bid_strategy_agent")
            agent_type: Type of agent (e.g., "bid_strategy")
            action: Action performed (e.g., "optimize_bid")
            input_data: Input data for the agent
            output_data: Output data from the agent
            execution_time_ms: Execution time in milliseconds
            tokens_used: Number of tokens used
            cost_usd: Cost in USD
            success: Whether execution was successful
            error_message: Error message if failed
            client_id: Client ID (optional)
            campaign_id: Campaign ID (optional)
        """
        async with get_db_session() as session:
            execution = AgentExecutionHistory(
                id=str(uuid.uuid4()),
                agent_name=agent_name,
                agent_type=agent_type,
                action=action,
                input_data=input_data,
                output_data=output_data,
                execution_time_ms=execution_time_ms,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                success=success,
                error_message=error_message,
                client_id=client_id,
                campaign_id=campaign_id,
                execution_date=datetime.now()
            )
            
            session.add(execution)
            await session.commit()
            
            print(f"[LOG] {agent_name} {action} - Success: {success}, Time: {execution_time_ms}ms")
    
    async def log_chat_execution(
        self,
        agent_name: str,
        model: str,
        user_message: str,
        agent_response: str,
        tokens_used: int,
        cost_usd: float,
        execution_time_ms: int,
        success: bool = True
    ):
        """
        Log a chat execution.
        
        Args:
            agent_name: Agent name
            model: Model used (e.g., "gpt-4")
            user_message: User's message
            agent_response: Agent's response
            tokens_used: Tokens used
            cost_usd: Cost in USD
            execution_time_ms: Execution time
            success: Whether execution was successful
        """
        await self.log_execution(
            agent_name=agent_name,
            agent_type="chat",
            action="chat_response",
            input_data={"user_message": user_message, "model": model},
            output_data={"agent_response": agent_response},
            execution_time_ms=execution_time_ms,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            success=success
        )
    
    async def get_execution_history(
        self,
        agent_name: Optional[str] = None,
        limit: int = 50
    ) -> list:
        """
        Get execution history from database.
        
        Args:
            agent_name: Filter by agent name (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of AgentExecutionHistory objects
        """
        async with get_db_session() as session:
            query = select(AgentExecutionHistory)
            
            if agent_name:
                query = query.where(AgentExecutionHistory.agent_name == agent_name)
            
            query = query.order_by(AgentExecutionHistory.execution_date.desc())
            query = query.limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_execution_stats(
        self,
        agent_name: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """
        Get execution statistics for an agent.
        
        Args:
            agent_name: Agent name (optional)
            days: Number of days to analyze
            
        Returns:
            Dictionary with statistics
        """
        from datetime import timedelta
        from sqlalchemy import func
        
        async with get_db_session() as session:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            query = select(AgentExecutionHistory).where(
                AgentExecutionHistory.execution_date >= cutoff_date
            )
            
            if agent_name:
                query = query.where(AgentExecutionHistory.agent_name == agent_name)
            
            # Get count
            total_count_result = await session.execute(
                query.with_only_columns(func.count(AgentExecutionHistory.id))
            )
            total_count = total_count_result.scalar()
            
            # Get success rate
            success_count_result = await session.execute(
                query.where(AgentExecutionHistory.success == True)
                .with_only_columns(func.count(AgentExecutionHistory.id))
            )
            success_count = success_count_result.scalar()
            
            # Get average latency
            avg_latency_result = await session.execute(
                query.with_only_columns(func.avg(AgentExecutionHistory.execution_time_ms))
            )
            avg_latency = avg_latency_result.scalar()
            
            # Get total tokens
            total_tokens_result = await session.execute(
                query.with_only_columns(func.sum(AgentExecutionHistory.tokens_used))
            )
            total_tokens = total_tokens_result.scalar()
            
            # Get total cost
            total_cost_result = await session.execute(
                query.with_only_columns(func.sum(AgentExecutionHistory.cost_usd))
            )
            total_cost = total_cost_result.scalar()
            
            return {
                "total_executions": total_count or 0,
                "success_count": success_count or 0,
                "success_rate": (success_count / total_count) if total_count else 0,
                "avg_latency_ms": avg_latency or 0,
                "total_tokens": total_tokens or 0,
                "total_cost_usd": float(total_cost) if total_cost else 0.0
            }


# Global logger instance
agent_execution_logger = AgentExecutionLogger()