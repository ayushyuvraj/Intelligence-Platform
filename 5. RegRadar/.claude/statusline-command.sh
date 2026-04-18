#!/usr/bin/env bash
# RegRadar Claude Code Status Line
# Reads JSON from stdin and outputs a compact status line

input=$(cat)

# Extract fields
dir=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
model=$(echo "$input" | jq -r '.model.display_name // ""')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
vim_mode=$(echo "$input" | jq -r '.vim.mode // empty')
session_name=$(echo "$input" | jq -r '.session_name // empty')
git_worktree=$(echo "$input" | jq -r '.workspace.git_worktree // empty')

# Shorten directory: basename only
basename_dir=$(basename "$dir")

# Build status line pieces
parts=()

# Directory
[ -n "$basename_dir" ] && parts+=("$(printf '\033[0;36m%s\033[0m' "$basename_dir")")

# Git worktree (if in a linked worktree)
[ -n "$git_worktree" ] && parts+=("$(printf '\033[0;35mworktree:%s\033[0m' "$git_worktree")")

# Session name
[ -n "$session_name" ] && parts+=("$(printf '\033[0;33m\"%s\"\033[0m' "$session_name")")

# Model (shortened)
if [ -n "$model" ]; then
  short_model=$(echo "$model" | sed 's/Claude //' | sed 's/ Sonnet/S/' | sed 's/ Haiku/H/' | sed 's/ Opus/O/')
  parts+=("$(printf '\033[0;32m%s\033[0m' "$short_model")")
fi

# Context usage
if [ -n "$used_pct" ]; then
  used_int=$(printf '%.0f' "$used_pct")
  if [ "$used_int" -ge 80 ]; then
    color='\033[0;31m'   # red
  elif [ "$used_int" -ge 50 ]; then
    color='\033[0;33m'   # yellow
  else
    color='\033[0;32m'   # green
  fi
  parts+=("$(printf "${color}ctx:%d%%\033[0m" "$used_int")")
fi

# Vim mode
[ -n "$vim_mode" ] && parts+=("$(printf '\033[0;35m[%s]\033[0m' "$vim_mode")")

# Join with separator
printf '%s' "${parts[0]}"
for part in "${parts[@]:1}"; do
  printf ' \033[0;90m|\033[0m %s' "$part"
done
printf '\n'
