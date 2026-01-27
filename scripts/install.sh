#!/bin/bash

# AI-Dev Workflow Installer
# Copies skill files to ~/.claude/skills/

set -e

SKILLS_DIR="$HOME/.claude/skills"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

echo "================================"
echo "  AI-Dev Workflow Installer"
echo "================================"
echo ""

# Check if Claude Code skills directory exists
if [ ! -d "$HOME/.claude" ]; then
    echo "Creating ~/.claude directory..."
    mkdir -p "$HOME/.claude"
fi

# Create skills directory if not exists
if [ ! -d "$SKILLS_DIR" ]; then
    echo "Creating skills directory..."
    mkdir -p "$SKILLS_DIR"
fi

# List of skills to install
SKILLS=(
    "ai-dev"
    "ai-dev.analyze"
    "ai-dev.spec"
    "ai-dev.plan"
    "ai-dev.impl"
    "ai-dev.review"
    "ai-dev.pr"
)

# Install each skill
echo "Installing skills..."
echo ""

for skill in "${SKILLS[@]}"; do
    if [ -d "$REPO_DIR/skills/$skill" ]; then
        echo "  Installing $skill..."

        # Backup existing skill if exists
        if [ -d "$SKILLS_DIR/$skill" ]; then
            echo "    Backing up existing $skill..."
            mv "$SKILLS_DIR/$skill" "$SKILLS_DIR/$skill.backup.$(date +%Y%m%d%H%M%S)"
        fi

        cp -r "$REPO_DIR/skills/$skill" "$SKILLS_DIR/"
        echo "    ✅ Done"
    else
        echo "  ⚠️  Warning: $skill not found in repository"
    fi
done

echo ""
echo "================================"
echo "  Installation Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your project paths:"
echo "   Edit ~/.claude/skills/ai-dev/SKILL.md"
echo "   Replace 'my-ios-app' with your project name"
echo ""
echo "2. Configure MCP servers (optional):"
echo "   - Codex MCP for cross-check"
echo "   - figma-ocaml MCP for Figma integration"
echo "   - apple-docs MCP for API documentation"
echo ""
echo "3. Start using:"
echo "   /ai-dev PROJ-12345"
echo ""
