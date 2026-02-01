import * as React from "react"

const Progress = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { value?: number }
>(({ className, value, ...props }, ref) => (
  <div
    ref={ref}
    className={`relative h-4 w-full overflow-hidden rounded-full bg-slate-200 ${className || ''}`}
    {...props}
  >
    <div
      className="h-full bg-indigo-600 transition-all duration-300"
      style={{ width: `${value || 0}%` }}
    />
  </div>
))
Progress.displayName = "Progress"

export { Progress }
