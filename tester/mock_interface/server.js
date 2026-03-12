import express from "express";
import fetch from "node-fetch";
import path from "path";
import { fileURLToPath } from "url";

// Create app
const app = express();
app.use(express.json());


/**
 * Serve static website
 */
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
app.use(express.static(path.join(__dirname, "public")));



/**
 * SSE Setup
 */
// Store connected SSE clients
let clients = [];
// Endpoint
app.get("/events", (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("Access-Control-Allow-Origin", "*");

  // Flush headers immediately
  res.flushHeaders?.();

  const clientId = Date.now();
  const newClient = { id: clientId, res };

  clients.push(newClient);
  console.log(`SSE client connected: ${clientId}`);

  // Optional: send initial message
  res.write(`data: ${JSON.stringify({ status: "connected" })}\n\n`);

  // Remove client on disconnect
  req.on("close", () => {
    console.log(`SSE client disconnected: ${clientId}`);
    clients = clients.filter(client => client.id !== clientId);
  });

  // Optional: heartbeat to prevent proxy timeout
  setInterval(() => {
  clients.forEach(client => {
    client.res.write(":\n\n"); // comment heartbeat
  });
  }, 15000);

});

app.post("/callback", (req, res) => {
  const payload = req.body;

  console.log("Received callback:", payload);

  const data = JSON.stringify(payload);

  // Broadcast to all SSE clients
  clients.forEach(client => {
    client.res.write(`event: callback\n`); // Custom event type (optional definition)
    client.res.write(`data: ${data}\n\n`);
  });

  res.json({ status: "ok", deliveredTo: clients.length });
});


/**
 * Calling external services
 */
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


/**
 * Server startup
 */
app.listen(3001, () => console.log("Proxy running on 3001"));