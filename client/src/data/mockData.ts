export interface Assignment {
  id: string
  name: string
  dueDate: string
  description: string
  estimatedHours: number
}

export interface Course {
  id: string
  name: string
  code: string
  instructor: string
  credits: number
  assignments: Assignment[]
  difficulty?: number
}

export interface QuizQuestion {
  id: string
  question: string
  options: string[]
  correctAnswer: number
  explanation?: string
}

export interface Quiz {
  id: string
  title: string
  description: string
  subject: string
  difficulty: 'Easy' | 'Medium' | 'Hard'
  questions: QuizQuestion[]
  createdAt: string
}

export const mockQuizzes: Quiz[] = [
  {
    id: '1',
    title: 'JavaScript Fundamentals',
    description: 'Test your knowledge of basic JavaScript concepts',
    subject: 'Web Development',
    difficulty: 'Easy',
    createdAt: '2025-01-15',
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
      }
    ]
  }
]

export const mockCourses: Course[] = [
  {
    id: '1',
    name: 'Introduction to Computer Science',
    code: 'CS 101',
    instructor: 'Dr. Smith',
    credits: 4,
    assignments: [
      {
        id: '1-1',
        name: 'Hello World Program',
        dueDate: '2025-02-15',
        description: 'Write your first program in Python',
        estimatedHours: 2,
      },
      {
        id: '1-2',
        name: 'Variables and Data Types Quiz',
        dueDate: '2025-02-22',
        description: 'Multiple choice quiz on basic data types',
        estimatedHours: 1,
      },
      {
        id: '1-3',
        name: 'Functions Assignment',
        dueDate: '2025-03-01',
        description: 'Create reusable functions for common tasks',
        estimatedHours: 3,
      },
    ],
  },
  {
    id: '2',
    name: 'Data Structures and Algorithms',
    code: 'CS 201',
    instructor: 'Prof. Johnson',
    credits: 4,
    assignments: [
      {
        id: '2-1',
        name: 'Linked List Implementation',
        dueDate: '2025-02-18',
        description: 'Implement a doubly linked list in Python',
        estimatedHours: 5,
      },
      {
        id: '2-2',
        name: 'Binary Search Tree Project',
        dueDate: '2025-03-05',
        description: 'Build a BST with insert, delete, and search operations',
        estimatedHours: 8,
      },
      {
        id: '2-3',
        name: 'Sorting Algorithms Comparison',
        dueDate: '2025-03-15',
        description: 'Implement and analyze 3 different sorting algorithms',
        estimatedHours: 10,
      },
      {
        id: '2-4',
        name: 'Graph Algorithms Assignment',
        dueDate: '2025-04-01',
        description: 'Implement Dijkstra and A* algorithms',
        estimatedHours: 12,
      },
    ],
  },
  {
    id: '3',
    name: 'Web Development Fundamentals',
    code: 'CS 250',
    instructor: 'Dr. Williams',
    credits: 3,
    assignments: [
      {
        id: '3-1',
        name: 'HTML & CSS Portfolio',
        dueDate: '2025-02-20',
        description: 'Create a personal portfolio page',
        estimatedHours: 4,
      },
      {
        id: '3-2',
        name: 'JavaScript Quiz App',
        dueDate: '2025-03-10',
        description: 'Build an interactive quiz application',
        estimatedHours: 6,
      },
    ],
  },
  {
    id: '4',
    name: 'Machine Learning Basics',
    code: 'CS 350',
    instructor: 'Dr. Chen',
    credits: 4,
    assignments: [
      {
        id: '4-1',
        name: 'Linear Regression Implementation',
        dueDate: '2025-02-25',
        description: 'Implement linear regression from scratch',
        estimatedHours: 6,
      },
      {
        id: '4-2',
        name: 'Neural Network Assignment',
        dueDate: '2025-03-20',
        description: 'Build a simple neural network for classification',
        estimatedHours: 10,
      },
      {
        id: '4-3',
        name: 'Image Classification Project',
        dueDate: '2025-04-10',
        description: 'Train a CNN to classify handwritten digits',
        estimatedHours: 15,
      },
    ],
  },
  {
    id: '5',
    name: 'Software Engineering',
    code: 'CS 340',
    instructor: 'Prof. Davis',
    credits: 3,
    assignments: [
      {
        id: '5-1',
        name: 'Requirements Analysis Document',
        dueDate: '2025-02-28',
        description: 'Create detailed requirements for a software project',
        estimatedHours: 5,
      },
      {
        id: '5-2',
        name: 'UML Diagrams',
        dueDate: '2025-03-15',
        description: 'Design system architecture with UML diagrams',
        estimatedHours: 4,
      },
      {
        id: '5-3',
        name: 'Team Project Phase 1',
        dueDate: '2025-04-05',
        description: 'Implement first sprint of the project',
        estimatedHours: 15,
      },
    ],
  },
]
