# FlowPulse Git Commit Guidelines

This project follows a consistent commit message format to keep the repository history clean and easy to understand.

## Commit Format

<module>: <clear action>

## Examples

models: implement Pydantic data contracts  
config: add YAML config loader with environment overrides  
logging: implement production logger with rotation  
utils: add string helper utilities  
io: implement CSV/JSON/YAML file handlers  
validation: add schema validation layer  
ingestion: implement event ingestion parser  
streaming: add Kafka producer for event pipeline  
warehouse: implement star schema tables  
analytics: add aggregation queries  
docs: update project documentation  
repo: update .gitignore

## Rules

1. Use lowercase module names.
2. Use a short action description after the colon.
3. Each commit should represent one logical change.
4. Keep commit messages concise and clear.
5. Tests should be included with feature commits whenever possible.

## Example Workflow

git add .
git commit -m "models: implement Pydantic data contracts"
git push origin main