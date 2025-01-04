// File: frontend/src/components/ui/alert.tsx
"use client"

import { cn } from "@/lib/utils"
import * as React from "react"

const Alert = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        role="alert"
        className={cn(
            "bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative",
            className
        )}
        {...props}
    />
))

Alert.displayName = "Alert"

const AlertDescription = React.forwardRef<
    HTMLParagraphElement,
    React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
    <p
        ref={ref}
        className={cn("text-sm", className)}
        {...props}
    />
))

AlertDescription.displayName = "AlertDescription"

export { Alert, AlertDescription }
