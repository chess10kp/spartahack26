export class OpenAIClient {
  private apiKey: string | null = null;

  constructor() {
    this.apiKey = this.getApiKey();
  }

  private getApiKey(): string | null {
    return process.env.OPENAI_API_KEY || null;
  }

  isConfigured(): boolean {
    return this.apiKey !== null;
  }

  async generateCompletion(prompt: string): Promise<string> {
    if (!this.apiKey) {
      throw new Error('OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.');
    }

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: 'You are an expert code challenge generator. Generate engaging, medium-difficulty coding challenges that test understanding of codebases. Always respond with valid JSON.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.8,
        max_tokens: 1500
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`OpenAI API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json() as { choices: Array<{ message: { content: string } }> };
    return data.choices[0].message.content;
  }
}
