import { createRouter, createRootRoute, createRoute } from '@tanstack/react-router'
import { App } from './App'
import { CourseList } from './components/CourseList'
import { Evaluation } from './components/Evaluation'
import { QuizCreator } from './components/QuizCreator'
import { QuizTaker } from './components/QuizTaker'

const rootRoute = createRootRoute({
  component: App,
})

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: CourseList,
})

const coursesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/courses',
  component: CourseList,
})

const evaluationRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/evaluation',
  component: Evaluation,
})

const quizCreatorRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/quiz/create',
  component: QuizCreator,
})

const quizTakerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/quiz/take',
  component: QuizTaker,
})

const routeTree = rootRoute.addChildren([indexRoute, coursesRoute, evaluationRoute, quizCreatorRoute, quizTakerRoute])

export const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
