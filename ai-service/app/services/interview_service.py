"""
Interview module.

Question generation defaults to a template engine driven by the skills
found in the resume/JD (via ResumeAnalyzer's skill extraction) — this is
deterministic and free, and is what actually runs in tests/CI without a key.
If an LLM is configured, questions are generated live instead and
`generated_by` reflects which path ran.

Answer evaluation combines:
  - technical_relevance_score: TF-IDF cosine similarity between the answer
    and the question (proxy for on-topic-ness — a real embedding model
    would do better, but this is honest about what it is).
  - clarity_score: heuristic on sentence length / filler-word density.
  - grammar_issues: a small set of common rule-based checks (double
    spaces, repeated words, missing capitalization) — NOT a full grammar
    model. If you want proper grammar checking, that's a genuine gap to
    flag rather than dress up as AI-graded.
"""
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.schemas.schemas import InterviewAnswerEvaluationResponse, InterviewQuestion
from app.services.llm_client import LLMClient, LLMUnavailableError
from app.services.resume_analyzer import ResumeAnalyzer

_TEMPLATES = {
    "technical": [
        "Explain how you used {skill} in a project you've built.",
        "What are the main trade-offs of {skill} compared to alternatives you know?",
        "Walk me through how {skill} fits into the overall architecture of one of your projects.",
        "What's a bug or limitation you ran into while working with {skill}, and how did you resolve it?",
    ],
    "hr": [
        "Why are you interested in this role?",
        "Where do you see yourself in the next two years?",
        "What's a strength you'd bring to this team, and where are you still growing?",
        "How do you prioritize when you have multiple deadlines at once?",
    ],
    "behavioral": [
        "Tell me about a time you disagreed with a teammate's technical decision. What did you do?",
        "Describe a project that didn't go as planned. What did you learn?",
        "Tell me about a time you had to learn something new quickly to finish a task.",
        "Describe how you handled feedback that was hard to hear.",
    ],
    "coding": [
        "How would you approach optimizing a slow database query in {skill}?",
        "Write pseudocode for validating and sanitizing user input in a {skill} REST endpoint.",
    ],
}


class InterviewService:
    def __init__(self, resume_analyzer: ResumeAnalyzer | None = None, llm: LLMClient | None = None):
        self.resume_analyzer = resume_analyzer or ResumeAnalyzer()
        self.llm = llm or LLMClient()

    def _template_questions(
        self, resume_text: str, job_description: str, question_types: list[str], count_per_type: int
    ) -> list[InterviewQuestion]:
        skills = sorted(self.resume_analyzer._extract_skills(resume_text) & self.resume_analyzer._extract_skills(job_description))
        if not skills:
            skills = sorted(self.resume_analyzer._extract_skills(resume_text))[:5] or ["your core stack"]

        questions: list[InterviewQuestion] = []
        for qtype in question_types:
            templates = _TEMPLATES.get(qtype, _TEMPLATES["hr"])
            for i in range(count_per_type):
                template = templates[i % len(templates)]
                if "{skill}" in template:
                    skill = skills[i % len(skills)]
                    text = template.format(skill=skill)
                else:
                    text = template
                questions.append(InterviewQuestion(question_type=qtype, question=text))
        return questions

    async def generate_questions(
        self, resume_text: str, job_description: str, experience_level: str,
        question_types: list[str], count_per_type: int,
    ) -> tuple[list[InterviewQuestion], str]:
        if self.llm.is_available:
            try:
                skills = sorted(self.resume_analyzer._extract_skills(resume_text))
                prompt = (
                    f"Generate {count_per_type} interview questions for each of these types: "
                    f"{', '.join(question_types)}. Candidate experience level: {experience_level}. "
                    f"Candidate's key skills: {', '.join(skills[:15])}. "
                    f"Job description:\n{job_description[:1500]}\n\n"
                    "Return one question per line, prefixed with the type in brackets, e.g. "
                    "[technical] question text"
                )
                raw = await self.llm.generate(prompt, max_tokens=800)
                parsed = self._parse_llm_questions(raw)
                if parsed:
                    return parsed, "llm"
            except LLMUnavailableError:
                pass
        return self._template_questions(resume_text, job_description, question_types, count_per_type), "template_engine"

    @staticmethod
    def _parse_llm_questions(raw: str) -> list[InterviewQuestion]:
        questions = []
        for line in raw.splitlines():
            match = re.match(r"\s*\[(\w+)\]\s*(.+)", line)
            if match:
                questions.append(InterviewQuestion(question_type=match.group(1).lower(), question=match.group(2).strip()))
        return questions

    @staticmethod
    def _grammar_issues(text: str) -> list[str]:
        issues = []
        if "  " in text:
            issues.append("Double spaces detected.")
        if re.search(r"\b(\w+)\s+\1\b", text, flags=re.IGNORECASE):
            issues.append("Repeated word detected.")
        if text and not text[0].isupper():
            issues.append("Answer should start with a capital letter.")
        if text and text.strip()[-1] not in ".!?":
            issues.append("Answer should end with sentence-ending punctuation.")
        return issues

    def evaluate_answer(self, question: str, answer_text: str) -> InterviewAnswerEvaluationResponse:
        vectorizer = TfidfVectorizer(stop_words="english")
        try:
            matrix = vectorizer.fit_transform([question, answer_text])
            relevance = round(float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0]) * 100, 2)
        except ValueError:
            relevance = 0.0

        words = answer_text.split()
        word_count = len(words)
        filler_words = {"um", "uh", "like", "actually", "basically", "literally"}
        filler_count = sum(1 for w in words if w.lower().strip(".,") in filler_words)
        filler_ratio = filler_count / word_count if word_count else 1.0

        clarity = 100.0
        if word_count < 15:
            clarity -= 25  # too short to be a complete answer
        if word_count > 250:
            clarity -= 10  # rambling
        clarity -= min(filler_ratio * 200, 40)
        clarity = max(0.0, round(clarity, 2))

        grammar_issues = self._grammar_issues(answer_text)
        grammar_penalty = min(len(grammar_issues) * 5, 20)

        overall = round((relevance * 0.5 + clarity * 0.4) - grammar_penalty, 2)
        overall = max(0.0, min(100.0, overall))

        feedback_parts = []
        if relevance < 40:
            feedback_parts.append("Answer doesn't closely address the question asked — try to reference the question's key terms.")
        if word_count < 15:
            feedback_parts.append("Answer is quite short — expand with a concrete example.")
        if grammar_issues:
            feedback_parts.append("Minor writing issues: " + "; ".join(grammar_issues))
        if not feedback_parts:
            feedback_parts.append("Solid, relevant, well-formed answer.")

        return InterviewAnswerEvaluationResponse(
            technical_relevance_score=relevance,
            clarity_score=clarity,
            grammar_issues=grammar_issues,
            overall_score=overall,
            feedback=" ".join(feedback_parts),
        )
