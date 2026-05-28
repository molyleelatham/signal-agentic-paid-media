"""
Overmind Integration Layer for Agent Tracing and Optimization.

This implements Module 10 from the technical spec:
- Overmind SDK integration for LLM tracing
- Quality criteria evaluation
- P&L score as ground truth for optimization
"""
from functools import wraps
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
import os

try:
    from overmind import init, get_tracer, set_user, set_tag, capture_exception
    OVERMIND_AVAILABLE = True
except ImportError:
    OVERMIND_AVAILABLE = False
    print("Warning: Overmind SDK not available. Install with: pip install overmind")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not available. Install with: pip install openai")

from shared.agents.cursor_integration import CursorComposerService


class OvermindTracer:
    """
    Overmind tracer for agent function calls.
    
    Uses the real Overmind SDK for tracing LLM calls and agent operations.
    """
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None):
        """
        Initialize Overmind tracer.
        
        Args:
            api_key: Overmind API key (falls back to OVERMIND_API_KEY env var)
            project_id: Project ID for organization (used as service name)
        """
        self.api_key = api_key or os.getenv("OVERMIND_API_KEY")
        self.project_id = project_id or os.getenv("OVERMIND_PROJECT_ID", "signal-platform")
        self.initialized = False
        self.tracer = None
        
        if OVERMIND_AVAILABLE and self.api_key:
            try:
                # Initialize Overmind SDK
                init(
                    overmind_api_key=self.api_key,
                    service_name=self.project_id,
                    environment=os.getenv("OVERMIND_ENVIRONMENT", "development"),
                    providers=None  # Auto-detect installed providers
                )
                
                # Get tracer for custom spans
                self.tracer = get_tracer()
                self.initialized = True
                print(f"✅ Overmind SDK initialized successfully for service: {self.project_id}")
                
            except Exception as e:
                print(f"❌ Failed to initialize Overmind SDK: {e}")
                self.initialized = False
        else:
            if not OVERMIND_AVAILABLE:
                print("⚠️  Overmind SDK not installed. Install with: pip install overmind")
            if not self.api_key:
                print("⚠️  Overmind API key not provided. Set OVERMIND_API_KEY environment variable.")
    
    def trace(
        self,
        name: str,
        tags: List[str] = None,
        quality_criteria: List[str] = None
    ):
        """
        Decorator for tracing agent functions with Overmind.
        
        Args:
            name: Name of the traced function
            tags: Tags for categorization
            quality_criteria: Quality criteria for evaluation
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not self.initialized or not self.tracer:
                    # Fallback: execute without tracing
                    return await func(*args, **kwargs)
                
                # Execute with Overmind tracing
                with self.tracer.start_as_current_span(name) as span:
                    try:
                        # Add tags to span
                        if tags:
                            for tag in tags:
                                set_tag(tag, "true")
                        
                        # Add quality criteria as attributes
                        if quality_criteria:
                            span.set_attribute("quality_criteria", quality_criteria)
                        
                        # Add input parameters
                        span.set_attribute("input_args", str(args))
                        span.set_attribute("input_kwargs", str(kwargs))
                        
                        # Execute the function
                        result = await func(*args, **kwargs)
                        
                        # Add output to span
                        span.set_attribute("output", str(result)[:1000])  # Truncate long outputs
                        
                        return result
                        
                    except Exception as e:
                        # Capture exception with Overmind
                        capture_exception(e)
                        span.set_attribute("error", str(e))
                        raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not self.initialized or not self.tracer:
                    return func(*args, **kwargs)
                
                with self.tracer.start_as_current_span(name) as span:
                    try:
                        if tags:
                            for tag in tags:
                                set_tag(tag, "true")
                        
                        if quality_criteria:
                            span.set_attribute("quality_criteria", quality_criteria)
                        
                        span.set_attribute("input_args", str(args))
                        span.set_attribute("input_kwargs", str(kwargs))
                        
                        result = func(*args, **kwargs)
                        span.set_attribute("output", str(result)[:1000])
                        
                        return result
                        
                    except Exception as e:
                        capture_exception(e)
                        span.set_attribute("error", str(e))
                        raise
            
            # Return appropriate wrapper based on function type
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def set_user_context(self, user_id: str, user_data: Dict = None):
        """
        Set user context for traces.
        
        Args:
            user_id: User identifier
            user_data: Additional user metadata
        """
        if not self.initialized:
            return
        
        try:
            set_user(user_id)
            if user_data:
                for key, value in user_data.items():
                    set_tag(f"user.{key}", str(value))
        except Exception as e:
            print(f"Error setting user context: {e}")
    
    def set_custom_tag(self, key: str, value: str):
        """
        Set a custom tag for the current trace.
        
        Args:
            key: Tag key
            value: Tag value
        """
        if not self.initialized:
            return
        
        try:
            set_tag(key, value)
        except Exception as e:
            print(f"Error setting custom tag: {e}")
    
    def log_outcome(
        self,
        trace_id: str,
        outcome_label: str,
        outcome_value: float,
        metadata: Dict = None
    ) -> None:
        """
        Log outcome for a trace (e.g., P&L score).
        
        This connects agent decisions to real-world outcomes for optimization.
        
        Args:
            trace_id: Trace identifier
            outcome_label: Label for the outcome (e.g., "net_pnl")
            outcome_value: Value of the outcome
            metadata: Additional outcome metadata
        """
        if not self.initialized:
            return
        
        try:
            # Set outcome as a tag on the current span
            set_tag(f"outcome.{outcome_label}", str(outcome_value))
            
            if metadata:
                for key, value in metadata.items():
                    set_tag(f"outcome.{outcome_label}.{key}", str(value))
            
            print(f"✅ Logged outcome for trace {trace_id}: {outcome_label}={outcome_value}")
        except Exception as e:
            print(f"❌ Error logging outcome: {e}")
    
    def start_span(self, name: str):
        """
        Start a custom span for manual tracing.
        
        Args:
            name: Span name
            
        Returns:
            Context manager for the span
        """
        if not self.initialized or not self.tracer:
            # Return no-op context manager
            from contextlib import nullcontext
            return nullcontext()
        
        return self.tracer.start_as_current_span(name)


class AgentMemory:
    """
    Memory system for agents to store context and decisions.
    """
    
    def __init__(self):
        """Initialize agent memory."""
        self.short_term_memory: Dict[str, Any] = {}
        self.long_term_memory: Dict[str, List[Any]] = {}
        self.decision_history: List[Dict] = []
    
    def store(self, key: str, value: Any, memory_type: str = "short") -> None:
        """
        Store information in agent memory.
        
        Args:
            key: Storage key
            value: Value to store
            memory_type: "short" or "long" term memory
        """
        if memory_type == "short":
            self.short_term_memory[key] = value
        else:
            if key not in self.long_term_memory:
                self.long_term_memory[key] = []
            self.long_term_memory[key].append({
                "value": value,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def retrieve(self, key: str, memory_type: str = "short") -> Any:
        """
        Retrieve information from agent memory.
        
        Args:
            key: Storage key
            memory_type: "short" or "long" term memory
        
        Returns:
            Stored value or None
        """
        if memory_type == "short":
            return self.short_term_memory.get(key)
        else:
            return self.long_term_memory.get(key, [])
    
    def record_decision(
        self,
        agent_name: str,
        decision: str,
        reasoning: str,
        context: Dict
    ) -> None:
        """
        Record a decision in agent history.
        
        Args:
            agent_name: Name of the agent making the decision
            decision: The decision made
            reasoning: Reasoning behind the decision
            context: Context available to the agent
        """
        self.decision_history.append({
            "agent_name": agent_name,
            "decision": decision,
            "reasoning": reasoning,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_recent_decisions(
        self,
        agent_name: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent decisions from history.
        
        Args:
            agent_name: Filter by agent name (optional)
            limit: Maximum number of decisions to return
        
        Returns:
            List of recent decisions
        """
        decisions = self.decision_history
        
        if agent_name:
            decisions = [d for d in decisions if d["agent_name"] == agent_name]
        
        return decisions[-limit:]


