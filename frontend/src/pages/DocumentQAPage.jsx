import { useState } from "react";
import { Box, Paper, Typography, Button, TextField, Alert, List, ListItem, ListItemText, Chip } from "@mui/material";
import { aiApi } from "../api/endpoints";

export default function DocumentQAPage() {
  const [file, setFile] = useState(null);
  const [document, setDocument] = useState(null);
  const [question, setQuestion] = useState("");
  const [conversation, setConversation] = useState([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const handleIngest = async () => {
    if (!file) return;
    setError("");
    setBusy(true);
    try {
      const { data } = await aiApi.ingestDocument(file);
      setDocument(data);
      setConversation([]);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not ingest document.");
    } finally {
      setBusy(false);
    }
  };

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!document || !question.trim()) return;
    setError("");
    setBusy(true);
    try {
      const { data } = await aiApi.queryDocument({ document_id: document.document_id, question });
      setConversation([...conversation, { question, answer: data.answer, llmGenerated: data.llm_generated }]);
      setQuestion("");
    } catch (err) {
      setError(err.response?.data?.detail || "Query failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Box sx={{ p: 4, display: "flex", gap: 4, flexWrap: "wrap" }}>
      <Paper sx={{ p: 3, flex: "1 1 320px" }}>
        <Typography variant="h6" gutterBottom>Upload Document</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Upload a PDF or text file, then ask questions about it (RAG search over the document).
        </Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <input type="file" accept=".pdf,.txt" onChange={(e) => setFile(e.target.files[0])} />
        <Button variant="contained" sx={{ mt: 2, display: "block" }} disabled={!file || busy} onClick={handleIngest}>
          {busy ? "Processing..." : "Ingest Document"}
        </Button>
        {document && (
          <Box sx={{ mt: 2 }}>
            <Chip label={`${document.filename} — ${document.chunk_count} chunks indexed`} color="success" />
          </Box>
        )}
      </Paper>

      <Paper sx={{ p: 3, flex: "2 1 480px" }}>
        <Typography variant="h6" gutterBottom>Ask Questions</Typography>
        <List>
          {conversation.map((turn, i) => (
            <ListItem key={i} alignItems="flex-start" divider>
              <ListItemText
                primary={`Q: ${turn.question}`}
                secondary={
                  <>
                    {turn.answer}
                    {!turn.llmGenerated && (
                      <Typography variant="caption" display="block" color="text.secondary">
                        (extractive match — configure an LLM provider for generated answers)
                      </Typography>
                    )}
                  </>
                }
              />
            </ListItem>
          ))}
          {conversation.length === 0 && <Typography color="text.secondary">No questions asked yet.</Typography>}
        </List>
        <form onSubmit={handleAsk}>
          <TextField
            fullWidth label="Ask a question about the document" value={question}
            onChange={(e) => setQuestion(e.target.value)} disabled={!document} sx={{ mt: 2 }}
          />
          <Button type="submit" variant="contained" sx={{ mt: 2 }} disabled={!document || busy}>
            {busy ? "Thinking..." : "Ask"}
          </Button>
        </form>
      </Paper>
    </Box>
  );
}
