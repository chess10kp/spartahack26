use serde::Deserialize;

#[derive(Deserialize)]
pub struct GreetArgs {
    name: String,
}
