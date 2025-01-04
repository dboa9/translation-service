import { NextRequest, NextResponse } from 'next/server'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export async function POST(request: NextRequest) {
    try {
        const body = await request.json()
        
        const response = await fetch(`${API_URL}/api/v2/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        })

        if (!response.ok) {
            const error = await response.json()
            return NextResponse.json(
                { error: error.detail || 'Translation failed' },
                { status: response.status }
            )
        }

        const data = await response.json()
        return NextResponse.json(data)
    } catch (error) {
        console.error('Translation API error:', error)
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        )
    }
}

export async function GET() {
    try {
        const response = await fetch(`${API_URL}/api/v2/models`)
        const data = await response.json()
        return NextResponse.json(data)
    } catch (error) {
        console.error('Models API error:', error)
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        )
    }
}
