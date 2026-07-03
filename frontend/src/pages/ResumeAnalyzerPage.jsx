import { useEffect, useState } from "react";
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  List,
  ListItem,
  ListItemText,
  Chip,
  Stack,
  LinearProgress,
  Divider,
} from "@mui/material";
import { resumeApi } from "../api/endpoints";

export default function ResumeAnalyzerPage() {
  const [fileName, setFileName] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [resumes, setResumes] = useState([]);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState(null);

  const loadResumes = () => {
    resumeApi
      .list()
      .then((res) => {
        console.log("Resumes from backend:", res.data);
        setResumes(res.data);
      })
      .catch((err) => {
        console.error("Failed to load resumes:", err);
      });
  };

  useEffect(() => {
    loadResumes();
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const { data } = await resumeApi.upload({
        fileName,
        resumeText,
        jobDescription,
      });

      console.log("Uploaded Resume:", data);

      setResumes([data, ...resumes]);
      setFileName("");
      setResumeText("");
      setJobDescription("");
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || "Upload failed.");
    }
  };

  const handleAnalyze = async (id) => {
    console.log("Analyzing Resume ID:", id);

    setBusyId(id);
    setError("");

    try {
      const { data } = await resumeApi.analyze(id);

      console.log("Analysis Result:", data);

      setResumes(resumes.map((r) => (r.id === id ? data : r)));
      setSelected(data);
    } catch (err) {
      console.error("Analyze Error:", err.response || err);
      setError(
        err.response?.data?.message ||
          err.response?.data?.detail ||
          "Analysis failed — is ai-service running?"
      );
    } finally {
      setBusyId(null);
    }
  };

  return (
    <Box sx={{ p: 4, display: "flex", gap: 4, flexWrap: "wrap" }}>
      <Paper sx={{ p: 3, flex: "1 1 380px" }}>
        <Typography variant="h6" gutterBottom>
          Upload Resume
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleUpload}>
          <TextField
            label="File name"
            fullWidth
            margin="normal"
            required
            value={fileName}
            onChange={(e) => setFileName(e.target.value)}
          />

          <TextField
            label="Resume text"
            fullWidth
            margin="normal"
            required
            multiline
            minRows={5}
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
          />

          <TextField
            label="Job description (for ATS scoring)"
            fullWidth
            margin="normal"
            multiline
            minRows={4}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />

          <Button type="submit" variant="contained" sx={{ mt: 2 }}>
            Upload
          </Button>
        </form>

        <Divider sx={{ my: 3 }} />

        <Typography variant="h6" gutterBottom>
          Your Resumes
        </Typography>

        <List>
          {resumes.map((r) => (
            <ListItem
              key={r.id}
              divider
              secondaryAction={
                <Button
                  size="small"
                  disabled={busyId === r.id}
                  onClick={() => handleAnalyze(r.id)}
                >
                  {busyId === r.id ? "Analyzing..." : "Analyze"}
                </Button>
              }
              onClick={() => setSelected(r)}
              sx={{ cursor: "pointer" }}
            >
              <ListItemText
                primary={r.fileName}
                secondary={`${r.status}${
                  r.atsScore ? ` — ATS ${r.atsScore}` : ""
                }`}
              />
            </ListItem>
          ))}
        </List>
      </Paper>

      <Paper sx={{ p: 3, flex: "1 1 380px" }}>
        <Typography variant="h6" gutterBottom>
          Analysis
        </Typography>

        {!selected && (
          <Typography color="text.secondary">
            Select or analyze a resume to see results.
          </Typography>
        )}

        {selected && selected.status !== "ANALYZED" && (
          <Typography color="text.secondary">
            Not analyzed yet — click "Analyze" (requires a job description).
          </Typography>
        )}

        {selected && selected.status === "ANALYZED" && (
          <Box>
            <Typography variant="subtitle2">ATS Score</Typography>

            <LinearProgress
              variant="determinate"
              value={selected.atsScore}
              sx={{ height: 10, borderRadius: 5, mb: 1 }}
            />

            <Typography variant="h5" sx={{ mb: 2 }}>
              {selected.atsScore} / 100
            </Typography>

            <Typography variant="body2">
              Keyword match: {selected.keywordMatchScore}%
            </Typography>

            <Typography variant="body2" sx={{ mb: 2 }}>
              Semantic similarity: {selected.semanticSimilarityScore}%
            </Typography>

            <Typography variant="subtitle2">Matched skills</Typography>

            <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 2 }}>
              {selected.matchedSkills?.map((s) => (
                <Chip
                  key={s}
                  label={s}
                  color="success"
                  size="small"
                  sx={{ mb: 1 }}
                />
              ))}

              {selected.matchedSkills?.length === 0 && (
                <Typography color="text.secondary">None</Typography>
              )}
            </Stack>

            <Typography variant="subtitle2">Missing skills</Typography>

            <Stack direction="row" spacing={1} flexWrap="wrap">
              {selected.missingSkills?.map((s) => (
                <Chip
                  key={s}
                  label={s}
                  color="warning"
                  size="small"
                  sx={{ mb: 1 }}
                />
              ))}

              {selected.missingSkills?.length === 0 && (
                <Typography color="text.secondary">
                  None — great match!
                </Typography>
              )}
            </Stack>
          </Box>
        )}
      </Paper>
    </Box>
  );
}
