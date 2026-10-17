# Flyo Travel Document Parser

Robust Python-based ingestion pipeline designed to extract and validate unstructured travel emails and booking confirmations safely.

## Architectural Highlights
- **Typed Schemas:** Uses Pydantic v2 to strictly validate flight segments, IATA codes, and pricing before database persistence.
- **Zero-Hallucination Guardrails:** Stops corrupted or unverified LLM extractions at the door.
- **Deterministic Regex Fallback:** Automatically falls back to high-performance regex pattern matching if primary structured extraction fails.
