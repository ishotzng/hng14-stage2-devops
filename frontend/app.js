const express = require("express");
const axios = require("axios");
const cookieParser = require("cookie-parser");
const csrf = require("csurf");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;
const API_URL = process.env.API_URL || "http://localhost:8000";

const JOB_ID_REGEX = /^[0-9a-f-]{36}$/;

app.use(express.json());
app.use(cookieParser());
app.use(csrf({ cookie: true }));
app.use(express.static(path.join(__dirname, "views")));

app.get("/csrf-token", (req, res) => {
    res.json({ csrfToken: req.csrfToken() });
});

app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "views", "index.html"));
});

app.post("/submit", async (req, res) => {
    try {
        const response = await axios.post(`${API_URL}/jobs`);
        res.json(response.data);
    } catch (err) {
        res.status(500).json({ error: "Failed to submit job" });
    }
});

app.get("/jobs/:id", async (req, res) => {
    if (!JOB_ID_REGEX.test(req.params.id)) {
        return res.status(400).json({ error: "invalid job id" });
    }
    try {
        const response = await axios.get(`${API_URL}/jobs/${req.params.id}`);
        res.json(response.data);
    } catch (err) {
        if (err.response && err.response.status === 404) {
            return res.status(404).json({ error: "job not found" });
        }
        res.status(500).json({ error: "Failed to get job status" });
    }
});

app.listen(PORT, () => {
    console.log(`Frontend running on port ${PORT}`);
});