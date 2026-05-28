"""
Agent Logging Service

Logs agent actions for Bloomberg Terminal-style display.
Shows decisions like "BUY Campaign XYZ £5000" when media planning is done.
"""

from typing import List, Dict, Optional, Literal
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import json


class AgentAction(Enum):
    """Types of agent actions."""
    BUY = "BUY"
    HOLD = "HOLD"
    STOP = "STOP"
    OPTIMIZE = "OPTIMIZE"
    ANALYZE = "ANALYZE"
    EXECUTE = "EXECUTE"
    MONITOR = "MONITOR"


@dataclass
class AgentLogEntry:
    """Single agent log entry."""
    
    timestamp: str
    agent: str
    action: str
    campaign: Optional[str] = None
    channel: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "£"
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    result: Optional[str] = None
    
    def to_display_string(self) -> str:
        """Format log entry for terminal display."""
        parts = [f"{self.timestamp}"]
        
        # Agent name
        parts.append(f"[{self.agent}]")
        
        # Action and details
        if self.campaign and self.amount:
            parts.append(f"{self.action} {self.campaign} {self.currency}{self.amount:,.0f}")
        elif self.campaign:
            parts.append(f"{self.action} {self.campaign}")
        else:
            parts.append(self.action)
        
        # Confidence if available
        if self.confidence:
            parts.append(f"({self.confidence*100:.0f}%)")
        
        # Result if available
        if self.result:
            parts.append(f"→ {self.result}")
        
        return " ".join(parts)


