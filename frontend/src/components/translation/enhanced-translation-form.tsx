'use client'

import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Textarea } from "@/components/ui/textarea"
import { useState } from 'react'

type LanguageOption = 'english' | 'arabic' | 'darija';
type ModelOption = 'Helsinki-NLP/opus-mt-ar-en' | 'Helsinki-NLP/opus-mt-en-ar' | 'ychafiqui/darija-to-english-2';

export default function EnhancedTranslationForm() {
    const [sourceLang, setSourceLang] = useState<LanguageOption>('arabic')
    const [inputText, setInputText] = useState('')
    const [translation, setTranslation] = useState('')
    const [error, setError] = useState('')
    const [isLoading, setIsLoading] = useState(false)

    // Helper function to determine the appropriate model and target language
    const getTranslationConfig = (source: LanguageOption): { model: ModelOption, targetLang: string } => {
        switch (source) {
            case 'arabic':
                return { model: 'Helsinki-NLP/opus-mt-ar-en', targetLang: 'en' }
            case 'english':
                return { model: 'Helsinki-NLP/opus-mt-en-ar', targetLang: 'ar' }
            case 'darija':
                return { model: 'ychafiqui/darija-to-english-2', targetLang: 'en' }
            default:
                return { model: 'Helsinki-NLP/opus-mt-ar-en', targetLang: 'en' }
        }
    }

    // Helper function to get source language code
    const getSourceLangCode = (lang: LanguageOption): string => {
        switch (lang) {
            case 'arabic':
                return 'ar'
            case 'english':
                return 'en'
            case 'darija':
                return 'darija'
            default:
                return 'ar'
        }
    }

    const handleTranslate = async () => {
        if (!inputText.trim()) {
            setError('Please enter text to translate')
            return
        }

        setIsLoading(true)
        setError('')

        try {
            const config = getTranslationConfig(sourceLang)
            const response = await fetch('/api/v2/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: inputText,
                    source_lang: getSourceLangCode(sourceLang),
                    target_lang: config.targetLang,
                    model: config.model,
                }),
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Translation failed')
            }

            const data = await response.json()
            setTranslation(data.translation)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Translation failed. Please try again.')
            console.error('Translation error:', err)
        } finally {
            setIsLoading(false)
        }
    }

    const getTargetLanguage = (source: LanguageOption): string => {
        return source === 'english' ? 'Arabic' : 'English'
    }

    return (
        <Card className="w-full max-w-2xl mx-auto">
            <CardHeader>
                <CardTitle>Enhanced Translation</CardTitle>
            </CardHeader>

            <CardContent className="space-y-6">
                <div className="space-y-3">
                    <Label>Source Language</Label>
                    <RadioGroup
                        value={sourceLang}
                        onValueChange={(value) => {
                            setSourceLang(value as LanguageOption)
                            setTranslation('')
                            setError('')
                        }}
                        className="flex flex-wrap gap-4"
                    >
                        <div className="flex items-center space-x-2">
                            <RadioGroupItem value="english" id="english" />
                            <Label htmlFor="english">English</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                            <RadioGroupItem value="arabic" id="arabic" />
                            <Label htmlFor="arabic">Arabic (MSA)</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                            <RadioGroupItem value="darija" id="darija" />
                            <Label htmlFor="darija">Darija</Label>
                        </div>
                    </RadioGroup>
                </div>

                <div className="space-y-2">
                    <Label>{`Enter ${sourceLang} text`}</Label>
                    <Textarea
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        placeholder={`Type your ${sourceLang} text here...`}
                        className={`min-h-[100px] ${sourceLang !== 'english' ? 'text-right' : ''}`}
                        dir={sourceLang !== 'english' ? 'rtl' : 'ltr'}
                    />
                </div>

                {error && (
                    <Alert>
                        <AlertDescription className="text-red-600">{error}</AlertDescription>
                    </Alert>
                )}

                {translation && (
                    <div className="space-y-2">
                        <Label>{getTargetLanguage(sourceLang)} Translation</Label>
                        <div className={`p-4 rounded-md bg-muted ${getTargetLanguage(sourceLang).toLowerCase() === 'arabic' ? 'text-right' : ''}`}
                            dir={getTargetLanguage(sourceLang).toLowerCase() === 'arabic' ? 'rtl' : 'ltr'}
                        >
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
