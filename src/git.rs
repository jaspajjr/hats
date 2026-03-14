use anyhow::{Context, Result};
use std::process::Command;

use crate::config::GitConfig;

/// Get current git user configuration
pub fn get_status() -> Result<GitConfig> {
    let name = get_git_config("user.name")?;
    let email = get_git_config("user.email")?;

    Ok(GitConfig { name, email })
}

/// Apply git configuration
pub fn apply(config: &GitConfig) -> Result<()> {
    if let Some(name) = &config.name {
        set_git_config("user.name", name)?;
    }

    if let Some(email) = &config.email {
        set_git_config("user.email", email)?;
    }

    Ok(())
}

/// Get a git config value
/// Returns None if the key is not set
fn get_git_config(key: &str) -> Result<Option<String>> {
    // Run: git config --global --get <key>
    let output = Command::new("git")
        .args(["config", "--global", "--get", key])
        .output()
        .context("Failed to run git command")?;

    // Exit code 1 means key not found (not an error for us)
    if !output.status.success() {
        return Ok(None);
    }

    // Convert output bytes to String and trim whitespace
    let value = String::from_utf8(output.stdout)
        .context("Git config value is not valid UTF-8")?
        .trim()
        .to_string();

    Ok(if value.is_empty() {
        None
    } else {
        Some(value)
    })
}

/// Set a git config value
fn set_git_config(key: &str, value: &str) -> Result<()> {
    // Run: git config --global <key> <value>
    let status = Command::new("git")
        .args(["config", "--global", key, value])
        .status()
        .context("Failed to run git command")?;

    if !status.success() {
        anyhow::bail!("Failed to set git config {}", key);
    }

    Ok(())
}
