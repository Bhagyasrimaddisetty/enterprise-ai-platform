import { useState } from "react";
import { Box, Paper, TextField, Button, Typography, Alert, MenuItem, Link as MuiLink } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ROLES = ["CANDIDATE", "HR", "INTERVIEWER", "ADMIN"];

export default function RegisterPage() {
  const [form, setForm] = useState({ email: "", fullName: "", password: "", role: "CANDIDATE" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(form.email, form.fullName, form.password, form.role);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.message || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: "flex", justifyContent: "center", mt: 8 }}>
      <Paper sx={{ p: 4, width: 400 }} elevation={3}>
        <Typography variant="h5" gutterBottom>Create an account</Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <form onSubmit={handleSubmit}>
          <TextField label="Full name" fullWidth margin="normal" required
            value={form.fullName} onChange={update("fullName")} />
          <TextField label="Email" type="email" fullWidth margin="normal" required
            value={form.email} onChange={update("email")} />
          <TextField label="Password" type="password" fullWidth margin="normal" required
            helperText="At least 8 characters" value={form.password} onChange={update("password")} />
          <TextField select label="Role" fullWidth margin="normal" value={form.role} onChange={update("role")}>
            {ROLES.map((r) => <MenuItem key={r} value={r}>{r}</MenuItem>)}
          </TextField>
          <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }} disabled={loading}>
            {loading ? "Creating..." : "Register"}
          </Button>
        </form>
        <Typography variant="body2" sx={{ mt: 2 }}>
          Already have an account? <MuiLink component={Link} to="/login">Sign in</MuiLink>
        </Typography>
      </Paper>
    </Box>
  );
}
