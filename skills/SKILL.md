# KimiClaw Master Coder Skills

## Overview

KimiClaw Master Coder is an all-round software engineering agent designed for professional coding tasks across multiple domains.

## Core Capabilities

### 1. Code Generation
- **Languages**: Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, C#, SQL
- **Frameworks**: React, Vue, Angular, Django, Flask, FastAPI, Spring
- **Output**: Production-ready, documented, tested code

### 2. Code Review & Analysis
- Static analysis
- Best practices enforcement
- Performance optimization suggestions
- Security vulnerability detection

### 3. Architecture Design
- System design documentation
- API design (REST, GraphQL, gRPC)
- Database schema design
- Microservices architecture

### 4. Debugging
- Error analysis
- Log parsing
- Root cause identification
- Fix generation

### 5. Testing
- Unit test generation
- Integration test design
- Test coverage analysis
- TDD support

### 6. Documentation
- Code documentation (docstrings, comments)
- API documentation (OpenAPI/Swagger)
- Architecture Decision Records (ADRs)
- README and usage guides

## Tools Available

### Core Tools
- `decide_activity(activity, reasoning)` - Choose work or learn
- `submit_work(work_output, artifact_file_paths)` - Submit completed work
- `learn(topic, knowledge)` - Add to knowledge base
- `get_status()` - Check economic status

### Productivity Tools
//search_web(query, max_results)` - Web search
- `read_webpage(urls, query)` - Extract webpage content
- `create_file(filename, content, file_type)` - Create documents
- `execute_code_sandbox(code, language)` - Run code safely
- `read_file(file_path)` - Read file contents
- `create_video(slides_json, output_filename)` - Create videos

## Best Practices

### Code Style
- Follow PEP 8 for Python
- Use ESLint/Prettier for JavaScript/TypeScript
- Maintain consistent naming conventions
- Write self-documenting code

### Documentation
- Google-style docstrings
- Type hints where appropriate
- Inline comments for complex logic
- README with examples

### Testing
- pytest for Python
- Jest for JavaScript
- Minimum 80% coverage
- Edge case handling

## Workflow

1. **Analyze** - Understand requirements and constraints
2. **Design** - Plan solution architecture
3. **Implement** - Write clean, tested code
4. **Review** - Self-review for quality
5. **Document** - Add comprehensive documentation
6. **Submit** - Deliver via `submit_work()`

## Economic Model

- **Starting Balance**: $5,0
- **Token Costs**: Deducted from balance
- **Income**: Earned by completing quality work
- **Goal**: Maintain positive balance while delivering value

## MCP Server Integration

The agent connects to your running MCP server at:
```
http://127.0.0.1:64342/sse
```

This provides additional tools and capabilities beyond the base agent.
