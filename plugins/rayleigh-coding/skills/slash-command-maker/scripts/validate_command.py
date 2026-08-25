#!/usr/bin/env python3
"""
Validate jarvis slash command files.

Checks:
- YAML frontmatter syntax
- Required fields (name, description)
- Naming conventions
- Example block structure
- File location
- Body content presence

Usage:
    python validate_command.py <path/to/command.md>
    python validate_command.py ~/jarvis/commands/  # Validate all commands
"""

import sys
import re
import yaml
from pathlib import Path
from typing import NamedTuple

class ValidationResult(NamedTuple):
    valid: bool
    errors: list[str]
    warnings: list[str]

def extract_frontmatter(content: str) -> tuple[dict | None, str, str | None]:
    """
    Extract YAML frontmatter from markdown content.
    Returns (frontmatter_dict, body, error_message).
    """
    if not content.startswith('---'):
        return None, content, "File must start with YAML frontmatter (---)"
    
    # Find closing ---
    lines = content.split('\n')
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_idx = i
            break
    
    if end_idx is None:
        return None, content, "No closing --- found for frontmatter"
    
    frontmatter_text = '\n'.join(lines[1:end_idx])
    body = '\n'.join(lines[end_idx + 1:])
    
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return None, body, "Frontmatter must be a YAML dictionary"
        return frontmatter, body, None
    except yaml.YAMLError as e:
        return None, body, f"Invalid YAML in frontmatter: {e}"

def validate_name(name: str | None) -> list[str]:
    """Validate the command name field."""
    errors = []
    
    if not name:
        errors.append("Missing required field: name")
        return errors
    
    if not isinstance(name, str):
        errors.append(f"Name must be a string, got {type(name).__name__}")
        return errors
    
    # Check format: lowercase, hyphenated, no spaces
    if name != name.lower():
        errors.append(f"Name must be lowercase: '{name}' → '{name.lower()}'")
    
    if ' ' in name:
        errors.append(f"Name cannot contain spaces: '{name}'")
    
    if '_' in name:
        errors.append(f"Name should use hyphens, not underscores: '{name}'")
    
    if not re.match(r'^[a-z][a-z0-9-]*$', name):
        errors.append(f"Name must start with letter, contain only lowercase letters, numbers, and hyphens: '{name}'")
    
    if len(name) < 2:
        errors.append(f"Name too short (min 2 chars): '{name}'")
    
    if len(name) > 30:
        errors.append(f"Name too long (max 30 chars): '{name}' ({len(name)} chars)")
    
    return errors

def validate_description(description: str | None) -> tuple[list[str], list[str]]:
    """Validate the description field. Returns (errors, warnings)."""
    errors = []
    warnings = []
    
    if not description:
        errors.append("Missing required field: description")
        return errors, warnings
    
    if not isinstance(description, str):
        errors.append(f"Description must be a string, got {type(description).__name__}")
        return errors, warnings
    
    # Check for example blocks
    if '<example>' not in description:
        errors.append("Description must include at least one <example> block")
    else:
        # Count examples
        example_count = description.count('<example>')
        close_count = description.count('</example>')
        
        if example_count != close_count:
            errors.append(f"Mismatched example tags: {example_count} <example> vs {close_count} </example>")
        
        if example_count < 2:
            warnings.append(f"Consider adding more examples (found {example_count}, recommend 2-3)")
        
        # Check example structure
        example_pattern = r'<example>.*?Context:.*?user:.*?assistant:.*?</example>'
        if not re.search(example_pattern, description, re.DOTALL | re.IGNORECASE):
            warnings.append("Example blocks should include Context:, user:, and assistant: fields")
    
    # Check for trigger documentation
    trigger_patterns = ['trigger', 'invoke', 'activate', 'use when']
    if not any(p in description.lower() for p in trigger_patterns):
        warnings.append("Consider documenting trigger phrases in description")
    
    # Check description length
    if len(description) < 50:
        warnings.append(f"Description seems short ({len(description)} chars). Add more trigger context.")
    
    return errors, warnings

def validate_optional_fields(frontmatter: dict) -> list[str]:
    """Validate optional fields if present."""
    warnings = []
    
    # Model field
    if 'model' in frontmatter:
        valid_models = ['opus', 'sonnet', 'haiku']
        if frontmatter['model'] not in valid_models:
            warnings.append(f"Unknown model '{frontmatter['model']}'. Valid: {valid_models}")
    
    # Color field
    if 'color' in frontmatter:
        valid_colors = ['green', 'blue', 'purple', 'orange', 'red']
        if frontmatter['color'] not in valid_colors:
            warnings.append(f"Unknown color '{frontmatter['color']}'. Valid: {valid_colors}")
    
    # Unknown fields
    known_fields = {'name', 'description', 'model', 'color'}
    unknown = set(frontmatter.keys()) - known_fields
    if unknown:
        warnings.append(f"Unknown frontmatter fields (will be ignored): {unknown}")
    
    return warnings

