# iOS Remote Development with Claude Code (March 2026)

## TL;DR — Best Options Ranked

| Approach | Best For | Effort |
|----------|----------|--------|
| **Claude Code Remote Control** (`/rc`) | Easiest, official Anthropic solution | Zero setup |
| **Moshi + mosh + tmux** | Power users running AI agents | Medium |
| **Blink Shell + Tailscale + tmux** | General remote dev (Harper Reed's stack) | Medium |
| **Termius + Tailscale + tmux** | Teams, cross-platform sync | Low-Medium |

---

## Verifiable Data — GitHub Stars & App Store Ratings (March 4, 2026)

### Terminal Tools (GitHub) — Actively Maintained in 2026

| Project | Stars | Forks | Language | Last Commit | 2026 Active? |
|---------|------:|------:|----------|-------------|:------------:|
| [ghostty-org/ghostty](https://github.com/ghostty-org/ghostty) | 45,399 | 1,789 | Zig | 2026-03-04 | **Yes** — daily commits, macOS audio bell, Xcode 26.3 |
| [tmux/tmux](https://github.com/tmux/tmux) | 42,543 | 2,451 | C | 2026-03-04 | **Yes** — daily commits, new features (exit-on-scroll, list-keys sort) |
| [zellij-org/zellij](https://github.com/zellij-org/zellij) | 29,631 | 1,003 | Rust | 2026-03-04 | **Yes** — Windows port landed, mobile web client, active |
| [Eugeny/tabby](https://github.com/Eugeny/tabby) | 69,270 | 3,890 | TypeScript | 2026-02-28 | **Yes** — tabby:// URL scheme, SFTP, SSH fixes |
| [wez/wezterm](https://github.com/wez/wezterm) | 24,643 | 1,233 | Rust | 2026-01-17 | **Slowing** — last commit Jan 17, was very active in 2025 |
| [mobile-shell/mosh](https://github.com/mobile-shell/mosh) | 13,604 | 788 | C++ | 2026-02-28 | **Yes** — getrandom/getentropy support, CI updates |

### iOS SSH Clients — Actively Maintained in 2026

| App | GitHub Stars | App Store Rating | Reviews | Price | 2026 Active? |
|-----|------------:|:----------------:|--------:|-------|:------------:|
| [Moshi](https://apps.apple.com/us/app/moshi-ssh-mosh-terminal/id6757859949) | N/A (closed) | 5.0/5 | 13 ratings | ~$10 | **Yes** — v1.4.2 (Feb 10, 2026), Tailscale SSH, file sharing |
| [Termius](https://apps.apple.com/us/app/termius-modern-ssh-client/id549039908) | N/A (closed) | 4.7/5 | 17,341 reviews | Free / $10/mo | **Yes** — regular App Store updates |
| [Blink Shell](https://github.com/blinksh/blink) | 6,620 | 3.1/5 | N/A | $20/yr | **No** — last GitHub commit May 2025, issues still filed but no code changes |
| [claude-code-mobile-ssh](https://github.com/aiya000/claude-code-mobile-ssh) | 14 | N/A (PWA) | N/A | Free | **No** — last commit Jul 2025, appears abandoned |

### Homebrew Install Analytics

> Brew analytics are JS-rendered and blocked from automated scraping.
> Run locally to get exact numbers:
> ```bash
> curl -sL https://formulae.brew.sh/api/formula/tmux.json | jq '.analytics'
> curl -sL https://formulae.brew.sh/api/formula/mosh.json | jq '.analytics'
> curl -sL https://formulae.brew.sh/api/formula/zellij.json | jq '.analytics'
> ```

### Key Takeaways from the Data

- **All core tools (tmux, mosh, zellij, ghostty) are actively maintained** with commits in March 2026
- **WezTerm is slowing down** — last commit Jan 17, 2026 (was daily in 2025)
- **Blink Shell is effectively unmaintained** — no code commits since May 2025, rating at 3.1
- **Moshi is the most actively developed iOS SSH client** — v1.4.2 shipped Feb 2026 with Tailscale support
- **Termius has the most App Store social proof** (17k+ reviews, 4.7 rating)
- **claude-code-mobile-ssh is dead** — 14 stars, no commits since Jul 2025
- **Zellij is the most exciting multiplexer** — Windows port just landed, mobile web client added

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
