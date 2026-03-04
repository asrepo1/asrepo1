# iOS Remote Development — Claude Code, Codex, Gemini CLI (March 2026)

> **Your requirements:** Extremely fast, lightweight, iPhone-first. Claude Code primary, Codex + Gemini CLI secondary. Apple Developer Program member. Actively maintained in 2026.

---

## TL;DR — Pick One and Go

| If you want... | Use this | Setup time |
|----------------|----------|------------|
| **Zero setup, official** | Claude Code `/rc` | 30 seconds |
| **All 3 CLIs, open source, push notifications** | [Happy Coder](https://happy.engineering/) | 2 minutes |
| **Self-hosted, no cloud, fastest** | [MobileCLI](https://www.mobilecli.app/) | 5 minutes |
| **Voice-first, hands-free** | [Sled](https://sled.layercode.com/) or [VoxHerd](https://voxherd.com/) | 5 minutes |
| **Raw SSH terminal, AI-optimized** | [Moshi](https://getmoshi.app) + mosh + tmux | 10 minutes |
| **Self-build your own app** | [SwiftTerm](https://github.com/migueldeicaza/SwiftTerm) or [Blink Shell](https://github.com/blinksh/blink) | Hours |

---

## Tier 1: Native/Official Solutions (No SSH Needed)

### Claude Code Remote Control (`/rc`)

Anthropic's official solution, shipped Feb 25, 2026. The fastest path.

```bash
# Update Claude Code
curl -fsSL https://claude.ai/install.sh | bash

# Inside any session:
/rc

# Or start a new remote session:
claude remote-control
```

- Scan QR code with Claude iOS app or open URL in browser
- Code stays on your machine — only chat flows through encrypted TLS bridge
- Auto-reconnects after sleep/network drops (~10 min timeout)
- Requires Claude Code v2.1.52+, Pro ($20/mo) or Max ($100-200/mo)
- One remote viewer per session
- Cannot use `--dangerously-skip-permissions` — must approve from phone

**Tip:** Run `/config` → "Enable Remote Control for all sessions" to auto-enable.

Docs: [code.claude.com/docs/en/remote-control](https://code.claude.com/docs/en/remote-control)

### OpenAI Codex Cloud (Web)

No CLI needed — visit [chatgpt.com/codex](https://chatgpt.com/codex) in mobile Safari.

- Runs tasks in parallel sandbox environments
- Can propose PRs directly
- Included with ChatGPT Plus ($20/mo), Pro ($200/mo)
- No native mobile remote for the CLI yet ([requested: openai/codex#9224](https://github.com/openai/codex/issues/9224))

### Google Gemini CLI — Headless Mode

No native mobile remote. Use SSH or headless mode:

```bash
# One-shot from phone over SSH
gemini -p "Summarize ./report.txt"

# Free tier: 60 req/min, 1,000 req/day with personal Google account
```

---

## Tier 2: Multi-Agent Companion Apps (All 3 CLIs)

These are purpose-built for running Claude Code, Codex, and Gemini CLI from your phone.

### Happy Coder — Free, Open Source, All 3 CLIs

```bash
npm install -g happy-coder

# Launch Claude Code
happy

# Launch Codex
happy codex

# Launch Gemini CLI
happy gemini
```

- **iOS app:** [App Store](https://apps.apple.com/us/app/happy-codex-claude-code-app/id6748571505)
- **GitHub:** [slopus/happy](https://github.com/slopus/happy)
- Multi-session (multiple Claude Codes in parallel)
- E2E encryption, push notifications, voice execution
- Free, MIT license, runs on your hardware

### MobileCLI — Self-Hosted, No Cloud

- **Website:** [mobilecli.app](https://www.mobilecli.app/)
- Self-hosted Rust daemon (macOS, Linux, Windows)
- Streams terminal output to your phone
- Approve tool calls, browse files, monitor progress
- Connects over local network or Tailscale
- Multiple concurrent sessions across agents
- Push notifications
- Free core features, open source daemon

### Sled by Layercode — Voice-First

- **Website:** [sled.layercode.com](https://sled.layercode.com/)
- **GitHub:** [layercodedev/sled](https://github.com/layercodedev/sled)
- Web UI spawns local agents in headless API mode
- Voice I/O — handles camelCase, function names correctly, 300+ voices
- Works with AirPods, no screen needed
- Free, open source

### VoxHerd — Voice Controller

- **Website:** [voxherd.com](https://voxherd.com/)
- Apple TestFlight (active development)
- On-device speech recognition (no cloud)
- Routes voice commands to correct project
- Works with Claude Code, Codex, Gemini CLI

### Other Companion Apps

| App | Model | Key Feature |
|-----|-------|-------------|
| [Remote Codetrol](https://remotecodetrol.ai/) | Mac server + iPhone | mTLS security, supports 7+ AI CLIs |
| [Claude Remote](https://www.clauderc.com/) | Cloudflare Tunnel | Monitor long-running tasks |
| [CloudCLI](https://github.com/siteboon/claudecodeui) | Web UI | Supports Claude, Cursor, Codex, Gemini |
| [Mobile IDE for Claude Code](https://apps.apple.com/us/app/mobile-ide-for-claude-code/id6757921693) | CloudKit sync | Syncs prompts/results iPhone↔Mac |
| [Claude-Code-Remote](https://github.com/JessyTsui/Claude-Code-Remote) | Email/Discord/Telegram | Control Claude Code via messaging |

---

## Tier 3: SSH Terminal Apps (The Classic Stack)

For when you want a raw terminal on your phone.

### Recommended Stack

```
iPhone → Tailscale (free) → mosh → tmux → Claude Code / Codex / Gemini
```

### iOS Terminal App Comparison (March 2026)

| App | Mosh | Price | Push Notifications | Best For |
|-----|:----:|-------|:------------------:|----------|
| **[Moshi](https://getmoshi.app)** | Yes | Free | **Yes** (+ Apple Watch) | AI agent workflows |
| **[Echo](https://replay.software/echo)** | Yes | $2.99 one-time | No | Raw speed (Ghostty engine, Metal) |
| **[Prompt 3](https://panic.com/prompt/)** | Yes + ET | $20/yr or $100 | No | Polish, Panic quality |
| **[Termius](https://termius.com/)** | Yes | Free / paid tiers | No | Teams, cross-platform sync |
| **[Blink Shell](https://blink.sh/)** | Yes | $19.99/yr | No | Open source, iPad dev |

#### Moshi — Purpose-Built for AI Agents

- Push notifications when Claude needs input
- Voice-to-terminal (on-device Whisper, no cloud)
- Native mosh, Tailscale DNS built in
- Face ID for SSH keys
- Free, no subscription
- iOS 17.0+, v1.4.2 (Feb 2026)

#### Echo — Fastest Rendering (NEW)

- Ghostty terminal engine (Metal-accelerated)
- $2.99 one-time, no subscription
- Native mosh, SSH cert auth + Face ID
- 400+ themes, touch-optimized toolbar
- **Requires iOS 26.2+** (very new)
- [Show HN thread](https://news.ycombinator.com/item?id=47064787)

#### Prompt 3 by Panic — Most Polished

- 10x faster scrolling/emulation (retooled engine)
- Mosh + Eternal Terminal support
- Panic Sync, YubiKey 2FA, mouse support for TUIs
- $20/yr or $100 one-time

### Setup (5 minutes)

```bash
# On your Mac (one time)
brew install mosh tmux
# Enable SSH: System Settings → General → Sharing → Remote Login

# Install Tailscale on Mac + iPhone (free for personal use)
brew install tailscale

# Start Claude in tmux
tmux new -s ai && claude
```

On iPhone:
1. Install Moshi (or Echo, or Prompt 3)
2. Connect: `mosh your-mac-tailscale-hostname`
3. Attach: `tmux attach -t ai`

### Push Notifications for Agent Idle

Use [ntfy.sh](https://ntfy.sh/) (free) to get notified when Claude needs input:

```bash
# Claude Code hooks fire on idle_prompt (waiting 60+ sec)
# and permission_prompt
```

See: [Claude Code from the beach](https://rogs.me/2026/02/claude-code-from-the-beach-my-remote-coding-setup-with-mosh-tmux-and-ntfy/)

---

## Tier 4: Self-Build (Apple Developer Program)

Since you have Apple Developer Program, you can build and sideload custom apps.

### SwiftTerm — Build Your Own Terminal

- **GitHub:** [migueldeicaza/SwiftTerm](https://github.com/migueldeicaza/SwiftTerm) — Xterm/VT100 emulator library
- Creator: Miguel de Icaza (Mono/Xamarin)
- Includes iOS sample app with SSH via swift-nio-ssh
- Active (last update Dec 2025)
- **Use case:** Build a custom terminal tailored exactly to your AI agent workflow

### Blink Shell — Fork and Customize

- **GitHub:** [blinksh/blink](https://github.com/blinksh/blink) — 6,620 stars, GPL3
- Full SSH + mosh implementation in Swift
- You can fork, strip features you don't need, add push notifications
- **Caveat:** Last code commit May 2025 — community still active but core dev slowed

### Ghostty — Terminal Engine (macOS, not iOS yet)

- **GitHub:** [ghostty-org/ghostty](https://github.com/ghostty-org/ghostty) — 45,399 stars
- SwiftUI on macOS, Metal renderer, C-compatible library
- Daily commits as of March 2026
- Powers the Echo iOS app (above)
- Could theoretically be embedded in a custom iOS app

### NewTerm 3

- **GitHub:** [hbang/NewTerm](https://github.com/hbang/NewTerm)
- iPhone + iPad + Mac support, iTerm2 Shell Integration

---

## Headless / Non-Interactive Modes

For quick one-shots from your phone without the full TUI:

### Claude Code

```bash
claude -p "Fix the failing tests" --max-turns 5
claude -p "Summarize this file" --output-format json
echo "Add types to utils.ts" | claude -p
claude -p "Continue the refactor" --continue
```

### Codex CLI

```bash
codex exec "Fix the linting errors"   # non-interactive
codex e "Add error handling"           # alias
```

### Gemini CLI

```bash
gemini -p "Explain the auth flow"
gemini --yolo -p "Fix all tests"       # auto-approve tool calls
gemini --sandbox -p "Run experiments"  # sandboxed
```

---

## Verified Data (March 4, 2026)

### Terminal Tools — GitHub Activity

| Project | Stars | Last Commit | 2026 Status |
|---------|------:|-------------|-------------|
| [ghostty](https://github.com/ghostty-org/ghostty) | 45,399 | 2026-03-04 | Daily commits |
| [tmux](https://github.com/tmux/tmux) | 42,543 | 2026-03-04 | Daily commits |
| [zellij](https://github.com/zellij-org/zellij) | 29,631 | 2026-03-04 | Windows port, mobile web client |
| [mosh](https://github.com/mobile-shell/mosh) | 13,604 | 2026-02-28 | Active |
| [wezterm](https://github.com/wez/wezterm) | 24,643 | 2026-01-17 | Slowing down |

### iOS Apps — App Store Status

| App | Rating | Reviews | Last Update |
|-----|--------|---------|-------------|
| Termius | 4.7/5 | 17,341 | Active |
| Moshi | 5.0/5 | 13 | v1.4.2 (Feb 2026) |
| Blink Shell | 3.1/5 | — | Code: May 2025 |

---

## What Engineers Actually Use

| Who | Stack |
|-----|-------|
| **Anthropic (internal)** | Coder cloud dev environments + `/rc` for mobile |
| **Harper Reed** | Blink Shell + mosh + tmux + Tailscale |
| **Community consensus** (HN, dev.to) | Moshi or Blink + Tailscale + tmux + mosh |
| **Japanese dev community** | Moshi + mosh + tmux + Tailscale |
| **Codex CLI users** | Termius + Tailscale (per GitHub issue) |

---

## Decision Flowchart

```
Q: Do you only use Claude Code?
├─ Yes → Use /rc (30 seconds, done)
│
Q: Do you use multiple CLIs (Claude + Codex + Gemini)?
├─ Yes → Happy Coder (free, all 3, push notifications)
│        OR MobileCLI (self-hosted, no cloud)
│
Q: Do you want voice control?
├─ Yes → Sled (voice I/O, AirPods) or VoxHerd (on-device)
│
Q: Do you want raw terminal access?
├─ Yes, fastest render → Echo ($2.99, Ghostty engine)
├─ Yes, push notifications → Moshi (free)
├─ Yes, most polished → Prompt 3 ($20/yr)
│
Q: Do you want to build your own app?
└─ Yes → Fork Blink Shell or build on SwiftTerm
```

---

## Sources

### Official Docs
- [Claude Code Remote Control](https://code.claude.com/docs/en/remote-control)
- [Claude Code Headless Mode](https://code.claude.com/docs/en/headless)
- [OpenAI Codex CLI](https://developers.openai.com/codex/cli/)
- [Gemini CLI](https://geminicli.com/)

### Announcements & Coverage
- [VentureBeat: Anthropic Remote Control](https://venturebeat.com/orchestration/anthropic-just-released-a-mobile-version-of-claude-code-called-remote)
- [Simon Willison on /rc](https://simonwillison.net/2026/Feb/25/claude-code-remote-control/)
- [Builder.io: Claude Code on Your Phone](https://www.builder.io/blog/claude-code-mobile-phone)

### Community Workflows
- [Harper Reed: Claude Code on Phone](https://harper.blog/2026/01/05/claude-code-is-better-on-your-phone/)
- [Claude Code from the Beach (mosh + tmux + ntfy)](https://rogs.me/2026/02/claude-code-from-the-beach-my-remote-coding-setup-with-mosh-tmux-and-ntfy/)
- [Anthropic Engineers Using Coder](https://coder.com/blog/building-for-2026-why-anthropic-engineers-are-running-claude-code-remotely-with-c)
- [iPhone → MacBook Setup](https://dreamiurg.net/2026/01/06/iphone-to-macbook-remote-claude-code-setup.html)

### Apps & Tools
- [Moshi](https://getmoshi.app) | [Articles](https://getmoshi.app/articles/best-ios-terminal-app-coding-agent)
- [Echo](https://replay.software/echo) | [HN Thread](https://news.ycombinator.com/item?id=47064787)
- [Prompt 3](https://panic.com/prompt/)
- [Termius](https://termius.com/)
- [Happy Coder](https://happy.engineering/) | [GitHub](https://github.com/slopus/happy)
- [MobileCLI](https://www.mobilecli.app/)
- [Sled](https://sled.layercode.com/) | [GitHub](https://github.com/layercodedev/sled)
- [VoxHerd](https://voxherd.com/)
- [Remote Codetrol](https://remotecodetrol.ai/)
- [Tailscale iOS](https://tailscale.com/docs/install/ios)

### Self-Build Resources
- [SwiftTerm](https://github.com/migueldeicaza/SwiftTerm)
- [Blink Shell Source](https://github.com/blinksh/blink)
- [Ghostty](https://github.com/ghostty-org/ghostty)
- [NewTerm](https://github.com/hbang/NewTerm)
