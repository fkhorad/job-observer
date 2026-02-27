import express from "express";
import fetch from "node-fetch";
import path from "path";
import { fileURLToPath } from "url";

const app = express();
app.use(express.json());

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
app.use(express.static(path.join(__dirname, "public")));

const SERVICES = {
  "/api/first/job": "http://localhost:8001/job",
  "/api/second/job": "http://localhost:8002/job",
  "/api/add_job": "http://localhost:8000/add_job",
  "/api/job_status": "http://localhost:8000/job_status"
};

app.use("/api", async (req, res) => {
  try {
    // find which service matches
    const match = Object.keys(SERVICES).find(prefix =>
      req.originalUrl.startsWith(prefix)
    );

    if (!match) {
      return res.status(404).send("Unknown API route");
    }

    const targetBase = SERVICES[match];

    // remove local prefix when forwarding
    const forwardPath = req.originalUrl.replace(match, "");
    const url = targetBase + forwardPath;

    console.log("→ proxy:", req.method, url);

    const response = await fetch(url, {
      method: req.method,
      headers: {
        "Content-Type": "application/json",
        origin: targetBase,
      },
      body: ["GET", "HEAD"].includes(req.method)
        ? undefined
        : JSON.stringify(req.body),
    });

    const text = await response.text();
    res.status(response.status).send(text);

  } catch (e) {
    console.error(e);
    res.status(500).send("Proxy error");
  }
});

app.listen(3001, () => console.log("Proxy running on 3001"));