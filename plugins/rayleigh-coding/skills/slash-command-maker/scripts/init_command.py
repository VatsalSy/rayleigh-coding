#!/usr/bin/env python3
"""
Initialize a new jarvis slash command file with template structure.

Creates a properly structured command file with:
- YAML frontmatter with required fields
- Template example blocks
- Markdown body scaffold

Usage:
    python init_command.py <command-name>
    python init_command.py <command-name> --path /custom/path
    python init_command.py <command-name> --model opus --color green

Examples:
    python init_command.py git-sync
    python init_command.py note-create --model sonnet
    python init_command.py pr-review --path ~/projects/jarvis/commands/
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

COMMAND_TEMPLATE = '''---
name: {name}
description: |
  {description_placeholder}

  **Triggers:** "{trigger_placeholder}"

  <example>
  Context: [Describe the situation]
  user: "[Example user message that triggers this command]"
  assistant: "[Expected assistant response or action]"
  <commentary>
  [Explain why this input triggers this command]
  </commentary>
  </example>

  <example>
  Context: [Alternative situation]
  user: "[Different phrasing that also triggers this]"
  assistant: "[Expected response]"
  <commentary>
  [Explain the pattern match]
  </commentary>
  </example>
{optional_fields}---

# {title} - [Brief Descriptor]

You are an expert [role] specializing in [domain].

## Core Responsibilities

1. [Primary responsibility]
2. [Secondary responsibility]
3. [Additional responsibility]

## Process

1. **[Step 1 name]**
   - [Detail]

2. **[Step 2 name]**
   - [Detail]

3. **[Step 3 name]**
   - [Detail]

## Guidelines

- [Guideline 1]
- [Guideline 2]
- [Guideline 3]

## Output Format

[Describe expected output structure]

```
[Template if applicable]
```
'''

def to_title(name: str) -> str:
    """Convert command-name to Title Case."""
    return ' '.join(word.capitalize() for word in name.split('-'))

def generate_description_placeholder(name: str) -> str:
    """Generate a placeholder description based on command name."""
    words = name.split('-')
    if len(words) >= 2:
        action = words[0]
        subject = ' '.join(words[1:])
        return f"[Describe what this command does with {subject}]"
    return "[Describe what this command does]"

def generate_trigger_placeholder(name: str) -> str:
    """Generate placeholder triggers based on command name."""
    words = name.split('-')
    triggers = [name.replace('-', ' ')]
    if len(words) >= 2:
        triggers.append(f"{words[0]} {' '.join(words[1:])}")
        triggers.append(' '.join(words))
    return '", "'.join(triggers[:3])

def create_command(
    name: str,
    output_path: Path,
    model: str | None = None,
    color: str | None = None,
    force: bool = False
) -> Path:
    """
    Create a new command file from template.
    
    Args:
        name: Command name (lowercase, hyphenated)
        output_path: Directory to create file in
        model: Optional model (opus/sonnet/haiku)
        color: Optional color (green/blue/purple/orange/red)
        force: Overwrite if file exists
    
    Returns:
        Path to created file
    """
    # Validate name
    if not name.replace('-', '').isalnum():
        raise ValueError(f"Invalid command name: '{name}'. Use lowercase letters, numbers, and hyphens only.")
    
    if name != name.lower():
        raise ValueError(f"Command name must be lowercase: '{name}'")
    
    # Build optional fields
    optional_fields = ""
    if model:
        if model not in ['opus', 'sonnet', 'haiku']:
            raise ValueError(f"Invalid model: '{model}'. Use opus, sonnet, or haiku.")
        optional_fields += f"model: {model}\n"
    
    if color:
        if color not in ['green', 'blue', 'purple', 'orange', 'red']:
            raise ValueError(f"Invalid color: '{color}'. Use green, blue, purple, orange, or red.")
        optional_fields += f"color: {color}\n"
    
    # Generate content
    content = COMMAND_TEMPLATE.format(
        name=name,
        title=to_title(name),
        description_placeholder=generate_description_placeholder(name),
        trigger_placeholder=generate_trigger_placeholder(name),
        optional_fields=optional_fields
    )
    
    # Determine output file
    output_path = Path(output_path).expanduser()
    output_path.mkdir(parents=True, exist_ok=True)
    
    filepath = output_path / f"{name}.md"
    
    if filepath.exists() and not force:
        raise FileExistsError(f"File already exists: {filepath}. Use --force to overwrite.")
    
    # Write file
    filepath.write_text(content)
    
    return filepath

def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new jarvis slash command file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s git-sync
    %(prog)s note-create --model sonnet
    %(prog)s pr-review --color green --model opus
    %(prog)s my-command --path ~/custom/commands/
        """
    )
    
    parser.add_argument(
        'name',
        help='Command name (lowercase, hyphenated, e.g., git-sync)'
    )
    
    parser.add_argument(
        '--path', '-p',
        default='~/jarvis/commands/',
        help='Output directory (default: ~/jarvis/commands/)'
    )
    
    parser.add_argument(
        '--model', '-m',
        choices=['opus', 'sonnet', 'haiku'],
        help='Default model for the command'
    )
    
    parser.add_argument(
        '--color', '-c',
        choices=['green', 'blue', 'purple', 'orange', 'red'],
        help='UI color for the command'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Overwrite if file exists'
    )
    
    args = parser.parse_args()
    
    try:
        filepath = create_command(
            name=args.name,
            output_path=args.path,
            model=args.model,
            color=args.color,
            force=args.force
        )
        
        print(f"✓ Created command: {filepath}")
        print()
        print("Next steps:")
        print(f"  1. Edit {filepath} to customize the command")
        print(f"  2. Run: python validate_command.py {filepath}")
        print("  3. Reload jarvis to activate the command")
        print()
        print(f"Use the command with: /{args.name}")
        
    except (ValueError, FileExistsError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
