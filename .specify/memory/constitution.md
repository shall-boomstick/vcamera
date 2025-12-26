<!--
Sync Impact Report:
Version change: N/A → 1.0.0 (initial constitution)
Modified principles: N/A (new constitution)
Added sections: Core Principles, Development Environment, Governance
Removed sections: N/A
Templates requiring updates:
  ✅ .specify/templates/plan-template.md - Constitution Check section aligns with KISS principle
  ✅ .specify/templates/spec-template.md - No changes needed, already flexible
  ✅ .specify/templates/tasks-template.md - No changes needed, already supports simple workflows
Follow-up TODOs: None
-->

# vcamera Constitution

## Core Principles

### I. KISS (Keep It Simple, Stupid) - PRIMARY PRINCIPLE

Simplicity is the highest priority. Every design decision MUST favor the simplest solution that works. Avoid over-engineering, premature optimization, and unnecessary abstractions. If a feature doesn't directly solve the problem at hand, it doesn't belong. The goal is a working application, not enterprise-grade architecture.

**Rationale**: This project prioritizes functionality over formality. Complex solutions introduce maintenance burden and slow development. Simple code is easier to understand, debug, and modify.

### II. Python Web Application

The application MUST be built in Python with a web-based user interface. Choose the simplest web framework that meets the requirements. Prefer widely-adopted libraries with minimal dependencies. The web interface should be functional and intuitive, not necessarily polished or feature-rich.

**Rationale**: Python provides rapid development and a rich ecosystem. A web interface makes the application accessible across all platforms without requiring platform-specific GUI dependencies. This improves cross-platform compatibility and accessibility.

### III. Virtual Environment Isolation

ALL dependencies and the application runtime MUST operate within a Python virtual environment (VENV). No system-wide Python packages should be required. The VENV setup MUST be documented and reproducible.

**Rationale**: VENV isolation prevents dependency conflicts, ensures consistent environments across different machines, and simplifies deployment. This is a minimal requirement for maintainability.

## Development Environment

### Virtual Environment Setup

- Create VENV: `python3 -m venv venv`
- Activate VENV: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt`
- All development and execution MUST occur within the activated VENV

### Dependency Management

- Use `requirements.txt` for dependency tracking
- Keep dependencies minimal - only include what is necessary
- Document any non-standard setup steps in project README

## Governance

This constitution supersedes all other development practices. When in doubt, choose the simpler option.

**Amendment Procedure**: Update this document with version bump (MAJOR.MINOR.PATCH):

- MAJOR: Backward incompatible principle changes
- MINOR: New principles or significant additions
- PATCH: Clarifications and wording improvements

**Compliance**: All implementation plans and feature specifications MUST verify alignment with these principles, especially KISS. If complexity is necessary, it MUST be justified in the plan's Complexity Tracking section.

**Version**: 1.0.0 | **Ratified**: 2025-12-22 | **Last Amended**: 2025-12-22
