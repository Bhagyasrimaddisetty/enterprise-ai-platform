import { useState } from "react";
import {
  Box, Paper, Typography, TextField, Button, Alert, List, ListItem,
  ListItemText, Chip, LinearProgress,
} from "@mui/material";
import { aiApi } from "../api/endpoints";

export default function InterviewPrepPage() {
  const [resumeText, setResumeText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [evaluations, setEvaluations] = useState({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const { data } = await aiApi.generateInterviewQuestions({
        resume_text: resumeText,
        job_description: jobDescription,
        experience_level: "fresher",
        question_types: ["technical", "hr", "behavioral"],
        count_per_type: 3,
      });
      setQuestions(data.questions);
      setAnswers({});
      setEvaluations({});
    } catch (err) {
      setError(err.response?.data?.detail || "Could not generate questions.");
    } finally {
      setBusy(false);
    }
  };

  const handleEvaluate = async (index, questionText) => {
    const answerText = answers[index];
    if (!answerText?.trim()) return;
    try {
      const { data } = await aiApi.evaluateAnswer({ question: questionText, answer_text: answerText });
      setEvaluations({ ...evaluations, [index]: data });
    } catch (err) {
      setError(err.response?.data?.detail || "Evaluation failed.");
    }
  };

  return (
    <Box sx={{ p: 4 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Generate Interview Questions</Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <form onSubmit={handleGenerate}>
          <TextField label="Resume text" fullWidth margin="normal" multiline minRows={3} required
            value={resumeText} onChange={(e) => setResumeText(e.target.value)} />
          <TextField label="Job description" fullWidth margin="normal" multiline minRows={3} required
            value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} />
          <Button type="submit" variant="contained" sx={{ mt: 2 }} disabled={busy}>
            {busy ? "Generating..." : "Generate Questions"}
          </Button>
        </form>
      </Paper>

      {questions.map((q, i) => (
        <Paper key={i} sx={{ p: 3, mb: 2 }}>
          <Chip label={q.question_type} size="small" sx={{ mb: 1 }} />
          <Typography variant="subtitle1" gutterBottom>{q.question}</Typography>
          <TextField
            fullWidth multiline minRows={2} placeholder="Type your answer..."
            value={answers[i] || ""} onChange={(e) => setAnswers({ ...answers, [i]: e.target.value })}
          />
          <Button size="small" sx={{ mt: 1 }} onClick={() => handleEvaluate(i, q.question)}>
            Evaluate Answer
          </Button>
          {evaluations[i] && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2">Overall score: {evaluations[i].overall_score}/100</Typography>
              <LinearProgress variant="determinate" value={evaluations[i].overall_score} sx={{ height: 8, borderRadius: 4, my: 1 }} />
              <Typography variant="body2" color="text.secondary">{evaluations[i].feedback}</Typography>
            </Box>
          )}
        </Paper>
      ))}
    </Box>
  );
}
