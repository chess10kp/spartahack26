#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

pub use tauri_plugin_shell::ShellExt;

mod cmd;
