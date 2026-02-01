export class GeminiClient {
  private apiKey: string | null = null;

  constructor() {
    this.apiKey = this.getApiKey();
  }

  private getApiKey(): string | null {
    return process.env.GEMINI_API_KEY || null;
  }

  isConfigured(): boolean {
    return this.apiKey !== null;
  }

  async generateCompletion(prompt: string): Promise<string> {
    if (!this.apiKey) {
      throw new Error('Gemini API key not configured. Please set GEMINI_API_KEY environment variable.');
    }

    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=${this.apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        contents: [
          {
            parts: [
              {
                text: `You are an expert code challenge generator. Generate engaging, medium-difficulty coding challenges that test understanding of codebases. Always respond with valid JSON.\n\n${prompt}`
              }
            ]
          }
        ],
        generationConfig: {
          temperature: 0.8,
          maxOutputTokens: 1500,
          responseMimeType: "application/json"
        }
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Gemini API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json() as { candidates: Array<{ content: { parts: Array<{ text: string }> }> } };
    
    if (!data.candidates || data.candidates.length === 0) {
      throw new Error('No response from Gemini API');
    }

    return data.candidates[0].content.parts[0].text;
  }
}
