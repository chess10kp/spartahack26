// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
async fn capture_screenshot() -> Result<String, String> {
    use std::process::Command;
    
    let output = Command::new("import")
        .arg("-window")
        .arg("root")
        .arg("-silent")
        .arg("/tmp/screenshot.png")
        .output();
    
    match output {
        Ok(_) => Ok("/tmp/screenshot.png".to_string()),
        Err(e) => Err(format!("Failed to capture screenshot: {}", e))
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet, capture_screenshot])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
