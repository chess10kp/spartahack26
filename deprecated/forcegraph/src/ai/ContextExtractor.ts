import * as vscode from 'vscode';
import * as path from 'path';
import { CodeContext, FileContext, FunctionInfo, ClassInfo } from '../types';

const IGNORED_DIRECTORIES = ['node_modules', 'dist', 'out', 'build', '.git', '.vscode', 'coverage', '__tests__', 'test', 'tests'];
const IGNORED_FILE_PATTERNS = [/\.test\.(ts|js|tsx|jsx)$/, /\.spec\.(ts|js|tsx|jsx)$/, /\.d\.ts$/, /\.map$/];
const MAX_FILES_TO_ANALYZE = 20;
const MAX_FILE_SIZE = 50000;

export class ContextExtractor {
  async extractContext(workspaceFolders: readonly vscode.WorkspaceFolder[]): Promise<CodeContext> {
    const files: FileContext[] = [];

    for (const folder of workspaceFolders) {
      const folderFiles = await this.scanFolder(folder.uri);
      files.push(...folderFiles);
    }

    return {
      files: files.slice(0, MAX_FILES_TO_ANALYZE),
      projectStructure: this.buildProjectStructure(files),
      language: this.detectPrimaryLanguage(files),
      frameworks: this.detectFrameworks(files)
    };
  }

  private async scanFolder(folderUri: vscode.Uri): Promise<FileContext[]> {
    const contexts: FileContext[] = [];
    const files = await this.getAllFiles(folderUri.fsPath);

    for (const file of files) {
      if (this.shouldIgnoreFile(file)) {
        continue;
      }

      const context = await this.analyzeFile(file);
      if (context) {
        contexts.push(context);
      }
    }

    return contexts;
  }

  private async getAllFiles(dirPath: string): Promise<string[]> {
    const files: string[] = [];
    const entries = await vscode.workspace.fs.readDirectory(vscode.Uri.file(dirPath));

    for (const [name, type] of entries) {
      const fullPath = path.join(dirPath, name);

      if (type === vscode.FileType.Directory) {
        if (IGNORED_DIRECTORIES.includes(name)) {
          continue;
        }
        files.push(...await this.getAllFiles(fullPath));
      } else if (type === vscode.FileType.File) {
        files.push(fullPath);
      }
    }

    return files;
  }

  private shouldIgnoreFile(filePath: string): boolean {
    const basename = path.basename(filePath);
    return IGNORED_FILE_PATTERNS.some(pattern => pattern.test(basename));
  }

  private async analyzeFile(filePath: string): Promise<FileContext | null> {
    try {
      const uri = vscode.Uri.file(filePath);
      const stat = await vscode.workspace.fs.stat(uri);

      if (stat.size > MAX_FILE_SIZE) {
        return null;
      }

      const document = await vscode.workspace.openTextDocument(uri);
      const content = document.getText();
      const lines = content.split('\n');
      const language = document.languageId;

      const fileContext: FileContext = {
        path: filePath,
        language,
        exports: [],
        imports: [],
        functions: [],
        classes: [],
        lineCount: lines.length
      };

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        const lineNum = i + 1;

        if (line.startsWith('export function') || line.startsWith('function')) {
          const funcMatch = line.match(/(?:export\s+)?function\s+(\w+)/);
          if (funcMatch) {
            fileContext.exports.push(funcMatch[1]);
            fileContext.functions.push({
              name: funcMatch[1],
              line: lineNum,
              parameters: []
            });
          }
        } else if (line.startsWith('export class') || line.startsWith('class')) {
          const classMatch = line.match(/(?:export\s+)?class\s+(\w+)/);
          if (classMatch) {
            fileContext.classes.push({
              name: classMatch[1],
              line: lineNum,
              methods: [],
              properties: []
            });
            fileContext.exports.push(classMatch[1]);
          }
        } else if (line.startsWith('export const') || line.startsWith('const')) {
          const exportMatch = line.match(/(?:export\s+)?(?:const|let|var)\s+(\w+)/);
          if (exportMatch) {
            fileContext.exports.push(exportMatch[1]);
          }
        } else if (line.startsWith('import')) {
          const importMatch = line.match(/import\s+(?:\{[^}]+\}|\*\s+as\s+\w+|\w+)\s+from\s+['"]([^'"]+)['"]/);
          if (importMatch) {
            fileContext.imports.push(importMatch[1]);
          }
        } else if (line.startsWith('export default')) {
          fileContext.exports.push('default');
        }
      }

      if (fileContext.exports.length === 0 && fileContext.functions.length === 0 && fileContext.classes.length === 0) {
        return null;
      }

      return fileContext;
    } catch (error) {
      return null;
    }
  }

  private buildProjectStructure(files: FileContext[]): string {
    const paths = files.map(f => f.path);
    return paths.join('\n');
  }

  private detectPrimaryLanguage(files: FileContext[]): string {
    const languageCounts = new Map<string, number>();

    for (const file of files) {
      const count = languageCounts.get(file.language) || 0;
      languageCounts.set(file.language, count + 1);
    }

    let maxCount = 0;
    let primaryLanguage = 'unknown';

    for (const [language, count] of languageCounts) {
      if (count > maxCount) {
        maxCount = count;
        primaryLanguage = language;
      }
    }

    return primaryLanguage;
  }

  private detectFrameworks(files: FileContext[]): string[] {
    const frameworks = new Set<string>();
    const frameworksMap: Record<string, string[]> = {
      'typescript': [],
      'javascript': ['react', 'vue', 'angular'],
      'python': ['django', 'flask', 'fastapi'],
      'rust': [],
      'go': []
    };

    for (const file of files) {
      for (const imp of file.imports) {
        for (const framework of Object.values(frameworksMap).flat()) {
          if (imp.includes(framework)) {
            frameworks.add(framework);
          }
        }
      }
    }

    return Array.from(frameworks);
  }
}