class BaseAgent:
    """
    Base class for all AI agents.
    
    Provides common functionality for agent operations including:
    - Overmind tracing
    - Memory management
    - LLM integration with real OpenAI calls
    """
    
    def __init__(
        self,
        name: str,
        overmind_tracer: OvermindTracer = None,
        llm_client: Any = None,
        cursor_composer: CursorComposerService = None,
    ):
        """
        Initialize base agent.
        
        Args:
            name: Agent name
            overmind_tracer: Overmind tracer instance
            llm_client: LLM client for inference
            cursor_composer: Cursor Composer 2.5 service (preferred when configured)
        """
        self.name = name
        self.overmind_tracer = overmind_tracer or OvermindTracer()
        self.memory = AgentMemory()
        self.cursor_composer = cursor_composer or CursorComposerService()

        # Initialize OpenAI client if not provided (fallback after Cursor)
        if llm_client is None and OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.llm_client = OpenAI(api_key=api_key)
            else:
                self.llm_client = None
        else:
            self.llm_client = llm_client
    
    async def think(
        self,
        prompt: str,
        context: Dict = None,
        temperature: float = 0.7
    ) -> str:
        """
        Core thinking method - uses LLM to process information.
        
        Args:
            prompt: Prompt for the LLM
            context: Additional context
            temperature: Sampling temperature
        
        Returns:
            LLM response
        """
        full_prompt = self._build_prompt(prompt, context)
        system_prompt = (
            f"You are {self.name}, an AI agent for autonomous media trading optimization "
            "on the SIGNAL platform. Provide concise, actionable analysis."
        )

        if self.cursor_composer.is_configured:
            try:
                return await self.cursor_composer.complete(
                    user_prompt=full_prompt,
                    system_prompt=system_prompt,
                )
            except Exception as e:
                print(f"❌ Cursor Composer call failed: {e}. Trying OpenAI fallback.")

        # Use OpenAI if Cursor unavailable
        if self.llm_client:
            try:
                response = self.llm_client.chat.completions.create(
                    model="gpt-4o-mini",  # Use cost-effective model
                    messages=[
                        {"role": "system", "content": f"You are {self.name}, an AI agent for media trading optimization."},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=500
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"❌ LLM call failed: {e}. Using fallback response.")
                return self._fallback_response(full_prompt)
        else:
            return self._fallback_response(full_prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """
        Generate fallback response when LLM is not available.
        
        Args:
            prompt: The original prompt
        
        Returns:
            Fallback response
        """
        return f"Agent {self.name} processed: {prompt[:100]}... (LLM not available, using fallback)"
    
    def _build_prompt(self, base_prompt: str, context: Dict = None) -> str:
        """
        Build full prompt with context.
        
        Args:
            base_prompt: Base prompt
            context: Additional context
        
        Returns:
            Full prompt
        """
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            return f"{base_prompt}\n\nContext:\n{context_str}"
        return base_prompt
    
    def decide(
        self,
        decision_type: str,
        options: List[str],
        context: Dict = None
    ) -> Dict:
        """
        Make a decision from available options.
        
        Args:
            decision_type: Type of decision
            options: Available options
            context: Decision context
        
        Returns:
            Decision result with reasoning
        """
        # Store decision context
        self.memory.store("current_context", context)
        self.memory.store("available_options", options)
        
        # Simple decision logic (would use LLM in production)
        selected_option = options[0] if options else None
        reasoning = f"Selected {selected_option} based on available options"
        
        # Record decision
        self.memory.record_decision(
            agent_name=self.name,
            decision=selected_option,
            reasoning=reasoning,
            context=context or {}
        )
        
        return {
            "decision": selected_option,
            "reasoning": reasoning,
            "agent": self.name,
            "timestamp": datetime.utcnow().isoformat()
        }