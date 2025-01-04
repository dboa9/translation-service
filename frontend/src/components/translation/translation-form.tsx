'use client'

import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Textarea } from "@/components/ui/textarea"
import { useState } from 'react'

export default function TranslationForm() {
    const [sourceLang, setSourceLang] = useState<'english' | 'arabic'>('arabic')
    const [inputText, setInputText] = useState('')
    const [translation, setTranslation] = useState('')
    const [error, setError] = useState('')
    const [isLoading, setIsLoading] = useState(false)

    const handleTranslate = async () => {
        if (!inputText.trim()) {
            setError('Please enter text to translate')
            return
        }

        setIsLoading(true)
        setError('')

        try {
            const response = await fetch('/api/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: inputText,
                    source_lang: sourceLang === 'arabic' ? 'ar' : 'en',
                    target_lang: sourceLang === 'arabic' ? 'en' : 'ar',
                    model: sourceLang === 'arabic' ? 'Helsinki-NLP/opus-mt-ar-en' : 'Helsinki-NLP/opus-mt-en-ar',
                }),
            })

            if (!response.ok) {
                throw new Error('Translation failed')
            }

            const data = await response.json()
            setTranslation(data.translation)
        } catch (err) {
            setError('Translation failed. Please try again.')
            console.error('Translation error:', err)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <Card className="w-full max-w-2xl mx-auto">
            <CardHeader>
                <CardTitle>Arabic-English Translation</CardTitle>
            </CardHeader>

            <CardContent className="space-y-6">
                <div className="space-y-3">
                    <Label>Source Language</Label>
                    <RadioGroup
                        value={sourceLang}
                        onValueChange={(value) => setSourceLang(value as 'english' | 'arabic')}
                        className="flex space-x-4"
                    >
                        <div className="flex items-center space-x-2">
                            <RadioGroupItem value="english" id="english" />
                            <Label htmlFor="english">English</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                            <RadioGroupItem value="arabic" id="arabic" />
                            <Label htmlFor="arabic">Arabic</Label>
                        </div>
                    </RadioGroup>
                </div>

                <div className="space-y-2">
                    <Label>{`Enter ${sourceLang} text`}</Label>
                    <Textarea
                        value={inputText}
                        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInputText(e.target.value)}
                        placeholder={`Type your ${sourceLang} text here...`}
                        className="min-h-[100px]"
                    />
                </div>

                {error && (
                    <Alert>
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}

                {translation && (
                    <div className="space-y-2">
                        <Label>{sourceLang === 'arabic' ? 'English' : 'Arabic'} Translation</Label>
                        <div className="p-4 rounded-md bg-muted">
                            {translation}
                        </div>
                    </div>
                )}
            </CardContent>

            <CardFooter className="flex justify-between">
                <Button
                    variant="outline"
                    onClick={() => {
                        setInputText('')
                        setTranslation('')
                        setError('')
                    }}
                >
                    Clear
                </Button>
                <Button
                    onClick={handleTranslate}
                    disabled={isLoading || !inputText.trim()}
                >
                    {isLoading ? 'Translating...' : 'Translate'}
                </Button>
            </CardFooter>
        </Card>
    )
}
