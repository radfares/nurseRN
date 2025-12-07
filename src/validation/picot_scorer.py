"""
PICOT Quality Scorer

Scores PICOT questions using GPT-4 and SMART criteria rubric.

Features:
- Automated scoring with GPT-4 (temperature=0 for consistency)
- Breakdown by category (Specificity, Measurability, Achievability, Relevance, Time-Bound)
- Actionable improvement suggestions
- Grade assignment (Excellent/Good/Fair/Poor)

Part of Phase 5: Task 19.2
"""

import json
import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class PICOTScoreResult:
    """
    Result of PICOT quality scoring.

    Attributes:
        overall_score: Total score (0-100)
        specificity_score: Specificity category score (0-25)
        measurability_score: Measurability category score (0-20)
        achievability_score: Achievability category score (0-20)
        relevance_score: Relevance category score (0-20)
        timebound_score: Time-Bound category score (0-15)
        feedback: Actionable improvement suggestions
        grade: Overall grade (Excellent/Good/Fair/Poor)
    """
    overall_score: int
    specificity_score: int
    measurability_score: int
    achievability_score: int
    relevance_score: int
    timebound_score: int
    feedback: str
    grade: str

    def __post_init__(self):
        """Validate and clamp scores to valid ranges."""
        # Clamp overall score
        self.overall_score = max(0, min(100, self.overall_score))

        # Clamp category scores
        self.specificity_score = max(0, min(25, self.specificity_score))
        self.measurability_score = max(0, min(20, self.measurability_score))
        self.achievability_score = max(0, min(20, self.achievability_score))
        self.relevance_score = max(0, min(20, self.relevance_score))
        self.timebound_score = max(0, min(15, self.timebound_score))


class PICOTScorer:
    """
    Scores PICOT questions using GPT-4 and SMART criteria.

    Uses temperature=0 for consistent scoring across runs.
    """

    def __init__(self):
        """Initialize scorer with rubric."""
        self.rubric_path = Path(__file__).parent / "PICOT_RUBRIC.md"
        self._rubric_content = self._load_rubric()

    def _load_rubric(self) -> str:
        """Load scoring rubric from file."""
        if self.rubric_path.exists():
            with open(self.rubric_path, 'r') as f:
                return f.read()
        else:
            # Fallback if rubric file not found
            return "Score PICOT questions on SMART criteria (0-100 scale)"

    def score(self, picot_question: str) -> PICOTScoreResult:
        """
        Score a PICOT question using GPT-4.

        Args:
            picot_question: The PICOT question to score

        Returns:
            PICOTScoreResult with scores and feedback
        """
        try:
            # Import here to avoid circular imports and allow mocking
            from agno.agent import Agent
            from agno.models.openai import OpenAIChat

            # Create scoring agent with temperature=0 for consistency
            agent = Agent(
                model=OpenAIChat(
                    id="gpt-4o",
                    temperature=0.0  # Consistency requirement
                ),
                instructions=self._get_scoring_instructions(),
                markdown=False
            )

            # Score the PICOT
            query = f"""Score this PICOT question according to the rubric:

PICOT: {picot_question}

Return ONLY valid JSON with these exact keys:
- overall_score (0-100)
- specificity_score (0-25)
- measurability_score (0-20)
- achievability_score (0-20)
- relevance_score (0-20)
- timebound_score (0-15)
- feedback (string with improvement suggestions)
- grade (Excellent/Good/Fair/Poor)
"""

            response = agent.run(query)
            result_json = self._parse_response(response.content)

            return PICOTScoreResult(
                overall_score=result_json.get("overall_score", 0),
                specificity_score=result_json.get("specificity_score", 0),
                measurability_score=result_json.get("measurability_score", 0),
                achievability_score=result_json.get("achievability_score", 0),
                relevance_score=result_json.get("relevance_score", 0),
                timebound_score=result_json.get("timebound_score", 0),
                feedback=result_json.get("feedback", "Unable to generate feedback"),
                grade=result_json.get("grade", "Unknown")
            )

        except Exception as e:
            # Graceful fallback on error
            return PICOTScoreResult(
                overall_score=0,
                specificity_score=0,
                measurability_score=0,
                achievability_score=0,
                relevance_score=0,
                timebound_score=0,
                feedback=f"Scoring error: {str(e)}",
                grade="Error"
            )

    def _get_scoring_instructions(self) -> str:
        """Get system instructions for scoring agent."""
        return f"""You are a PICOT quality scorer for nursing QI projects.

{self._rubric_content}

Your task:
1. Score the PICOT question according to the rubric above
2. Provide specific, actionable feedback for improvement
3. Assign a grade based on the total score

Return results as valid JSON only, no markdown formatting.
"""

    def _parse_response(self, response_text: str) -> dict:
        """
        Parse GPT-4 response to extract JSON.

        Args:
            response_text: Raw response from GPT-4

        Returns:
            Dictionary with score data
        """
        try:
            # Try to parse as JSON directly
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
                return json.loads(json_str)
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
                return json.loads(json_str)
            else:
                # Try to find JSON object in text
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = response_text[start:end]
                    return json.loads(json_str)

            # If all parsing fails, return default
            raise ValueError("Could not parse JSON from response")
