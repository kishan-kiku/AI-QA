from app.config import get_settings


def load_prompt(relative_path: str) -> str:
    """Load a prompt file from prompts/. Analog: a reusable test library, not a page object."""
    path = get_settings().prompts_dir / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")
