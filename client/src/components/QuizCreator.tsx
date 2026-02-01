import { useState } from 'react'
import { Link, useNavigate } from '@tanstack/react-router'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Textarea } from './ui/textarea'
import { Badge } from './ui/badge'
import { ArrowLeft, Sparkles, Brain, Plus, BookOpen, Loader2, CheckCircle2 } from 'lucide-react'
import { mockCourses, type Quiz } from '../data/mockData'

export function QuizCreator() {
  const navigate = useNavigate()
  const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null)
  const [quizTitle, setQuizTitle] = useState('')
  const [quizDescription, setQuizDescription] = useState('')
  const [difficulty, setDifficulty] = useState<'Easy' | 'Medium' | 'Hard'>('Medium')
  const [numQuestions, setNumQuestions] = useState(5)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedQuiz, setGeneratedQuiz] = useState<Quiz | null>(null)

  const handleGenerateQuiz = () => {
    if (!selectedCourseId || !quizTitle.trim()) return

    setIsGenerating(true)
    const course = mockCourses.find((c) => c.id === selectedCourseId)

    setTimeout(() => {
      const questions = Array.from({ length: numQuestions }, (_, i) => ({
        id: `q-${Date.now()}-${i}`,
        question: `AI Generated Question ${i + 1} about ${course?.name}: ${generateMockQuestion(course?.name, difficulty)}`,
        options: [
          generateMockOption(0, difficulty),
          generateMockOption(1, difficulty),
          generateMockOption(2, difficulty),
          generateMockOption(3, difficulty),
        ],
        correctAnswer: Math.floor(Math.random() * 4),
        explanation: `This is an AI-generated explanation for question ${i + 1}.`
      }))

      const newQuiz = {
        id: `quiz-${Date.now()}`,
        title: quizTitle,
        description: quizDescription || `AI-generated quiz for ${course?.name}`,
        subject: course?.name || 'General',
        difficulty,
        questions,
        createdAt: new Date().toISOString()
      }

      setGeneratedQuiz(newQuiz)
      setIsGenerating(false)
    }, 2000)
  }

  const generateMockQuestion = (_subject?: string, diff?: 'Easy' | 'Medium' | 'Hard'): string => {
    const questions = [
      'What is the primary purpose of this concept?',
      'Which of the following best describes the relationship between these elements?',
      'What would be the expected output in this scenario?',
      'Which approach is most efficient for solving this problem?',
      'What are the key characteristics of this method?'
    ]
    const levelSpecific = diff === 'Hard' ? ' (Advanced)' : diff === 'Easy' ? ' (Basic)' : ''
    return questions[Math.floor(Math.random() * questions.length)] + levelSpecific
  }

  const generateMockOption = (index: number, diff?: 'Easy' | 'Medium' | 'Hard'): string => {
    const options = ['Option A', 'Option B', 'Option C', 'Option D']
    const complexity = diff === 'Hard' ? 'Complex explanation' : 'Simple explanation'
    return `${options[index]} - ${complexity}`
  }

  const handleTakeQuiz = () => {
    if (generatedQuiz) {
      navigate({ to: '/evaluation', search: { mode: 'quiz', quizId: generatedQuiz.id } })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Link to="/">
            <Button variant="ghost" className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Courses
            </Button>
          </Link>
          <div className="flex items-center gap-3">
            <Brain className="w-8 h-8 text-indigo-600" />
            <div>
              <h1 className="text-4xl font-bold text-slate-900">AI Quiz Creator</h1>
              <p className="text-slate-600 mt-2">Generate AI-powered quizzes for your courses</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-indigo-600" />
                  Select Course
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {mockCourses.map((course) => (
                  <button
                    key={course.id}
                    onClick={() => setSelectedCourseId(course.id)}
                    className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                      selectedCourseId === course.id
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-slate-900">{course.name}</p>
                        <p className="text-sm text-slate-600">{course.code}</p>
                      </div>
                      <Badge variant="secondary">{course.credits} Credits</Badge>
                    </div>
                  </button>
                ))}
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-indigo-600" />
                  Quiz Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Quiz Title</label>
                  <Input
                    placeholder="Enter quiz title..."
                    value={quizTitle}
                    onChange={(e) => setQuizTitle(e.target.value)}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Description (Optional)</label>
                  <Textarea
                    placeholder="Describe what this quiz covers..."
                    value={quizDescription}
                    onChange={(e) => setQuizDescription(e.target.value)}
                    rows={2}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Difficulty</label>
                  <div className="flex gap-2">
                    {(['Easy', 'Medium', 'Hard'] as const).map((level) => (
                      <Button
                        key={level}
                        variant={difficulty === level ? 'default' : 'outline'}
                        onClick={() => setDifficulty(level)}
                        className="flex-1"
                      >
                        {level}
                      </Button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Number of Questions</label>
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min="3"
                      max="20"
                      value={numQuestions}
                      onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                      className="flex-1"
                    />
                    <Badge variant="outline" className="text-lg px-4 py-1">
                      {numQuestions}
                    </Badge>
                  </div>
                </div>

                <Button
                  onClick={handleGenerateQuiz}
                  disabled={!selectedCourseId || !quizTitle.trim() || isGenerating}
                  className="w-full"
                  size="lg"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Generating Quiz...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5 mr-2" />
                      Generate AI Quiz
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {generatedQuiz && (
              <Card className="border-green-200 bg-green-50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-900">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    Quiz Generated Successfully!
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="text-xl font-bold text-slate-900">{generatedQuiz.title}</h3>
                    <p className="text-slate-600 mt-1">{generatedQuiz.description}</p>
                  </div>
                  <div className="flex gap-3">
                    <Badge variant="secondary">{generatedQuiz.difficulty}</Badge>
                    <Badge variant="outline">{generatedQuiz.questions.length} Questions</Badge>
                  </div>
                  <Button onClick={handleTakeQuiz} className="w-full" size="lg">
                    <Plus className="w-5 h-5 mr-2" />
                    Start Quiz
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
