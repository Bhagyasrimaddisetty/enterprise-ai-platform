import { useEffect, useState } from "react";
import { Box, Grid, Paper, Typography, CircularProgress, Alert } from "@mui/material";
import { resumeApi } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";

function StatCard({ label, value }) {
  return (
    <Paper sx={{ p: 3, textAlign: "center" }} elevation={2}>
      <Typography variant="h4">{value}</Typography>
      <Typography variant="body2" color="text.secondary">{label}</Typography>
    </Paper>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    resumeApi.list()
      .then((res) => setResumes(res.data))
      .catch(() => setError("Could not load resume data."))
      .finally(() => setLoading(false));
  }, []);

  const analyzed = resumes.filter((r) => r.status === "ANALYZED");
  const avgScore = analyzed.length
    ? (analyzed.reduce((sum, r) => sum + (r.atsScore || 0), 0) / analyzed.length).toFixed(1)
    : "—";

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>Welcome back, {user?.fullName}</Typography>
      {error && <Alert severity="warning" sx={{ mb: 2 }}>{error}</Alert>}
      {loading ? (
        <CircularProgress />
      ) : (
        <Grid container spacing={3}>
          <Grid item xs={12} sm={4}><StatCard label="Resumes uploaded" value={resumes.length} /></Grid>
          <Grid item xs={12} sm={4}><StatCard label="Analyzed" value={analyzed.length} /></Grid>
          <Grid item xs={12} sm={4}><StatCard label="Average ATS score" value={avgScore} /></Grid>
        </Grid>
      )}
      <Paper sx={{ mt: 4, p: 3 }}>
        <Typography variant="h6" gutterBottom>Recent Activity</Typography>
        {resumes.slice(0, 5).map((r) => (
          <Box key={r.id} sx={{ display: "flex", justifyContent: "space-between", py: 1, borderBottom: "1px solid #eee" }}>
            <Typography>{r.fileName}</Typography>
            <Typography color="text.secondary">{r.status}{r.atsScore ? ` — ATS ${r.atsScore}` : ""}</Typography>
          </Box>
        ))}
        {resumes.length === 0 && <Typography color="text.secondary">No resumes yet — upload one to get started.</Typography>}
      </Paper>
    </Box>
  );
}
