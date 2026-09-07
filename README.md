# AI Manufacturing Knowledge & Troubleshooting Copilot

An AI-powered engineering knowledge and troubleshooting assistant for industrial maintenance and automation teams.

## Vision

Help maintenance and automation engineers troubleshoot industrial equipment faster by connecting trusted engineering documentation with AI-powered retrieval and evidence-based guidance.

## Initial MVP

**Equipment:** Industrial Motor + VFD

The system will:

- Ingest technical manuals and SOPs
- Extract and clean document content
- Split documents into meaningful chunks
- Store document metadata
- Create searchable representations
- Retrieve relevant engineering knowledge
- Generate evidence-backed troubleshooting guidance
- Cite the source document and relevant section/page
- Ask clarification questions when required
- Escalate uncertain or safety-critical situations to a qualified human

## Initial Architecture

User
  |
Web Dashboard
  |
FastAPI Backend
  |
AI / RAG Layer
  |
Knowledge Base + Vector Database
  |
Technical Manuals / SOPs / Maintenance Records

## Development Principles

- Evidence over hallucination
- Human-in-the-loop for safety-critical decisions
- Source and revision traceability
- Evaluation before production deployment
- Modular architecture
- Production-oriented engineering

## Project Status

MVP - Under Development

## Roadmap

### Phase 1
Document ingestion and knowledge-base pipeline.

### Phase 2
RAG-powered troubleshooting assistant.

### Phase 3
Evaluation, guardrails, observability and production API.

### Phase 4
Maintenance history and structured equipment data.

### Phase 5
Bounded AI agents and workflow automation.

### Future
Sensor/IoT integration and ML-based anomaly detection.

## Safety

This system is designed as a decision-support copilot. It does not autonomously control physical industrial equipment. Final operational decisions remain with qualified personnel.
