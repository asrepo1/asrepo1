# iOS Remote Development with Claude Code (March 2026)

## TL;DR — Best Options Ranked

| Approach | Best For | Effort |
|----------|----------|--------|
| **Claude Code Remote Control** (`/rc`) | Easiest, official Anthropic solution | Zero setup |
| **Moshi + mosh + tmux** | Power users running AI agents | Medium |
| **Blink Shell + Tailscale + tmux** | General remote dev (Harper Reed's stack) | Medium |
| **Termius + Tailscale + tmux** | Teams, cross-platform sync | Low-Medium |

---

## Option 1: Claude Code Remote Control (Official — NEW Feb 2026)

Anthropic shipped this on Feb 25, 2026. No SSH needed.

```bash
# In your terminal on Mac, update Claude Code first
curl -fsSL https://claude.ai/install.sh | bash

# Start a session, then run:
claude remote-control
# or use the slash command inside a session:
/rc
```

- Scan the QR code with the Claude app on your iPhone
- Your phone becomes a window into the session running on your Mac
- No code leaves your machine — phone is just a remote display
- Requires Claude v2.1.52+, Pro or Max plan
- Limitation: one remote session per instance, terminal must stay open

## Option 2: SSH + tmux + mosh (The Classic Stack)

This is what Harper Reed, most Anthropic engineers, and the broader community recommend.

### Networking: Tailscale

```bash
# Install on Mac
brew install tailscale

# Install on iPhone from App Store
# Both devices join the same Tailnet — direct encrypted connection
```

### Session Persistence: tmux

```bash
# On your Mac, start a tmux session
tmux new -s claude

# Run Claude Code inside it
claude

# Detach: Ctrl-b d
# Reattach from phone: tmux attach -t claude
```

### Connection Resilience: mosh

```bash
# Install on Mac
brew install mosh

# Connect from iOS (Blink/Moshi support mosh natively)
mosh your-mac-tailscale-ip
```

mosh handles Wi-Fi → cellular → tunnel transitions seamlessly.

### iOS SSH Client Options

**Moshi** (~$10) — Purpose-built for AI coding agents
- Native mosh support
- Push notifications when Claude needs input
- Voice input for responding to prompts
- Best choice specifically for Claude Code workflows

**Blink Shell** ($20/yr) — Best general-purpose terminal
- Native mosh support
- Open source, very mature
- No push notifications for agent events
- Harper Reed's pick

**Termius** (Free tier available) — Best for teams
- Cloud sync of hosts/credentials across devices
- Clean UI, good keyboard toolbar
- No mosh support (SSH only)

## Option 3: Is There Anything Better Than tmux?

### Zellij — Modern alternative
- Discoverable UI with floating/stacked panes
- Plugin system, true multiplayer collaboration
- Better defaults out of the box
- `cargo install zellij` or `brew install zellij`

### Shpool — Lightweight session persistence only
- If you only need detach/reattach (no splits/panes)
- Much simpler than tmux
- `cargo install shpool`

### WezTerm — Terminal + multiplexer in one
- GPU-accelerated, Lua-scriptable
- Built-in multiplexer eliminates need for tmux
- Cross-platform

### Verdict
For remote iOS → Mac with Claude Code, **tmux is still the best choice** because:
1. Every iOS SSH client supports it
2. iTerm2's `tmux -CC` control mode turns tmux windows into native macOS tabs
3. Battle-tested over SSH connections
4. Zellij is great locally but has rougher edges over SSH

## Recommended Stack (What Teams Actually Use)

### Anthropic / Claude Team
- Cloud dev environments (Coder) for multi-agent workflows
- Remote Control (`/rc`) for quick mobile access
- tmux for session persistence

### Community Consensus (Harper Reed, indie devs)
```
Tailscale + Blink Shell (or Moshi) + mosh + tmux
```

### Enterprise / Teams
```
Tailscale (or corporate VPN) + Termius + tmux
```

## Quick Start (5 minutes)

The absolute fastest path:

1. Update Claude Code: `curl -fsSL https://claude.ai/install.sh | bash`
2. Start a session: `claude`
3. Type `/rc`
4. Scan QR code with Claude app on iPhone
5. Done — code from your couch

If you want the full SSH setup for more control, persistence, and multiple sessions:

1. Install Tailscale on Mac + iPhone
2. Install Moshi (or Blink) on iPhone
3. `brew install mosh tmux` on Mac
4. Enable SSH on Mac: System Settings → General → Sharing → Remote Login
5. From iPhone: `mosh your-mac-tailscale-ip` → `tmux new -s claude` → `claude`

## Sources

- [Anthropic Remote Control announcement](https://venturebeat.com/orchestration/anthropic-just-released-a-mobile-version-of-claude-code-called-remote)
- [Claude Code Remote Control setup guide](https://claudefa.st/blog/guide/development/remote-control-guide)
- [Harper Reed — Remote Claude Code](https://harper.blog/2026/01/05/claude-code-is-better-on-your-phone/)
- [Moshi — Best iOS Terminal for AI Agents](https://getmoshi.app/articles/best-ios-terminal-app-coding-agent)
- [Blink Shell](https://blink.sh/)
- [Claude Code from the beach (mosh + tmux + ntfy)](https://rogs.me/2026/02/claude-code-from-the-beach-my-remote-coding-setup-with-mosh-tmux-and-ntfy/)
- [Anthropic engineers using Coder for remote Claude Code](https://coder.com/blog/building-for-2026-why-anthropic-engineers-are-running-claude-code-remotely-with-c)
- [Claude Code Mobile SSH (PWA)](https://github.com/aiya000/claude-code-mobile-ssh)
- [iTerm2 + tmux -CC control mode](https://evoleinik.com/posts/iterm2-tmux-control-mode/)
- [Builder.io — Claude Code on Your Phone](https://www.builder.io/blog/claude-code-mobile-phone)
