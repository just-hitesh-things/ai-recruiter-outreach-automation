# AI Recruiter Outreach Automation

An event-driven automation platform built with FastAPI, n8n, PostgreSQL, and Gemini API to automate personalized technical recruiter outreach and delivery tracking.

## System Architecture

```text
[Recruiter Data / Leads]
        │
        ▼
   [PostgreSQL] ◄── (Database Layer: Logs, Tracking, Leads)
        ▲
        │
     [n8n] ◄────── (Automation & Event Dispatcher)
        │
        ▼
 [FastAPI Service] ──► [Gemini 1.5 Pro / Flash] (Custom Context Personalization)
        │
        ▼
 [SMTP / Mail Provider] ──► [Delivery Tracking / Webhooks]