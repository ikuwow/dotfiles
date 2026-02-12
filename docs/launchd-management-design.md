# launchd Job Management Design

## 1. Directory Structure

```
dotfiles/
├── LaunchAgents/              # New directory
│   └── local.homebrew.autoupdate.plist
├── scripts/
│   ├── deploy.sh              # Modify: Add LaunchAgents support
│   └── configure_brew.sh      # Modify: Remove existing autoupdate config
├── Brewfile                   # No change (keep or remove tap "homebrew/autoupdate")
└── README.md                  # Modify: Add LaunchAgents management docs
```

## 2. Plist File Naming Convention

Format: `local.<category>.<job-name>.plist`

- `local.` prefix: Indicates user-defined job
- `<category>`: Functional category such as homebrew, backup, cleanup
- `<job-name>`: Specific task name such as autoupdate, sync

Examples:
- `local.homebrew.autoupdate.plist` - Auto-update Homebrew/mas
- `local.backup.timemachine.plist` - Time Machine backup
- `local.cleanup.logs.plist` - Log file cleanup

## 3. Basic Plist File Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Job identifier (should match plist filename) -->
    <key>Label</key>
    <string>local.homebrew.autoupdate</string>

    <!-- Command to execute -->
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>PATH=/opt/homebrew/bin:/usr/local/bin:$PATH; mas upgrade && brew upgrade</string>
    </array>

    <!-- Schedule: Daily at 4:00 AM -->
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>4</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <!-- Log output paths -->
    <key>StandardOutPath</key>
    <string>/tmp/homebrew-autoupdate.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/homebrew-autoupdate.err</string>

    <!-- Environment variables (if needed) -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
```

Design considerations:
- Explicitly set PATH in `ProgramArguments` (launchd has minimal environment variables)
- Include both `/opt/homebrew/bin` and `/usr/local/bin` for Intel/Apple Silicon compatibility
- Log files in `/tmp` (no persistence needed, periodically cleaned up)

## 4. Deployment Mechanism (deploy.sh)

```bash
#!/usr/bin/env bash

# ... existing code ...

# Deploy LaunchAgents
echo "Deploying LaunchAgents..."
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$LAUNCH_AGENTS_DIR"

