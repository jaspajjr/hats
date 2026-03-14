// Declare modules
mod config;
mod git;

use anyhow::Result;
use clap::{Parser, Subcommand};
use dialoguer::Input;

/// Manage authentication context across clients and projects
#[derive(Parser)]
#[command(name = "hats")]
#[command(about = "Switch authentication context between clients", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

/// CLI subcommands (like @app.command() in Python's typer)
#[derive(Subcommand)]
enum Commands {
    /// List available client contexts
    List,

    /// Show current git identity
    Status,

    /// Switch to a named client context
    Use {
        /// Client name to switch to
        client: String,
    },

    /// Show configuration for a named client
    Show {
        /// Client name to show
        client: String,
    },

    /// Create a new client context
    Create {
        /// Client name to create
        client: String,

        /// Git user name
        #[arg(long)]
        git_name: Option<String>,

        /// Git user email
        #[arg(long)]
        git_email: Option<String>,
    },

    /// Update an existing client context
    Update {
        /// Client name to update
        client: String,

        /// Git user name
        #[arg(long)]
        git_name: Option<String>,

        /// Git user email
        #[arg(long)]
        git_email: Option<String>,
    },

    /// Delete a client context
    Delete {
        /// Client name to delete
        client: String,

        /// Skip confirmation prompt
        #[arg(short, long)]
        yes: bool,
    },
}

fn main() {
    // Parse CLI arguments
    let cli = Cli::parse();

    // Run the appropriate command and handle errors
    if let Err(e) = run_command(cli.command) {
        eprintln!("{:#}", e); // Pretty-print error with context chain
        std::process::exit(1);
    }
}

/// Run the selected command
fn run_command(command: Commands) -> Result<()> {
    match command {
        Commands::List => cmd_list(),
        Commands::Status => cmd_status(),
        Commands::Use { client } => cmd_use(&client),
        Commands::Show { client } => cmd_show(&client),
        Commands::Create {
            client,
            git_name,
            git_email,
        } => cmd_create(&client, git_name, git_email),
        Commands::Update {
            client,
            git_name,
            git_email,
        } => cmd_update(&client, git_name, git_email),
        Commands::Delete { client, yes } => cmd_delete(&client, yes),
    }
}

fn cmd_list() -> Result<()> {
    let clients = config::list_clients()?;

    if clients.is_empty() {
        println!("No clients configured.");
        return Ok(());
    }

    for client in clients {
        println!("{}", client);
    }

    Ok(())
}

fn cmd_status() -> Result<()> {
    let info = git::get_status()?;

    println!("name:  {}", info.name.unwrap_or_else(|| "(not set)".to_string()));
    println!("email: {}", info.email.unwrap_or_else(|| "(not set)".to_string()));

    Ok(())
}

fn cmd_use(client: &str) -> Result<()> {
    let client_cfg = config::get_client(client)?;

    if let Some(git_cfg) = &client_cfg.git {
        git::apply(git_cfg)?;
        println!("Switched to '{}'.", client);
        println!(
            "  git name:  {}",
            git_cfg.name.as_deref().unwrap_or("(unchanged)")
        );
        println!(
            "  git email: {}",
            git_cfg.email.as_deref().unwrap_or("(unchanged)")
        );
    } else {
        println!("No git config for client '{}'.", client);
    }

    Ok(())
}

fn cmd_show(client: &str) -> Result<()> {
    let client_cfg = config::get_client(client)?;

    println!("[{}]", client);
    if let Some(git_cfg) = &client_cfg.git {
        println!(
            "  git name:  {}",
            git_cfg.name.as_deref().unwrap_or("(not set)")
        );
        println!(
            "  git email: {}",
            git_cfg.email.as_deref().unwrap_or("(not set)")
        );
    } else {
        println!("  (no settings)");
    }

    Ok(())
}

fn cmd_create(client: &str, git_name: Option<String>, git_email: Option<String>) -> Result<()> {
    // Interactive prompts when flags not provided
    let git_name = if git_name.is_none() {
        let input: String = Input::new()
            .with_prompt("Git user name")
            .allow_empty(true)
            .interact_text()?;
        if input.is_empty() {
            None
        } else {
            Some(input)
        }
    } else {
        git_name
    };

    let git_email = if git_email.is_none() {
        let input: String = Input::new()
            .with_prompt("Git user email")
            .allow_empty(true)
            .interact_text()?;
        if input.is_empty() {
            None
        } else {
            Some(input)
        }
    } else {
        git_email
    };

    // Build client config
    let client_cfg = config::ClientConfig {
        git: if git_name.is_some() || git_email.is_some() {
            Some(config::GitConfig { name: git_name, email: git_email })
        } else {
            None
        },
    };

    config::create_client(client, client_cfg)?;
    println!("Created client '{}'.", client);

    Ok(())
}

fn cmd_update(client: &str, git_name: Option<String>, git_email: Option<String>) -> Result<()> {
    // Get current config to show as defaults
    let current_cfg = config::get_client(client).ok();
    let current_git = current_cfg.as_ref().and_then(|c| c.git.as_ref());

    // Interactive prompts when flags not provided
    let git_name = if git_name.is_none() {
        let current_name = current_git.and_then(|g| g.name.as_deref()).unwrap_or("");
        let mut input_prompt = Input::new()
            .with_prompt("Git user name")
            .allow_empty(true);
        if !current_name.is_empty() {
            input_prompt = input_prompt.default(current_name.to_string());
        }
        let input: String = input_prompt.interact_text()?;
        if input.is_empty() {
            None
        } else {
            Some(input)
        }
    } else {
        git_name
    };

    let git_email = if git_email.is_none() {
        let current_email = current_git.and_then(|g| g.email.as_deref()).unwrap_or("");
        let mut input_prompt = Input::new()
            .with_prompt("Git user email")
            .allow_empty(true);
        if !current_email.is_empty() {
            input_prompt = input_prompt.default(current_email.to_string());
        }
        let input: String = input_prompt.interact_text()?;
        if input.is_empty() {
            None
        } else {
            Some(input)
        }
    } else {
        git_email
    };

    // Build client config
    let client_cfg = config::ClientConfig {
        git: if git_name.is_some() || git_email.is_some() {
            Some(config::GitConfig { name: git_name, email: git_email })
        } else {
            None
        },
    };

    config::update_client(client, client_cfg)?;
    println!("Updated client '{}'.", client);

    Ok(())
}

fn cmd_delete(client: &str, yes: bool) -> Result<()> {
    if !yes {
        let confirm = dialoguer::Confirm::new()
            .with_prompt(format!("Delete client '{}'?", client))
            .interact()?;

        if !confirm {
            println!("Cancelled.");
            return Ok(());
        }
    }

    config::delete_client(client)?;
    println!("Deleted client '{}'.", client);

    Ok(())
}