class AgentLogger:
    """
    Logs agent actions for Bloomberg Terminal display.
    
    This service:
    - Logs all agent decisions during media planning
    - Formats logs for CLI-style display
    - Tracks BUY/HOLD/STOP signals with campaign details
    - Provides real-time agent activity feed
    """
    
    def __init__(self):
        """Initialize agent logger."""
        self.logs: List[AgentLogEntry] = []
        self.max_logs = 100  # Keep last 100 logs
    
    def log_buy(
        self,
        agent: str,
        campaign: str,
        amount: float,
        channel: Optional[str] = None,
        confidence: Optional[float] = None,
        reasoning: Optional[str] = None
    ):
        """
        Log a BUY action.
        
        Args:
            agent: Agent name (e.g., "THOMPSON_ALLOCATOR", "BID_STRATEGY")
            campaign: Campaign name
            amount: Budget amount
            channel: Platform channel
            confidence: Confidence score (0-1)
            reasoning: Reasoning for the decision
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log = AgentLogEntry(
            timestamp=timestamp,
            agent=agent,
            action=AgentAction.BUY.value,
            campaign=campaign,
            channel=channel,
            amount=amount,
            confidence=confidence,
            reasoning=reasoning,
            result="Executing bid"
        )
        
        self._add_log(log)
    
    def log_hold(
        self,
        agent: str,
        campaign: str,
        channel: Optional[str] = None,
        confidence: Optional[float] = None,
        reasoning: Optional[str] = None
    ):
        """
        Log a HOLD action.
        
        Args:
            agent: Agent name
            campaign: Campaign name
            channel: Platform channel
            confidence: Confidence score (0-1)
            reasoning: Reasoning for the decision
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log = AgentLogEntry(
            timestamp=timestamp,
            agent=agent,
            action=AgentAction.HOLD.value,
            campaign=campaign,
            channel=channel,
            confidence=confidence,
            reasoning=reasoning,
            result="Maintaining current spend"
        )
        
        self._add_log(log)
    
    def log_stop(
        self,
        agent: str,
        campaign: str,
        channel: Optional[str] = None,
        confidence: Optional[float] = None,
        reasoning: Optional[str] = None
    ):
        """
        Log a STOP action.
        
        Args:
            agent: Agent name
            campaign: Campaign name
            channel: Platform channel
            confidence: Confidence score (0-1)
            reasoning: Reasoning for the decision
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log = AgentLogEntry(
            timestamp=timestamp,
            agent=agent,
            action=AgentAction.STOP.value,
            campaign=campaign,
            channel=channel,
            confidence=confidence,
            reasoning=reasoning,
            result="Campaign paused"
        )
        
        self._add_log(log)
    
    def log_optimize(
        self,
        agent: str,
        campaign: str,
        optimization_type: str,
        confidence: Optional[float] = None
    ):
        """
        Log an OPTIMIZE action.
        
        Args:
            agent: Agent name
            campaign: Campaign name
            optimization_type: Type of optimization
            confidence: Confidence score
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log = AgentLogEntry(
            timestamp=timestamp,
            agent=agent,
            action=AgentAction.OPTIMIZE.value,
            campaign=campaign,
            confidence=confidence,
            reasoning=f"Optimizing: {optimization_type}",
            result="Optimization applied"
        )
        
        self._add_log(log)
    
    def log_analyze(
        self,
        agent: str,
        analysis_type: str,
        result: Optional[str] = None
    ):
        """
        Log an ANALYZE action.
        
        Args:
            agent: Agent name
            analysis_type: Type of analysis
            result: Analysis result
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log = AgentLogEntry(
            timestamp=timestamp,
            agent=agent,
            action=AgentAction.ANALYZE.value,
            reasoning=analysis_type,
            result=result
        )
        
        self._add_log(log)
    
    def log_execute(
        self,
        agent: str,
        execution_type: str,
        result: Optional[str] = None
    ):
        """
        Log an EXECUTE action.
        
        Args:
            agent: Agent name
            execution_type: Type of execution
            result: Execution result
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log = AgentLogEntry(
            timestamp=timestamp,
            agent=agent,
            action=AgentAction.EXECUTE.value,
            reasoning=execution_type,
            result=result
        )
        
        self._add_log(log)
    
    def log_monitor(
        self,
        agent: str,
        metric: str,
        value: str
    ):
        """
        Log a MONITOR action.
        
        Args:
            agent: Agent name
            metric: Metric being monitored
            value: Metric value
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log = AgentLogEntry(
            timestamp=timestamp,
            agent=agent,
            action=AgentAction.MONITOR.value,
            reasoning=f"Monitoring: {metric}",
            result=value
        )
        
        self._add_log(log)
    
    def _add_log(self, log: AgentLogEntry):
        """Add log entry and maintain max size."""
        self.logs.append(log)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
    
    def get_logs(self, limit: int = 20) -> List[str]:
        """
        Get formatted log entries for display.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of formatted log strings
        """
        recent_logs = self.logs[-limit:] if limit else self.logs
        return [log.to_display_string() for log in recent_logs]
    
    def get_logs_dict(self, limit: int = 20) -> List[Dict]:
        """
        Get log entries as dictionaries.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of log dictionaries
        """
        recent_logs = self.logs[-limit:] if limit else self.logs
        return [asdict(log) for log in recent_logs]
    
    def clear_logs(self):
        """Clear all logs."""
        self.logs = []
    
    def get_logs_by_agent(self, agent: str, limit: int = 20) -> List[str]:
        """
        Get logs for a specific agent.
        
        Args:
            agent: Agent name to filter by
            limit: Maximum number of logs
            
        Returns:
            List of formatted log strings
        """
        agent_logs = [log for log in self.logs if log.agent == agent]
        recent_logs = agent_logs[-limit:] if limit else agent_logs
        return [log.to_display_string() for log in recent_logs]
    
    def get_logs_by_campaign(self, campaign: str, limit: int = 20) -> List[str]:
        """
        Get logs for a specific campaign.
        
        Args:
            campaign: Campaign name to filter by
            limit: Maximum number of logs
            
        Returns:
            List of formatted log strings
        """
        campaign_logs = [log for log in self.logs if log.campaign == campaign]
        recent_logs = campaign_logs[-limit:] if limit else campaign_logs
        return [log.to_display_string() for log in recent_logs]


# Global logger instance
agent_logger = AgentLogger()