"""Small checks on generated text before it becomes a PDF/DOCX."""
import ast
import re

FENCE = re.compile(r"```(?:python|py)\n(.*?)```", re.S)


def validate_generated(text):
    """Return (ok, problem_message)."""
    if not text or len(text.strip()) < 80:
        return False, "The answer is too short. Write a complete, well-structured document."
    for block in FENCE.findall(text):
        try:
            ast.parse(block)
        except SyntaxError as exc:
            return False, f"The Python code has a syntax error on line {exc.lineno}: {exc.msg}. Fix it."
    return True, ""