def validate_body(body: str) -> tuple[list[str], list[str]]:
    """Validate the markdown body content."""
    errors = []
    warnings = []
    
    body_stripped = body.strip()
    
    if not body_stripped:
        errors.append("Command body is empty. Add instructions after frontmatter.")
        return errors, warnings
    
    if len(body_stripped) < 100:
        warnings.append(f"Body seems short ({len(body_stripped)} chars). Add more detailed instructions.")
    
    # Check for common sections
    has_heading = body_stripped.startswith('#') or '\n#' in body_stripped
    if not has_heading:
        warnings.append("Consider adding markdown headings to structure the body")
    
    # Check for role/identity statement (common pattern)
    identity_patterns = ['you are', 'you specialize', 'your role', 'your job']
    if not any(p in body.lower() for p in identity_patterns):
        warnings.append("Consider adding an identity/role statement (e.g., 'You are an expert...')")
    
    return errors, warnings

def validate_file_location(filepath: Path) -> list[str]:
    """Check if file is in correct location."""
    warnings = []
    
    expected_parent = Path.home() / 'jarvis' / 'commands'
    
    try:
        # Check if in commands directory
        if filepath.parent.resolve() != expected_parent.resolve():
            warnings.append(f"File not in ~/jarvis/commands/. Current: {filepath.parent}")
    except Exception:
        pass  # Path comparison might fail in some edge cases
    
    # Check filename matches command pattern
    if not filepath.suffix == '.md':
        warnings.append(f"Expected .md extension, got '{filepath.suffix}'")
    
    return warnings

def validate_command(filepath: Path) -> ValidationResult:
    """
    Validate a single command file.
    Returns ValidationResult with valid flag, errors, and warnings.
    """
    errors = []
    warnings = []
    
    # Check file exists
    if not filepath.exists():
        return ValidationResult(False, [f"File not found: {filepath}"], [])
    
    # Read content
    try:
        content = filepath.read_text()
    except Exception as e:
        return ValidationResult(False, [f"Cannot read file: {e}"], [])
    
    # Extract frontmatter
    frontmatter, body, fm_error = extract_frontmatter(content)
    if fm_error:
        errors.append(fm_error)
    
    if frontmatter:
        # Validate name
        errors.extend(validate_name(frontmatter.get('name')))
        
        # Validate description
        desc_errors, desc_warnings = validate_description(frontmatter.get('description'))
        errors.extend(desc_errors)
        warnings.extend(desc_warnings)
        
        # Validate optional fields
        warnings.extend(validate_optional_fields(frontmatter))
        
        # Check filename matches name
        expected_filename = f"{frontmatter.get('name', '')}.md"
        if filepath.name != expected_filename:
            warnings.append(f"Filename '{filepath.name}' doesn't match command name. Expected: '{expected_filename}'")
    
    # Validate body
    body_errors, body_warnings = validate_body(body)
    errors.extend(body_errors)
    warnings.extend(body_warnings)
    
    # Check file location
    warnings.extend(validate_file_location(filepath))
    
    return ValidationResult(len(errors) == 0, errors, warnings)

def print_result(filepath: Path, result: ValidationResult) -> None:
    """Print validation results in a readable format."""
    status = "✓ VALID" if result.valid else "✗ INVALID"
    print(f"\n{status}: {filepath.name}")
    print("=" * 50)
    
    if result.errors:
        print("\nERRORS:")
        for error in result.errors:
            print(f"  ✗ {error}")
    
    if result.warnings:
        print("\nWARNINGS:")
        for warning in result.warnings:
            print(f"  ⚠ {warning}")
    
    if not result.errors and not result.warnings:
        print("\n  No issues found.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_command.py <path/to/command.md>")
        print("       python validate_command.py <path/to/commands/directory/>")
        sys.exit(1)
    
    path = Path(sys.argv[1]).expanduser()
    
    if path.is_dir():
        # Validate all .md files in directory
        files = list(path.glob('*.md'))
        if not files:
            print(f"No .md files found in {path}")
            sys.exit(1)
        
        all_valid = True
        for filepath in sorted(files):
            result = validate_command(filepath)
            print_result(filepath, result)
            if not result.valid:
                all_valid = False
        
        print("\n" + "=" * 50)
        print(f"Validated {len(files)} files. {'All valid!' if all_valid else 'Some have errors.'}")
        sys.exit(0 if all_valid else 1)
    
    elif path.is_file():
        result = validate_command(path)
        print_result(path, result)
        sys.exit(0 if result.valid else 1)
    
    else:
        print(f"Path not found: {path}")
        sys.exit(1)

if __name__ == '__main__':
    main()
