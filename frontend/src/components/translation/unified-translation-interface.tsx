'use client'

import React, { useState } from 'react'
import { Button } from "../ui/button"
import { Label } from "../ui/label"
import { RadioGroup, RadioGroupItem } from "../ui/radio-group"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs"
import { Textarea } from "../ui/textarea"

type LanguageOption = 'english' | 'arabic' | 'darija'
type ModelOption = '' | 'Helsinki-NLP/opus-mt-en-ar' | 'ychafiqui/darija-to-english-2'

export default function UnifiedTranslationInterface() {
    const [sourceLanguage, setSourceLanguage] = useState<LanguageOption>('english')
    const [inputText, setInputText] = useState('')
    const [translation, setTranslation] = useState('')
    const [error, setError] = useState('')
    const [isLoading, setIsLoading] = useState(false)

    const handleTranslate = async (isEnhanced: boolean) => {
        if (!inputText.trim()) {
            setError('Please enter text to translate')
            return
        }

        setIsLoading(true)
        setError('')

        try {
            const endpoint = isEnhanced ? '/api/v2/translate' : '/api/translate'
            const model = getTranslationModel(sourceLanguage, isEnhanced)

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: inputText,
                    source_lang: getSourceLangCode(sourceLanguage),
                    target_lang: getTargetLangCode(sourceLanguage),
                    model,
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

    const getTranslationModel = (lang: LanguageOption, isEnhanced: boolean): ModelOption => {
        if (isEnhanced && lang === 'darija') {
            return 'ychafiqui/darija-to-english-2'
        }
        return lang === 'english' ? 'Helsinki-NLP/opus-mt-en-ar' : ''
    }

    const getSourceLangCode = (lang: LanguageOption): string => {
        switch (lang) {
            case 'arabic': return 'ar'
            case 'english': return 'en'
            case 'darija': return 'darija'
        }
    }

    const getTargetLangCode = (lang: LanguageOption): string => {
        return lang === 'english' ? 'ar' : 'en'
    }

    const TranslationForm = ({ isEnhanced = false }) => (
        <div className="space-y-6">
            <div className="bg-white rounded-lg p-6 shadow-md">
                <h3 className="text-lg font-semibold mb-4 text-gray-800">
                    {isEnhanced ? 'Enhanced Translation' : 'Standard Translation'}
                </h3>

                <div className="space-y-4">
                    <div>
                        <Label className="text-gray-700">Source Language</Label>
                        <RadioGroup
                            value={sourceLanguage}
                            onValueChange={(value) => {
                                setSourceLanguage(value as LanguageOption)
                                setTranslation('')
                                setError('')
                            }}
                            className="flex flex-wrap gap-4 mt-2"
                        >
                            <div className="flex items-center space-x-2">
                                <RadioGroupItem value="english" id={`english-${isEnhanced}`} />
                                <Label htmlFor={`english-${isEnhanced}`} className="text-gray-600">English</Label>
                            </div>
                            <div className="flex items-center space-x-2">
                                <RadioGroupItem value="arabic" id={`arabic-${isEnhanced}`} />
                                <Label htmlFor={`arabic-${isEnhanced}`} className="text-gray-600">Arabic</Label>
                            </div>
                            {isEnhanced && (
                                <div className="flex items-center space-x-2">
                                    <RadioGroupItem value="darija" id="darija" />
                                    <Label htmlFor="darija" className="text-gray-600">Darija</Label>
                                </div>
                            )}
                        </RadioGroup>
                    </div>

                    <div>
                        <Label className="text-gray-700">Enter {sourceLanguage} text</Label>
                        <Textarea
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            placeholder={`Type your ${sourceLanguage} text here...`}
                            className={`mt-2 min-h-[200px] resize-none text-gray-800 ${sourceLanguage !== 'english' ? 'text-right' : ''
                                }`}
                            dir={sourceLanguage !== 'english' ? 'rtl' : 'ltr'}
                        />
                    </div>

                    {error && (
                        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                            <p className="text-red-800">{error}</p>
                        </div>
                    )}

                    {translation && (
                        <div>
                            <Label className="text-gray-700">
                                {sourceLanguage === 'english' ? 'Arabic' : 'English'} Translation
                            </Label>
                            <div
                                className={`mt-2 p-4 bg-gray-50 border border-gray-200 rounded-md text-gray-800 ${sourceLanguage === 'english' ? 'text-right' : ''
                                    }`}
                                dir={sourceLanguage === 'english' ? 'rtl' : 'ltr'}
                            >
                                {translation}
                            </div>
                        </div>
                    )}

                    <div className="flex justify-between pt-4">
                        <Button
                            variant="outline"
                            onClick={() => {
                                setInputText('')
                                setTranslation('')
                                setError('')
                            }}
                            className="text-gray-600 hover:text-gray-800"
                        >
                            Clear
                        </Button>
                        <Button
                            onClick={() => handleTranslate(isEnhanced)}
                            disabled={isLoading || !inputText.trim()}
                            className="bg-blue-600 text-white hover:bg-blue-700"
                        >
                            {isLoading ? 'Translating...' : 'Translate'}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    )

    return (
        <div className="w-full max-w-4xl mx-auto p-6 space-y-6 bg-gray-100">
            <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">Translation Service</h1>

            <Tabs defaultValue="standard" className="w-full">
                <TabsList className="w-full justify-center bg-white">
                    <TabsTrigger value="standard" className="text-gray-600 data-[state=active]:text-gray-900">Standard Translation</TabsTrigger>
                    <TabsTrigger value="enhanced" className="text-gray-600 data-[state=active]:text-gray-900">Enhanced Translation</TabsTrigger>
                </TabsList>

                <TabsContent value="standard" className="mt-6">
                    <TranslationForm isEnhanced={false} />
                </TabsContent>

                <TabsContent value="enhanced" className="mt-6">
                    <TranslationForm isEnhanced={true} />
                </TabsContent>
            </Tabs>
        </div>
    )
}
