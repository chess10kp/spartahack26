import { useState } from 'react'
import { Link } from '@tanstack/react-router'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Textarea } from './ui/textarea'
import { mockCourses } from '../data/mockData'
import { ArrowLeft, Brain, Sparkles, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react'

function evaluateCourseDifficulty(course: typeof mockCourses[0]): {
  score: number
  level: string
  color: string
  factors: string[]
  recommendations: string[]
} {
  const totalHours = course.assignments.reduce((sum, a) => sum + a.estimatedHours, 0)
  const avgHours = totalHours / course.assignments.length
  const assignmentCount = course.assignments.length

  let score = 0
  const factors: string[] = []
  const recommendations: string[] = []

  if (assignmentCount > 3) {
    score += 2
    factors.push('High assignment workload')
  }
  if (avgHours > 8) {
    score += 2
    factors.push('Complex assignments requiring significant time')
    recommendations.push('Break down large assignments into smaller tasks')
  }
  if (course.credits >= 4) {
    score += 1
    factors.push('Higher credit load')
  }
  if (course.code.includes('300') || course.code.includes('400')) {
    score += 1
    factors.push('Advanced level course')
    recommendations.push('Review prerequisite materials')
  }

  score = Math.min(10, Math.max(1, score))

  let level = 'Easy'
  let color = 'bg-green-100 text-green-800'

  if (score >= 8) {
    level = 'Very Difficult'
    color = 'bg-red-100 text-red-800'
    recommendations.push('Dedicate more time per week', 'Consider dropping other commitments')
  } else if (score >= 6) {
    level = 'Difficult'
    color = 'bg-orange-100 text-orange-800'
    recommendations.push('Stay ahead of schedule', 'Form study groups')
  } else if (score >= 4) {
    level = 'Moderate'
    color = 'bg-yellow-100 text-yellow-800'
  } else {
    level = 'Easy'
    color = 'bg-green-100 text-green-800'
  }

  return { score, level, color, factors, recommendations }
}

export function Evaluation() {
  const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null)
  const [customQuery, setCustomQuery] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<string | null>(null)

  const handleAnalyze = () => {
    if (!customQuery.trim()) return
    setIsAnalyzing(true)
    setTimeout(() => {
      const course = mockCourses.find((c) => c.id === selectedCourseId)
      const analysis = course
        ? `AI Analysis for ${course.name} (${course.code}):\n\nBased on course structure and assignments:\n` +
          `- Total Estimated Workload: ${course.assignments.reduce((s, a) => s + a.estimatedHours, 0)} hours\n` +
          `- Number of Assignments: ${course.assignments.length}\n` +
          `- Average Assignment Duration: ${(course.assignments.reduce((s, a) => s + a.estimatedHours, 0) / course.assignments.length).toFixed(1)} hours\n\n` +
          `Custom Query: "${customQuery}"\n\nAI Insight: ${course.assignments.length > 3 ? 'This course requires significant time management skills. Consider creating a study schedule early in the semester.' : 'This course appears manageable with consistent weekly effort.'}`
        : 'Please select a course first.'
      setAnalysisResult(analysis)
      setIsAnalyzing(false)
    }, 1500)
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
              <h1 className="text-4xl font-bold text-slate-900">AI Course Evaluation</h1>
              <p className="text-slate-600 mt-2">Get AI-powered insights on course difficulty</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-indigo-600" />
                  Select a Course
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {mockCourses.map((course) => {
                  const evaluation = evaluateCourseDifficulty(course)
                  return (
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
                        <Badge className={evaluation.color}>{evaluation.level}</Badge>
                      </div>
                      <div className="mt-2 flex items-center gap-2 text-sm text-slate-600">
                        <TrendingUp className="w-4 h-4" />
                        <span>Difficulty Score: {evaluation.score}/10</span>
                      </div>
                    </button>
                  )
                })}
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {selectedCourseId && (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle>Detailed Analysis</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {(() => {
                      const course = mockCourses.find((c) => c.id === selectedCourseId)
                      if (!course) return null

                      const evaluation = evaluateCourseDifficulty(course)
                      return (
                        <div className="space-y-6">
                          <div className="flex items-center gap-4">
                            <div className={`w-20 h-20 rounded-full flex items-center justify-center ${evaluation.color}`}>
                              <span className="text-3xl font-bold">{evaluation.score}</span>
                            </div>
                            <div>
                              <h3 className="text-2xl font-bold text-slate-900">{evaluation.level}</h3>
                              <p className="text-slate-600">Based on AI evaluation</p>
                            </div>
                          </div>

                          <div>
                            <h4 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                              <AlertTriangle className="w-4 h-4" />
                              Difficulty Factors
                            </h4>
                            <ul className="space-y-2">
                              {evaluation.factors.map((factor, idx) => (
                                <li key={idx} className="flex items-start gap-2 text-sm text-slate-700">
                                  <span className="text-indigo-600">•</span>
                                  {factor}
                                </li>
                              ))}
                            </ul>
                          </div>

                          <div>
                            <h4 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                              <CheckCircle2 className="w-4 h-4" />
                              AI Recommendations
                            </h4>
                            <ul className="space-y-2">
                              {evaluation.recommendations.map((rec, idx) => (
                                <li key={idx} className="flex items-start gap-2 text-sm text-slate-700">
                                  <span className="text-green-600">✓</span>
                                  {rec}
                                </li>
                              ))}
                            </ul>
                          </div>

                          <div className="p-4 bg-slate-50 rounded-lg">
                            <h4 className="font-semibold text-slate-900 mb-2">Course Statistics</h4>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <span className="text-slate-600">Total Workload:</span>
                                <span className="ml-2 font-medium">{course.assignments.reduce((s, a) => s + a.estimatedHours, 0)} hours</span>
                              </div>
                              <div>
                                <span className="text-slate-600">Assignments:</span>
                                <span className="ml-2 font-medium">{course.assignments.length}</span>
                              </div>
                              <div>
                                <span className="text-slate-600">Avg Hours/Assignment:</span>
                                <span className="ml-2 font-medium">
                                  {(course.assignments.reduce((s, a) => s + a.estimatedHours, 0) / course.assignments.length).toFixed(1)}h
                                </span>
                              </div>
                              <div>
                                <span className="text-slate-600">Credits:</span>
                                <span className="ml-2 font-medium">{course.credits}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )
                    })()}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="w-5 h-5 text-indigo-600" />
                      Ask AI a Question
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Textarea
                      placeholder="Ask a specific question about this course..."
                      value={customQuery}
                      onChange={(e) => setCustomQuery(e.target.value)}
                      rows={3}
                    />
                    <Button
                      onClick={handleAnalyze}
                      disabled={!customQuery.trim() || isAnalyzing}
                      className="w-full"
                    >
                      {isAnalyzing ? (
                        <>
                          <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4 mr-2" />
                          Get AI Insight
                        </>
                      )}
                    </Button>
                    {analysisResult && (
                      <div className="mt-4 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
                        <h4 className="font-semibold text-indigo-900 mb-2">AI Response</h4>
                        <pre className="text-sm text-slate-800 whitespace-pre-wrap font-sans">{analysisResult}</pre>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </>
            )}

            {!selectedCourseId && (
              <Card>
                <CardContent className="py-12 text-center">
                  <Brain className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <p className="text-slate-600">Select a course from the list to see AI evaluation</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