if [[ -d "$DOTPATH/LaunchAgents" ]]; then
  for plist in "$DOTPATH/LaunchAgents"/*.plist; do
    if [[ -f "$plist" ]]; then
      plist_name=$(basename "$plist")
      target="$LAUNCH_AGENTS_DIR/$plist_name"

      # Create symlink
      ln -fvns "$plist" "$target"

      # Register with launchd (unload first if already registered)
      launchctl unload "$target" 2>/dev/null || true
      launchctl load "$target"
      echo "Loaded: $plist_name"
    fi
  done
else
  echo "LaunchAgents directory not found, skipping."
fi
```

Idempotency guarantees:
1. `ln -fvns`: Force overwrite existing symlinks
2. `launchctl unload → load`: Unregister before re-registering
3. Continue on errors (`|| true`)

## 5. How to Update

### 5.1 Modifying plist file contents

```bash
# 1. Edit plist file in dotfiles repository
vim ~/dotfiles/LaunchAgents/local.homebrew.autoupdate.plist

# 2. Apply changes (deploy.sh automatically unloads → loads)
~/dotfiles/scripts/deploy.sh

# 3. Verify
launchctl list | grep local.homebrew.autoupdate
```

Git workflow:
```bash
cd ~/dotfiles
git add LaunchAgents/local.homebrew.autoupdate.plist
git commit -m "Update homebrew autoupdate schedule to 3am"
```

### 5.2 Changing schedule only

Edit `StartCalendarInterval` section:
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>3</integer>  <!-- Changed from 4 to 3 -->
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

## 6. How to Remove

### 6.1 Temporarily disable

```bash
# Stop job (keep symlink)
launchctl unload ~/Library/LaunchAgents/local.homebrew.autoupdate.plist
```

### 6.2 Permanently remove

```bash
# 1. Unregister from launchd
launchctl unload ~/Library/LaunchAgents/local.homebrew.autoupdate.plist

# 2. Delete from dotfiles repository
rm ~/dotfiles/LaunchAgents/local.homebrew.autoupdate.plist

# 3. Delete symlink
rm ~/Library/LaunchAgents/local.homebrew.autoupdate.plist

# 4. Commit to Git
cd ~/dotfiles
git add -A
git commit -m "Remove homebrew autoupdate job"
```

Note: deploy.sh does not auto-delete removed plists. This is a safety measure to prevent accidental deletion.

## 7. Verification Methods

### 7.1 Check registration status

```bash
# List all jobs
launchctl list | grep local.

# Show details for specific job
launchctl list local.homebrew.autoupdate
```

### 7.2 Manual test execution

```bash
# Execute job immediately (without waiting for schedule)
launchctl start local.homebrew.autoupdate

# Check logs
tail -f /tmp/homebrew-autoupdate.log
tail -f /tmp/homebrew-autoupdate.err
```

### 7.3 Check next execution time

macOS 13+:
```bash
launchctl print gui/$(id -u)/local.homebrew.autoupdate
```

macOS 12 and earlier:
```bash
# Check plist file directly
cat ~/Library/LaunchAgents/local.homebrew.autoupdate.plist | grep -A 5 StartCalendarInterval
```

## 8. Troubleshooting

### 8.1 Job not executing

```bash
# 1. Verify job is registered
launchctl list | grep local.homebrew.autoupdate

# 2. Check plist syntax
plutil -lint ~/Library/LaunchAgents/local.homebrew.autoupdate.plist

# 3. Check logs
cat /tmp/homebrew-autoupdate.log
cat /tmp/homebrew-autoupdate.err

# 4. Manual execution to check for errors
launchctl start local.homebrew.autoupdate
```

### 8.2 PATH not set correctly

Set PATH explicitly in plist `ProgramArguments`:
```xml
<key>ProgramArguments</key>
<array>
    <string>/bin/bash</string>
    <string>-c</string>
    <string>PATH=/opt/homebrew/bin:/usr/local/bin:$PATH; mas upgrade && brew upgrade</string>
</array>
```

Or use `EnvironmentVariables`:
```xml
<key>EnvironmentVariables</key>
<dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
</dict>
```

## 9. Modifications to configure_brew.sh

Remove existing `brew autoupdate` settings to avoid conflicts:

```bash
#!/usr/bin/env bash

# Disable existing brew autoupdate
echo "Checking brew autoupdate status..."
if brew autoupdate --status | grep -q 'Autoupdate is installed and running.'; then
  echo "Disabling brew autoupdate (using launchd instead)..."
  brew autoupdate delete
else
  echo "brew autoupdate is not running. Nothing to do."
fi
```

## 10. Brewfile Handling

Two options:

Option A: Remove tap
```ruby
# Remove tap "homebrew/autoupdate"
# No longer needed
```

Option B: Keep tap (recommended)
```ruby
tap "homebrew/autoupdate"  # Keep
# Reason: May want to use it in the future
# No harm in having it installed
```

## 11. README.md Addition

```markdown
## LaunchAgents Management

This repository manages launchd jobs via plist files in `LaunchAgents/` directory.

### Deployed Jobs

- `local.homebrew.autoupdate.plist` - Auto-update Homebrew and Mac App Store apps daily at 4:00 AM

### Managing LaunchAgents

Deploy/Update:
\```bash
./scripts/deploy.sh
\```

Check status:
\```bash
launchctl list | grep local.
\```

Manual execution (for testing):
\```bash
launchctl start local.homebrew.autoupdate
\```

View logs:
\```bash
tail -f /tmp/homebrew-autoupdate.log
\```

Disable a job:
\```bash
launchctl unload ~/Library/LaunchAgents/local.homebrew.autoupdate.plist
\```

Remove a job:
\```bash
launchctl unload ~/Library/LaunchAgents/local.homebrew.autoupdate.plist
rm ~/dotfiles/LaunchAgents/local.homebrew.autoupdate.plist
rm ~/Library/LaunchAgents/local.homebrew.autoupdate.plist
\```
```

## 12. Schedule Configuration Variations

### Daily at specific time
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>4</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

### Weekly on specific day (e.g., Sunday at 2:00 AM)
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Weekday</key>
    <integer>0</integer>  <!-- 0=Sunday, 1=Monday, ..., 6=Saturday -->
    <key>Hour</key>
    <integer>2</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

### Monthly on specific day (e.g., 1st of month at 3:00 AM)
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Day</key>
    <integer>1</integer>
    <key>Hour</key>
    <integer>3</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

### Multiple times (e.g., 4:00 AM and 4:00 PM)
```xml
<key>StartCalendarInterval</key>
<array>
    <dict>
        <key>Hour</key>
        <integer>4</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <dict>
        <key>Hour</key>
        <integer>16</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</array>
```

## 13. Security Considerations

1. Permissions: LaunchAgents run with user privileges (root not required)
2. Passwords: `mas upgrade` and `brew upgrade` generally do not require passwords
   - Some casks requiring `sudo` will fail (this is intentional behavior)
3. Log files: Placed in `/tmp`, periodically deleted by system
   - For persistence, change to `~/Library/Logs/`

## 14. Intel/Apple Silicon Compatibility

PATH setting in plist supports both architectures:

```xml
<key>EnvironmentVariables</key>
<dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
</dict>
```

- `/opt/homebrew/bin`: Apple Silicon
- `/usr/local/bin`: Intel
- Including both is harmless (non-existent paths are ignored)

## Implementation Plan

1. Create LaunchAgents directory
   - Create `dotfiles/LaunchAgents/` directory
   - Create `local.homebrew.autoupdate.plist` (runs mas/brew upgrade daily at 4:00 AM)

2. Modify scripts/deploy.sh
   - Add symlink handling for LaunchAgents
   - Idempotent registration with launchctl load/unload

3. Modify scripts/configure_brew.sh
   - Disable existing brew autoupdate settings (conflicts with launchd)

4. Update README.md
   - Add LaunchAgents management section
   - Document verification, testing, and removal procedures

5. Verification
   - Syntax check (plutil -lint)
   - Manual test execution (launchctl start)
   - Verify log output
