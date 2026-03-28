# Ipê Specifications

This directory contains the complete technical specifications for Ipê, organized by domain. Each specification file focuses on a specific aspect of the system and serves as the definitive source of truth for that domain.

## Navigation Guide

| Spec | Domain | Description |
|------|---------|-------------|
| [01-project-overview.md](01-project-overview.md) | **Vision & Philosophy** | Core values, philosophy, and project identity |
| [02-architecture.md](02-architecture.md) | **System Design** | Pipeline architecture, target system, and data models |
| [03-cli-interface.md](03-cli-interface.md) | **User Interface** | CLI commands, options, and user experience |
| [04-configuration-system.md](04-configuration-system.md) | **Configuration** | Settings, schemas, and configuration management |
| [05-code-generation.md](05-code-generation.md) | **Generation Engine** | Code generation process, templates, and output |
| [06-openapi-support.md](06-openapi-support.md) | **OpenAPI Integration** | Specification parsing, validation, and support |
| [99-future-features.md](99-future-features.md) | **Future Roadmap** | Planned extensions and post-MVP features |

## Reading Guide

**For New Contributors**: Start with specs 01-03 to understand the project vision and user interface.

**For Implementers**: Focus on specs 02, 04-06 for core implementation details.

**For Target Authors**: Review specs 02 and 05 for the LanguageTarget protocol and generation process.

## Specification Standards

Each specification follows these conventions:
- **Single Domain**: Each spec covers one cohesive area of responsibility
- **Decision Record**: Documents not just what, but why decisions were made
- **Implementation Focused**: Provides concrete guidance for implementation
- **Cross-References**: Links to related specifications when needed
- **Status Tracking**: Indicates current implementation status

## Maintenance

When making architectural decisions or adding features:
1. Identify which specification(s) are affected
2. Update the relevant spec files with the decision and rationale
3. Ensure cross-references remain accurate
4. Update the development plan if milestones are affected