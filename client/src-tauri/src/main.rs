#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn close_splashscreen(window: tauri::Window) {
    if let Some(splashscreen) = window.get_webview_window("splashscreen") {
        splashscreen.close().unwrap();
    }
    if let Some(main) = window.get_webview_window("main") {
        main.show().unwrap();
    }
}

#[tauri::command]
fn open_external_url(window: tauri::Window, url: String) {
    let _ = tauri::api::shell::open(&window.shell_scope(), url, None);
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            greet,
            close_splashscreen,
            open_external_url
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
