let appRouter = null

export function registerAppRouter(router) {
  appRouter = router
}

export function getAppRouter() {
  return appRouter
}
