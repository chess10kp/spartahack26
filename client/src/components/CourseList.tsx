import { Link } from '@tanstack/react-router'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { mockCourses } from '../data/mockData'
import { Calendar, Clock, BookOpen, Brain } from 'lucide-react'

export function CourseList() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">Course Dashboard</h1>
            <p className="text-slate-600 mt-2">Track your courses and assignments</p>
          </div>
          <div className="flex gap-3">
            <Link to="/quiz/create">
              <Button variant="outline" className="flex items-center gap-2">
                <Brain className="w-4 h-4" />
                AI Quiz Creator
              </Button>
            </Link>
            <Link to="/evaluation">
              <Button variant="outline" className="flex items-center gap-2">
                <BookOpen className="w-4 h-4" />
                AI Evaluation
              </Button>
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mockCourses.map((course) => (
            <Card key={course.id} className="hover:shadow-lg transition-shadow duration-300">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-xl">{course.name}</CardTitle>
                    <p className="text-sm text-slate-500 mt-1">{course.code}</p>
                  </div>
                  <Badge variant="secondary">{course.credits} Credits</Badge>
                </div>
                <p className="text-sm text-slate-600">
                  <span className="font-medium">Instructor:</span> {course.instructor}
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm text-slate-600">
                    <span className="flex items-center gap-1">
                      <BookOpen className="w-4 h-4" />
                      {course.assignments.length} Assignments
                    </span>
                  </div>

                  <div className="space-y-2 mt-4">
                    <p className="text-sm font-medium text-slate-700">Upcoming Assignments:</p>
                    {course.assignments.slice(0, 3).map((assignment) => (
                      <div
                        key={assignment.id}
                        className="p-3 bg-slate-50 rounded-lg border border-slate-200"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="text-sm font-medium text-slate-800">{assignment.name}</p>
                            <p className="text-xs text-slate-600 mt-1 line-clamp-2">
                              {assignment.description}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {new Date(assignment.dueDate).toLocaleDateString()}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {assignment.estimatedHours}h
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
