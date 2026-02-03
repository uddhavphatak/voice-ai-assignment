"""
Real-Time Insight Detection Module

Implement your insight extraction logic here.

Requirements:
- Generate rolling summaries as transcript chunks arrive
- Detect key financial signals:
  - Revenue mentions
  - Guidance (forward-looking statements)
  - Risks and challenges
  - Outlook and projections
- Insights should update continuously, not just at the end

Suggested Approaches:
- LLM-based extraction (OpenAI, Anthropic, Google)
- Rule-based keyword extraction as fallback
- Hybrid: rules for speed, LLM for quality
"""
import json
import logging
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import List, Optional

from openai import AsyncOpenAI

from src.transcription.transcriber import TranscriptChunk

logger = logging.getLogger(__name__)

class InsightType(Enum):
    """Types of financial insights to detect."""
    
    REVENUE = "revenue"
    GUIDANCE = "guidance"
    RISK = "risk"
    OUTLOOK = "outlook"
    GROWTH = "growth"
    MARGIN = "margin"
    MARKET_SHARE = "market_share"
    COMPETITION = "competition"
    REGULATION = "regulation"
    OTHER = "other"


class Sentiment(Enum):
    """Sentiment classification for insights."""
    
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class Insight:
    """Represents a detected insight."""
    
    type: InsightType
    text: str
    confidence: float = 1.0
    sentiment: Sentiment = Sentiment.NEUTRAL
    
    # Source information
    source_text: str = ""
    timestamp: float = 0.0


@dataclass
class InsightResult:
    """Result of insight detection for a transcript chunk."""
    
    # The transcript chunk that was analyzed
    chunk: TranscriptChunk
    
    # Detected insights
    insights: List[Insight] = field(default_factory=list)
    
    # Rolling summary (updated with each chunk)
    rolling_summary: str = ""
    
    # Key metrics mentioned
    metrics: dict = field(default_factory=dict)


class InsightDetector:
    """
    Real-time insight detection from transcript chunks.
    
    TODO: Implement this class with your chosen approach.
    
    Example usage:
        detector = InsightDetector()
        
        async for chunk in transcriber.process_audio(audio_path):
            result = await detector.analyze(chunk)
            print(f"Summary: {result.rolling_summary}")
            for insight in result.insights:
                print(f"  [{insight.type.value}] {insight.text}")
    """
    
    def __init__(self, use_llm: bool = True):
        """
        Initialize the insight detector.
        
        Args:
            use_llm: Whether to use LLM for insight extraction
        """
        self.use_llm = use_llm
        self.conversation_history: List[TranscriptChunk] = []
        self.all_insights: List[Insight] = []
        self.current_summary: str = ""
        
        # TODO: Initialize your LLM client if using one
        # Example with OpenAI:
        # from openai import OpenAI
        # self.client = OpenAI()
        if self.use_llm:
            self.client = AsyncOpenAI()
        
    async def analyze(self, chunk: TranscriptChunk) -> InsightResult:
        """
        Analyze a transcript chunk and extract insights.
        
        Args:
            chunk: The transcript chunk to analyze
            
        Returns:
            InsightResult with detected insights and updated summary
        """
        # Track conversation history
        self.conversation_history.append(chunk)
        
        # TODO: Implement insight detection
        # 
        # Suggested approach:
        # 1. Extract insights from the current chunk
        # 2. Update the rolling summary with new information
        # 3. Detect any financial signals
        #
        # Example with LLM:
        #
        # prompt = self._build_prompt(chunk)
        # response = await self._call_llm(prompt)
        # insights = self._parse_insights(response)
        # 
        # return InsightResult(
        #     chunk=chunk,
        #     insights=insights,
        #     rolling_summary=self._update_summary(chunk),
        # )

        current_insights = []

        if self.use_llm:
            try:
                prompt = self._build_prompt(chunk)
                response = await self._call_llm(prompt)

                # Parse the LLM JSON response
                data = json.loads(response)

                # Update rolling summary with new information
                self.current_summary = data.get("rolling_summary", self.current_summary)

                # Process insights
                for item in data.get("insights", []):
                    insight = Insight(
                        type=InsightType(item.get("type", "other")),
                        text=item.get("text", ""),
                        sentiment=Sentiment(item.get("sentiment", "neutral")),
                        source_text=chunk.text,
                        timestamp=chunk.start_time
                    )
                    current_insights.append(insight)
                    self.all_insights.append(insight)

            except Exception as e:
                logger.error(f"LLM insight extraction failed: {e}")
                # Fallback to rule-based extraction
                current_insights = self._extract_insights_rule_based(chunk)
        else:
            current_insights = self._extract_insights_rule_based(chunk)

        return InsightResult(
            chunk=chunk,
            insights=current_insights,
            rolling_summary=self.current_summary,
        )
    
    def _build_prompt(self, chunk: TranscriptChunk) -> str:
        """Build the prompt for LLM-based insight extraction."""
        # TODO: Design your prompt for effective insight extraction
        # 
        # Consider including:
        # - Context about Indian earnings calls
        # - The transcript history so far
        # - Clear instructions for what to extract
        # - Output format specification
        recent_context = " ".join([c.text for c in self.conversation_history[-3:-1]])
        
        prompt = f"""
        Analyze this transcript chunk from an Indian earnings call:
        
        "{chunk.text}"
        
        Extract:
        1. Any mentions of revenue, growth, or financial metrics
        2. Forward-looking guidance or projections
        3. Risks or challenges mentioned
        4. Overall sentiment
        
        Also provide a brief summary update.
        """
        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM API for insight extraction."""
        # TODO: Implement LLM API call
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a financial analyst extracting insights from earnings calls."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    
    def _extract_insights_rule_based(self, chunk: TranscriptChunk) -> List[Insight]:
        """
        Fallback rule-based insight extraction.
        
        Use this as a simple baseline or fallback when LLM is not available.
        
        TODO: Implement your own keyword/pattern detection logic here.
        Consider detecting:
        - Financial metrics (revenue, margins, growth)
        - Forward-looking statements (guidance, outlook)
        - Risk indicators
        - Sentiment signals
        """
        # TODO: Implement rule-based extraction
        insights = []
        text_lower = chunk.text.lower()

        # Simple keyword map for demonstration
        mapping = {
            "revenue": InsightType.REVENUE,
            "guidance": InsightType.GUIDANCE,
            "risk": InsightType.RISK,
            "outlook": InsightType.OUTLOOK,
            "ebitda": InsightType.MARGIN
        }

        for keyword, insight_type in mapping.items():
            if keyword in text_lower:
                insights.append(Insight(
                    type=insight_type,
                    text=f"Detected mention of {keyword}",
                    source_text=chunk.text,
                    timestamp=chunk.start_time
                ))
        return insights

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM API."""
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    
    async def get_final_summary(self) -> str:
        """
        Generate a final summary of the entire call.
        
        Call this after processing all chunks.
        """
        # TODO: Implement final summary generation
        full_text = " ".join([c.text for c in self.conversation_history])
        prompt = f"Provide a final, detailed summary of this earnings call transcript: {full_text}"
        return await self._call_llm(prompt)
    
    def get_key_insights(self) -> List[Insight]:
        """Get the most important insights detected so far."""
        return self.all_insights
