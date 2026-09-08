# AI Manufacturing Knowledge & Troubleshooting Copilot

An AI-powered engineering knowledge and troubleshooting assistant designed for industrial maintenance and automation teams.

> **Live Demo:**  
> 🚀 **[Launch AI Manufacturing Troubleshooting Copilot](https://ai-manufacturing-copilot-8yqrvjeqh4dcwoqvaaeyjn.streamlit.app/)**

The current MVP demonstrates an end-to-end Retrieval-Augmented Generation (RAG) workflow that retrieves relevant engineering knowledge from trusted technical documentation and generates grounded troubleshooting guidance with source-level evidence.

---

## 🎯 Problem

Industrial maintenance and automation engineers often spend significant time searching through technical manuals, troubleshooting guides, and equipment documentation when diagnosing faults or maintenance issues.

The goal of this project is to reduce that knowledge-search burden by providing an AI copilot that can quickly retrieve relevant engineering information and present it in a practical, evidence-backed format.

---

## 💡 Solution

The AI Manufacturing Knowledge & Troubleshooting Copilot connects trusted engineering documentation with:

- Document ingestion and cleaning
- Structure-aware document chunking
- Metadata-aware knowledge representation
- Hybrid keyword and semantic retrieval
- FAISS vector search
- Reciprocal Rank Fusion (RRF)
- Large Language Model (LLM) generation
- Evidence-backed troubleshooting responses
- Source and page-level traceability
- Human-in-the-loop safety controls

The system is designed to support engineers rather than replace engineering judgment.

---

## 🚀 Live Demo

### Try the Application

**[▶ Open Live Demo](https://ai-manufacturing-copilot-8yqrvjeqh4dcwoqvaaeyjn.streamlit.app/)**

The deployed Streamlit application demonstrates the complete troubleshooting workflow:

1. Submit a maintenance or troubleshooting question.
2. Retrieve relevant engineering evidence.
3. Generate a grounded AI response.
4. Review the supporting source documents and page references.

**Deployment:** Streamlit Community Cloud

**Current Knowledge Base:** Danfoss VLT AutomationDrive FC 302 Operating Guide

---

## 🏭 Initial MVP

**Equipment Domain:** Industrial Motor + VFD

**Current Equipment Knowledge Base:** Danfoss VLT AutomationDrive FC 302

The current MVP implements:

- Technical manual ingestion
- PDF text extraction and cleaning
- Structure-aware document chunking
- Section, subsection and subsubsection metadata
- Knowledge-base generation
- Semantic embeddings
- FAISS vector indexing
- Domain-aware keyword retrieval
- Semantic retrieval
- Hybrid retrieval using Reciprocal Rank Fusion (RRF)
- RAG-based answer generation
- Source/page traceability
- Safety-oriented response guardrails
- Streamlit web interface

---

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │        User          │
                    │ Maintenance Question│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Streamlit UI      │
                    │   Web Application    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      RAG Service      │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
       ┌─────────────────┐          ┌─────────────────┐
       │ Keyword Search  │          │ Semantic Search │
       │ Domain-Aware    │          │ Sentence        │
       │ Retrieval       │          │ Transformers    │
       └────────┬────────┘          └────────┬────────┘
                │                            │
                └──────────────┬─────────────┘
                               ▼
                    ┌──────────────────────┐
                    │ Reciprocal Rank     │
                    │ Fusion (RRF)        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Retrieved Evidence   │
                    │ + Metadata           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Groq LLM             │
                    │ Grounded Generation  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Engineering          │
                    │ Assessment           │
                    │ Causes                │
                    │ Troubleshooting      │
                    │ Safety                │
                    │ Evidence             │
                    └──────────────────────┘
