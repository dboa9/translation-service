// File: frontend/src/components/translation/ui/language-selector.tsx
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"

interface LanguageSelectorProps {
    value: 'english' | 'darija'
    onChange: (value: 'english' | 'darija') => void
}

export function LanguageSelector({
    value,
    onChange
}: LanguageSelectorProps) {
    return (
        <div className="space-y-3">
            <Label>Source Language</Label>
            <RadioGroup
                value={value}
                onValueChange={onChange}
                className="flex space-x-4"
            >
                <div className="flex items-center space-x-2">
                    <RadioGroupItem value="english" id="english" />
                    <Label htmlFor="english">English</Label>
                </div>
                <div className="flex items-center space-x-2">
                    <RadioGroupItem value="darija" id="darija" />
                    <Label htmlFor="darija">Darija</Label>
                </div>
            </RadioGroup>
        </div>
    )
}