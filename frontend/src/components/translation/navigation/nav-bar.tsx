'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'

export default function NavBar() {
    const [mounted, setMounted] = useState(false)
    
    useEffect(() => {
        setMounted(true)
    }, [])

    // Don't render anything until mounted to prevent hydration mismatch
    if (!mounted) {
        return (
            <nav className="bg-slate-800">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="flex justify-between h-16">
                        <div className="flex-shrink-0 flex items-center">
                            <span className="text-xl font-bold text-white">Translation Service</span>
                        </div>
                    </div>
                </div>
            </nav>
        )
    }

    const isActive = (path: string) => {
        if (typeof window !== 'undefined') {
            return window.location.pathname === path
        }
        return false
    }

    return (
        <nav className="bg-slate-800">
            <div className="max-w-7xl mx-auto px-4">
                <div className="flex justify-between h-16">
                    <div className="flex">
                        <div className="flex-shrink-0 flex items-center">
                            <span className="text-xl font-bold text-white">Translation Service</span>
                        </div>
                        <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                            <Link
                                href="/"
                                className={
                                    isActive('/') 
                                        ? 'inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-slate-900 rounded-md'
                                        : 'inline-flex items-center px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-700 rounded-md'
                                }
                            >
                                Standard Translation
                            </Link>
                            <Link
                                href="/enhanced-translation"
                                className={
                                    isActive('/enhanced-translation')
                                        ? 'inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-slate-900 rounded-md'
                                        : 'inline-flex items-center px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-700 rounded-md'
                                }
                            >
                                Enhanced Translation
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    )
}
