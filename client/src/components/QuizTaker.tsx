import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Progress } from './ui/progress'
import { ArrowLeft, CheckCircle2, XCircle, Lightbulb, Clock, Trophy } from 'lucide-react'

export function QuizTaker() {
  const navigate = useNavigate()
  const [quiz] = useState({
    id: '1',
    title: 'JavaScript Fundamentals',
    description: 'Test your knowledge of basic JavaScript concepts',
    subject: 'Web Development',
    difficulty: 'Easy' as const,
    questions: [
      {
        id: '1-1',
        question: 'Which keyword is used to declare a constant in JavaScript?',
        options: ['var', 'let', 'const', 'constant'],
        correctAnswer: 2,
        explanation: 'const is used to declare constants in JavaScript, which cannot be reassigned.'
      },
      {
        id: '1-2',
        question: 'What does DOM stand for?',
        options: ['Data Object Model', 'Document Object Model', 'Digital Ordinance Model', 'Document Orientation Model'],
        correctAnswer: 1,
        explanation: 'DOM stands for Document Object Model, which represents the HTML structure.'
      },
      {
        id: '1-3',
        question: 'Which method is used to add an element at the end of an array?',
        options: ['push()', 'pop()', 'shift()', 'unshift()'],
        correctAnswer: 0,
        explanation: 'push() adds one or more elements to the end of an array.'
      },
      {
        id: '1-4',
        question: 'What is the output of typeof null in JavaScript?',
        options: ['"null"', '"undefined"', '"object"', '"boolean"'],
        correctAnswer: 2,
        explanation: 'typeof null returns "object", which is a known bug in JavaScript.'
      },
      {
        id: '1-5',
        question: 'Which function is used to parse a string into an integer?',
        options: ['parseInt()', 'parseFloat()', 'Number()', 'parseInt() and Number()'],
        correctAnswer: 3,
        explanation: 'Both parseInt() and Number() can parse strings into integers, but parseInt() is more flexible.'
      }
    ],
    createdAt: '2025-01-15'
  })

  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({})
  const [showResults, setShowResults] = useState(false)
  const [showExplanation, setShowExplanation] = useState(false)
  const [answeredQuestions, setAnsweredQuestions] = useState<Record<string, boolean>>({})

  const currentQuestion = quiz.questions[currentQuestionIndex]
  const progress = ((currentQuestionIndex + 1) / quiz.questions.length) * 100

  const handleAnswerSelect = (optionIndex: number) => {
    if (answeredQuestions[currentQuestion.id]) return

    setSelectedAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: optionIndex,
    }))
    setAnsweredQuestions((prev) => ({
      ...prev,
      [currentQuestion.id]: true,
    }))
    setShowExplanation(true)
  }

  const handleNextQuestion = () => {
    setShowExplanation(false)
    if (currentQuestionIndex < quiz.questions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1)
    } else {
      setShowResults(true)
    }
  }

  const handlePreviousQuestion = () => {
    setShowExplanation(false)
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex((prev) => prev - 1)
    }
  }

  const calculateScore = () => {
    let correct = 0
    quiz.questions.forEach((question) => {
      if (selectedAnswers[question.id] === question.correctAnswer) {
        correct++
      }
    })
    return correct
  }

  const getScoreColor = (score: number, total: number) => {
    const percentage = (score / total) * 100
    if (percentage >= 80) return 'text-green-600'
    if (percentage >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreMessage = (score: number, total: number) => {
    const percentage = (score / total) * 100
    if (percentage >= 80) return 'Excellent work!'
    if (percentage >= 60) return 'Good job!'
    return 'Keep practicing!'
  }

  if (showResults) {
    const score = calculateScore()
    const percentage = Math.round((score / quiz.questions.length) * 100)

    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto">
            <div className="mb-8">
              <Button variant="ghost" onClick={() => navigate({ to: '/evaluation' })} className="mb-4">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Quiz
              </Button>
            </div>

            <Card className="text-center">
              <CardHeader>
                <div className="flex justify-center mb-4">
                  <div className={`w-32 h-32 rounded-full flex items-center justify-center ${getScoreColor(score, quiz.questions.length)} bg-opacity-10`}>
                    <Trophy className={`w-16 h-16 ${getScoreColor(score, quiz.questions.length)}`} />
                  </div>
                </div>
                <CardTitle className="text-3xl">Quiz Complete!</CardTitle>
                <p className="text-slate-600 mt-2">{quiz.title}</p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex justify-center gap-8">
                  <div className="text-center">
                    <p className="text-5xl font-bold">{score}</p>
                    <p className="text-slate-600 mt-1">Correct</p>
                  </div>
                  <div className="text-4xl text-slate-300">/</div>
                  <div className="text-center">
                    <p className="text-5xl font-bold text-slate-400">{quiz.questions.length}</p>
                    <p className="text-slate-600 mt-1">Total</p>
                  </div>
                </div>

                <div className="p-4 bg-slate-50 rounded-lg">
                  <p className={`text-2xl font-bold ${getScoreColor(score, quiz.questions.length)}`}>
                    {percentage}%
                  </p>
                  <p className="text-slate-600 mt-1">{getScoreMessage(score, quiz.questions.length)}</p>
                </div>

                <div className="space-y-2">
                  <h4 className="font-semibold text-slate-900">Review Your Answers</h4>
                  {quiz.questions.map((question, idx) => {
                    const isCorrect = selectedAnswers[question.id] === question.correctAnswer
                    return (
                      <div key={question.id} className="flex items-center gap-3 p-3 bg-white rounded-lg border border-slate-200">
                        {isCorrect ? (
                          <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                        )}
                        <div className="flex-1 text-left">
                          <p className="text-sm font-medium text-slate-900">
                            Question {idx + 1}: {question.question.substring(0, 60)}...
                          </p>
                        </div>
                        <Badge variant={isCorrect ? 'default' : 'destructive'}>
                          {isCorrect ? 'Correct' : 'Incorrect'}
                        </Badge>
                      </div>
                    )
                  })}
                </div>

                <div className="flex gap-3">
                  <Button onClick={() => navigate({ to: '/evaluation' })} className="flex-1">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back to Quizzes
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setCurrentQuestionIndex(0)
                      setSelectedAnswers({})
                      setAnsweredQuestions({})
                      setShowResults(false)
                      setShowExplanation(false)
                    }}
                    className="flex-1"
                  >
                    Retake Quiz
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <div className="mb-8">
            <Button variant="ghost" onClick={() => navigate({ to: '/evaluation' })} className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Quiz
            </Button>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-slate-900">{quiz.title}</h1>
                <p className="text-slate-600 mt-1">{quiz.description}</p>
              </div>
              <div className="flex gap-2">
                <Badge variant="secondary">{quiz.difficulty}</Badge>
                <Badge variant="outline">
                  <Clock className="w-3 h-3 mr-1" />
                  {currentQuestionIndex + 1}/{quiz.questions.length}
                </Badge>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <Progress value={progress} className="h-2" />
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">Question {currentQuestionIndex + 1}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <p className="text-lg text-slate-900 font-medium">{currentQuestion.question}</p>

              <div className="space-y-3">
                {currentQuestion.options.map((option, idx) => {
                  const isSelected = selectedAnswers[currentQuestion.id] === idx
                  const isCorrect = currentQuestion.correctAnswer === idx
                  const isWrong = isSelected && !isCorrect

                  return (
                    <button
                      key={idx}
                      onClick={() => handleAnswerSelect(idx)}
                      disabled={answeredQuestions[currentQuestion.id]}
                      className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                        answeredQuestions[currentQuestion.id] && isCorrect
                          ? 'border-green-500 bg-green-50'
                          : isWrong
                          ? 'border-red-500 bg-red-50'
                          : isSelected
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-slate-200 hover:border-slate-300'
                      } ${answeredQuestions[currentQuestion.id] ? 'cursor-not-allowed opacity-70' : 'cursor-pointer'}`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                          answeredQuestions[currentQuestion.id] && isCorrect
                            ? 'bg-green-500 text-white'
                            : isWrong
                            ? 'bg-red-500 text-white'
                            : isSelected
                            ? 'bg-indigo-500 text-white'
                            : 'bg-slate-200 text-slate-700'
                        }`}>
                          {answeredQuestions[currentQuestion.id] && isCorrect ? (
                            <CheckCircle2 className="w-5 h-5" />
                          ) : isWrong ? (
                            <XCircle className="w-5 h-5" />
                          ) : (
                            <span className="font-medium">{String.fromCharCode(65 + idx)}</span>
                          )}
                        </div>
                        <span className="text-slate-900">{option}</span>
                      </div>
                    </button>
                  )
                })}
              </div>

              {showExplanation && answeredQuestions[currentQuestion.id] && (
                <div className="p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
                  <div className="flex items-start gap-2">
                    <Lightbulb className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-indigo-900">Explanation</h4>
                      <p className="text-sm text-slate-800 mt-1">{currentQuestion.explanation}</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="flex justify-between pt-4">
                <Button
                  variant="outline"
                  onClick={handlePreviousQuestion}
                  disabled={currentQuestionIndex === 0}
                >
                  Previous
                </Button>
                {answeredQuestions[currentQuestion.id] ? (
                  <Button onClick={handleNextQuestion}>
                    {currentQuestionIndex < quiz.questions.length - 1 ? 'Next Question' : 'See Results'}
                  </Button>
                ) : (
                  <Button disabled>
                    Select an answer to continue
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
