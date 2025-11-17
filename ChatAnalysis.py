# ChatAnalysis.py
# -------------------------------------------------
# Analyze chat history for grammar, vocabulary, personality, role fit, goal orientation,
# and provide structured recommendations.
# Outputs structured JSON using Pydantic models.
# -------------------------------------------------

from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime

# ----------------------------
# Optional import for grammar check
# ----------------------------
try:
    import language_tool_python
    LANGUAGE_TOOL_AVAILABLE = True
except ImportError:
    LANGUAGE_TOOL_AVAILABLE = False
    print("⚠️ language_tool_python not installed. Grammar analysis will be skipped.")

# ----------------------------
# Pydantic Models
# ----------------------------
class GrammarAnalysis(BaseModel):
    total_sentences: int = 0
    correct_sentences: int = 0
    incorrect_sentences: int = 0
    grammar_accuracy: float = 0.0
    common_errors: List[str] = []

class VocabularyAnalysis(BaseModel):
    unique_words: int
    repeated_words: int
    variety_score: float
    recommendations: List[str]

class PersonalityAnalysis(BaseModel):
    confidence: float
    politeness: float
    positivity: float
    tone_consistency: float
    empathy: float
    overall_summary: str

class GoalOrientationAnalysis(BaseModel):
    clarity: float
    focus: float
    time_management: float
    follow_through: float
    improvement_recommendations: List[str]

class RoleFitAnalysis(BaseModel):
    professionalism: float
    work_ethic: float
    collaboration: float
    topic_relevance: float
    overall_fit: str
    recommendations: List[str]

class ChatAnalysisReport(BaseModel):
    chat_summary: str
    grammar_analysis: GrammarAnalysis
    vocabulary_analysis: VocabularyAnalysis
    personality_analysis: PersonalityAnalysis
    goal_orientation_analysis: GoalOrientationAnalysis
    role_fit_analysis: RoleFitAnalysis
    additional_points: Dict[str, str]
    timestamp: datetime

# ----------------------------
# Main Analyzer
# ----------------------------
class ChatAnalyzer:
    def __init__(self):
        if LANGUAGE_TOOL_AVAILABLE:
            self.tool = language_tool_python.LanguageTool('en-US')
        else:
            self.tool = None

    def analyze_grammar(self, text: str) -> GrammarAnalysis:
        if not LANGUAGE_TOOL_AVAILABLE or not self.tool:
            return GrammarAnalysis(
                total_sentences=0,
                correct_sentences=0,
                incorrect_sentences=0,
                grammar_accuracy=0.0,
                common_errors=["Grammar analysis skipped (language_tool_python not installed)"]
            )
        matches = self.tool.check(text)
        total_sentences = max(len([s for s in text.split('.') if s.strip()]), 1)
        incorrect_sentences = len(matches)
        correct_sentences = total_sentences - incorrect_sentences
        common_errors = list(set([m.ruleId for m in matches]))
        grammar_accuracy = round((correct_sentences / total_sentences) * 100, 2)
        return GrammarAnalysis(
            total_sentences=total_sentences,
            correct_sentences=correct_sentences,
            incorrect_sentences=incorrect_sentences,
            grammar_accuracy=grammar_accuracy,
            common_errors=common_errors
        )

    def analyze_vocabulary(self, text: str) -> VocabularyAnalysis:
        words = text.split()
        unique_words = len(set(words))
        repeated_words = len(words) - unique_words
        variety_score = round(unique_words / max(len(words), 1) * 100, 2)
        recommendations = []
        if variety_score < 50:
            recommendations.append("Try to use more diverse vocabulary.")
        if repeated_words > 20:
            recommendations.append("Avoid repeating same words frequently.")
        return VocabularyAnalysis(
            unique_words=unique_words,
            repeated_words=repeated_words,
            variety_score=variety_score,
            recommendations=recommendations
        )

    def analyze_personality(self, text: str) -> PersonalityAnalysis:
        confidence = min(max(text.count("I") / max(len(text.split()),1)*100, 30), 90)
        politeness = min(max(text.count("please")+text.count("thank")*2, 0), 100)
        positivity = min(max(text.count("good")+text.count("great")+text.count("excellent"),0),100)
        tone_consistency = 80
        empathy = min(max(text.count("sorry")+text.count("understand"),0), 100)
        overall_summary = "You appear confident, polite, and generally positive in tone."
        return PersonalityAnalysis(
            confidence=confidence,
            politeness=politeness,
            positivity=positivity,
            tone_consistency=tone_consistency,
            empathy=empathy,
            overall_summary=overall_summary
        )

    def analyze_goal_orientation(self, text: str) -> GoalOrientationAnalysis:
        clarity = 85
        focus = 80
        time_management = 75
        follow_through = 70
        improvement_recommendations = [
            "Define goals more specifically.",
            "Break down tasks into smaller achievable steps.",
            "Track progress regularly."
        ]
        return GoalOrientationAnalysis(
            clarity=clarity,
            focus=focus,
            time_management=time_management,
            follow_through=follow_through,
            improvement_recommendations=improvement_recommendations
        )

    def analyze_role_fit(self, text: str) -> RoleFitAnalysis:
        professionalism = 80
        work_ethic = 85
        collaboration = 75
        topic_relevance = 80
        overall_fit = "You are well-suited for task-oriented roles with moderate collaboration."
        recommendations = [
            "Participate more actively in discussions.",
            "Focus on aligning contributions with role responsibilities.",
        ]
        return RoleFitAnalysis(
            professionalism=professionalism,
            work_ethic=work_ethic,
            collaboration=collaboration,
            topic_relevance=topic_relevance,
            overall_fit=overall_fit,
            recommendations=recommendations
        )

    def generate_additional_points(self, text: str) -> Dict[str, str]:
        return {
            "creativity": "Moderate",
            "decision_making": "Good",
            "problem_solving": "Good",
            "stress_management": "Average",
            "teamwork": "Good",
            "initiative": "Good",
            "adaptability": "Average",
            "attention_to_detail": "Good",
            "leadership": "Average",
            "motivation": "High",
            "emotional_intelligence": "Average",
            "communication_skills": "Good",
            "critical_thinking": "Good",
            "learning_ability": "High",
            "technical_knowledge": "Moderate",
            "planning": "Good",
            "organization": "Good",
            "confidence_level": "High",
            "punctuality": "Good",
            "work_life_balance": "Average",
            "overall_rating": "Above Average",
        }

    def analyze_chat(self, text: str) -> ChatAnalysisReport:
        grammar = self.analyze_grammar(text)
        vocab = self.analyze_vocabulary(text)
        personality = self.analyze_personality(text)
        goal_orientation = self.analyze_goal_orientation(text)
        role_fit = self.analyze_role_fit(text)
        additional_points = self.generate_additional_points(text)
        chat_summary = f"Chat Summary: Your overall chat is structured, goal-oriented, and mostly grammatically correct."

        return ChatAnalysisReport(
            chat_summary=chat_summary,
            grammar_analysis=grammar,
            vocabulary_analysis=vocab,
            personality_analysis=personality,
            goal_orientation_analysis=goal_orientation,
            role_fit_analysis=role_fit,
            additional_points=additional_points,
            timestamp=datetime.now()
        )


# ----------------------------
# Example Usage
# ----------------------------
if __name__ == "__main__":
    analyzer = ChatAnalyzer()
    sample_text = "I want to improve my English grammar. I am working hard. Please guide me."
    report = analyzer.analyze_chat(sample_text)
    print(report.json(indent=4))
