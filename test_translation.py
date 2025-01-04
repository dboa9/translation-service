from core.translation.translation_service import TranslationService

def test_translation():
    service = TranslationService()
    
    # Test English to Darija
    en_text = "Hello, how are you?"
    print("\nTesting English to Darija translation:")
    print(f"Input: {en_text}")
    result = service.translate(
        text=en_text,
        source_lang="English",
        target_lang="Darija",
        model="BAKKALIAYOUB/DarijaTranslation-V1"  # This model works well
    )
    print(f"Translation: {result}")
    
    # Test Darija to English
    dar_text = "labas, kif nta?"
    print("\nTesting Darija to English translation:")
    print(f"Input: {dar_text}")
    result = service.translate(
        text=dar_text,
        source_lang="Darija",
        target_lang="English",
        model="lachkarsalim/LatinDarija_English-v2"  # Using a different model that exists
    )
    print(f"Translation: {result}")

    # Check tokenizer configuration
    print("\nChecking tokenizer configuration:")
    service.check_tokenizer_config("BAKKALIAYOUB/DarijaTranslation-V1")
    service.check_tokenizer_config("lachkarsalim/LatinDarija_English-v2")

if __name__ == "__main__":
    test_translation()
