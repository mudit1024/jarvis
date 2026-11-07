# ADR-0001: React Native with Expo for the client, not Flutter

* **Status:** Accepted
* **Date:** 2026-11-07
* **Jira:** JAR-2

## Context
JARVIS needs one client codebase for Android, iOS, web and, later, desktop. The backend and the laptop device
agent are Python. The owner knows React and is learning Python and AI backend engineering, which is the
project's primary goal. Laptop control (media, volume, files) is done by the Python device agent, not by the UI,
so the client doesn't need deep desktop operating-system access.

## Options considered
1. **Flutter (Dart).** Excellent on mobile and desktop, one UI codebase. Cons: a second new language and
   ecosystem at the same time as Python, which takes time away from the primary learning goal.
2. **React Native with Expo (TypeScript).** Android, iOS and web from one project; reuses React knowledge;
   typed API client generated from FastAPI's OpenAPI spec. Cons: desktop needs the web build or a
   Tauri/Electron wrapper.

## Decision
React Native with Expo and TypeScript, using Expo Router. Desktop uses the web build (installable as a PWA),
with a Tauri wrapper only if a native window becomes necessary.

## Consequences
* One TypeScript client plus Python backend and agent; the API contract is shared through generated types.
* Learning effort stays focused on the Python and AI backend.
* Revisit only if the UI becomes heavily custom-drawn (where Flutter is stronger).
