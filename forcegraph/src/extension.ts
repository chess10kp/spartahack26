// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
	console.log('EXTENSION ACTIVATED!');
	vscode.window.showInformationMessage('Extension activated!');

	const provider = new ForceGraphViewProvider(context.extensionUri);
	context.subscriptions.push(vscode.window.registerWebviewViewProvider('forcegraph-sidebar', provider));

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with registerCommand
	// The commandId parameter must match the command field in package.json
	const disposable = vscode.commands.registerCommand('forcegraph.helloWorld', () => {
		// The code you place here will be executed every time your command is executed
		// Display a message box to the user
		vscode.window.showInformationMessage('Hello World from forcegraph!');
	});

	const randomFile = vscode.commands.registerCommand('forcegraph.randomFile', async () => {
		vscode.window.showInformationMessage('TEST: Command is working!');
		console.log('TEST: Command is working!');
		const workspaceFolders = vscode.workspace.workspaceFolders;
		if (!workspaceFolders || workspaceFolders.length === 0) {
			console.log('No workspace folder');
			vscode.window.showErrorMessage('No workspace folder open');
			return;
		}

		const workspacePath = workspaceFolders[0].uri.fsPath;
		console.log('Workspace path:', workspacePath);
		const files = await vscode.workspace.fs.readDirectory(vscode.Uri.file(workspacePath));
		console.log('Files found:', files.length);
		const fileEntries = files.filter(([name, type]) => type === vscode.FileType.File);

		if (fileEntries.length === 0) {
			console.log('No files in directory');
			vscode.window.showInformationMessage('No files found in workspace');
			return;
		}

		const randomIndex = Math.floor(Math.random() * fileEntries.length);
		const [randomFileName] = fileEntries[randomIndex];
		const randomFilePath = vscode.Uri.file(`${workspacePath}/${randomFileName}`);
		console.log('Selected file:', randomFileName);

		const doc = await vscode.workspace.openTextDocument(randomFilePath);
		const content = doc.getText();
		const lines = content.split('\n');

		const targets: { type: string; line: number; text: string }[] = [];

		for (let i = 0; i < lines.length; i++) {
			const line = lines[i].trim();
			if (line.startsWith('export function') || line.startsWith('export class') || line.startsWith('function') || line.startsWith('class')) {
				targets.push({ type: 'function/class', line: i + 1, text: line });
			} else if (line.startsWith('export const') || line.startsWith('export let') || line.startsWith('export var')) {
				targets.push({ type: 'export', line: i + 1, text: line });
			} else if (line.startsWith('import ') && !line.includes('from')) {
				targets.push({ type: 'import', line: i + 1, text: line });
			}
		}

		console.log('Targets found:', targets.length);
		if (targets.length === 0) {
			vscode.window.showInformationMessage(`No interesting sections found in ${randomFileName}. Try another file!`);
			return;
		}

		const randomTarget = targets[Math.floor(Math.random() * targets.length)];
		await vscode.window.showTextDocument(doc, { selection: new vscode.Range(randomTarget.line - 1, 0, randomTarget.line - 1, 0) });
		vscode.window.showInformationMessage(`Find the ${randomTarget.type} on line ${randomTarget.line} in ${randomFileName}`);
	});

	context.subscriptions.push(randomFile);

	context.subscriptions.push(disposable);
}

class ForceGraphViewProvider implements vscode.WebviewViewProvider {
	constructor(private readonly extensionUri: vscode.Uri) {}

	resolveWebviewView(webviewView: vscode.WebviewView): void | Thenable<void> {
		webviewView.webview.options = { enableScripts: true };
		webviewView.webview.html = `<!DOCTYPE html>
			<html>
			<head>
				<style>
					body { font-family: Arial, sans-serif; padding: 10px; background-color: var(--vscode-panel-background); color: var(--vscode-foreground); }
					h1 { font-size: 16px; margin-bottom: 10px; color: var(--vscode-foreground); }
					.question-item {
						padding: 8px;
						margin: 5px 0;
						background-color: var(--vscode-button-background);
						color: var(--vscode-button-foreground);
						border-radius: 4px;
						cursor: pointer;
					}
					.question-item:hover { background-color: var(--vscode-button-hover-background); }
				</style>
			</head>
			<body>
				<h1>Questions</h1>
				<div id="questions"></div>
				<script>
					const questions = [
						"How are dependencies connected in the codebase?",
						"Which files are most interconnected?",
						"What are the main modules in this project?",
						"Show me the file with the most imports"
					];
					const container = document.getElementById('questions');
					questions.forEach((q, i) => {
						const div = document.createElement('div');
						div.className = 'question-item';
						div.textContent = q;
						div.onclick = () => console.log('Selected question:', i);
						container.appendChild(div);
					});
				</script>
			</body>
			</html>`;
	}
}

// This method is called when your extension is deactivated
export function deactivate() {}
