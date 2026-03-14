use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;

/// Git configuration settings
/// #[derive(...)] automatically implements traits (like Python decorators)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GitConfig {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub email: Option<String>,
}

/// A client configuration (contains git, gcloud, aws in future)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClientConfig {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub git: Option<GitConfig>,
}

/// Root configuration structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    #[serde(default)]
    pub clients: HashMap<String, ClientConfig>,
}

/// Get the path to the config file
pub fn config_path() -> PathBuf {
    // Rust's ? operator: if home_dir() returns None, return early with error
    let home = home::home_dir().expect("Could not determine home directory");
    home.join(".config/hats/config.toml")
}

/// Load configuration from disk
/// Result<Config, anyhow::Error> is like Python's return type + raises
pub fn load_config() -> Result<Config> {
    let path = config_path();

    // If file doesn't exist, return empty config
    if !path.exists() {
        return Ok(Config {
            clients: HashMap::new(),
        });
    }

    // Read file to string
    // .context() adds context to errors (like "while doing X")
    let contents = fs::read_to_string(&path)
        .context("Failed to read config file")?;

    // Parse TOML
    let config: Config = toml::from_str(&contents)
        .context("Failed to parse config file")?;

    Ok(config)
}

/// Save configuration to disk
fn save_config(config: &Config) -> Result<()> {
    let path = config_path();

    // Create parent directory if it doesn't exist
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)
            .context("Failed to create config directory")?;
    }

    // Serialize to TOML
    let contents = toml::to_string_pretty(config)
        .context("Failed to serialize config")?;

    // Write to file
    fs::write(&path, contents)
        .context("Failed to write config file")?;

    Ok(())
}

/// Get a specific client configuration
pub fn get_client(name: &str) -> Result<ClientConfig> {
    let config = load_config()?;

    config.clients.get(name)
        .cloned() // Clone the value (Rust doesn't allow moving from HashMap)
        .ok_or_else(|| {
            let available: Vec<&String> = config.clients.keys().collect();
            let available_str = if available.is_empty() {
                "(none)".to_string()
            } else {
                available.iter()
                    .map(|s| s.as_str())
                    .collect::<Vec<_>>()
                    .join(", ")
            };
            anyhow::anyhow!("Client '{}' not found. Available: {}", name, available_str)
        })
}

/// Create a new client
pub fn create_client(name: &str, client_config: ClientConfig) -> Result<()> {
    let mut config = load_config()?;

    // Check if client already exists
    if config.clients.contains_key(name) {
        anyhow::bail!("Client '{}' already exists", name);
    }

    config.clients.insert(name.to_string(), client_config);
    save_config(&config)?;

    Ok(())
}

/// Update an existing client
pub fn update_client(name: &str, client_config: ClientConfig) -> Result<()> {
    let mut config = load_config()?;

    // Check if client exists
    if !config.clients.contains_key(name) {
        let available: Vec<&String> = config.clients.keys().collect();
        let available_str = if available.is_empty() {
            "(none)".to_string()
        } else {
            available.iter()
                .map(|s| s.as_str())
                .collect::<Vec<_>>()
                .join(", ")
        };
        anyhow::bail!("Client '{}' not found. Available: {}", name, available_str);
    }

    config.clients.insert(name.to_string(), client_config);
    save_config(&config)?;

    Ok(())
}

/// Delete a client
pub fn delete_client(name: &str) -> Result<()> {
    let mut config = load_config()?;

    // Check if client exists
    if !config.clients.contains_key(name) {
        let available: Vec<&String> = config.clients.keys().collect();
        let available_str = if available.is_empty() {
            "(none)".to_string()
        } else {
            available.iter()
                .map(|s| s.as_str())
                .collect::<Vec<_>>()
                .join(", ")
        };
        anyhow::bail!("Client '{}' not found. Available: {}", name, available_str);
    }

    config.clients.remove(name);
    save_config(&config)?;

    Ok(())
}

/// List all client names
pub fn list_clients() -> Result<Vec<String>> {
    let config = load_config()?;
    let mut names: Vec<String> = config.clients.keys().cloned().collect();
    names.sort();
    Ok(names)
}
