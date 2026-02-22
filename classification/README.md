# Image Classification System

## How to Use

1. **Place Images**: Copy your images into this `classification` folder
   - Supported formats: JPG, JPEG, PNG, BMP, GIF, TIFF, WEBP

2. **Run Classification**: Execute the classification script
   ```bash
   python classify_images.py
   ```

3. **View Results**: Check the generated text file with timestamp
   - Format: `classification_results_YYYYMMDD_HHMMSS.txt`

## Classification Categories

The system classifies images based on material composition:

- **can** - Metal, aluminum beverage containers
- **plastic** - PET bottles, containers, wrappers  
- **paper** - Cardboard, newspapers, paper materials
- **glass** - Glass bottles or jars

## Features

- ✅ Material-based classification (ignores brands/labels)
- ✅ AI-powered visual analysis using Gemini
- ✅ Single-word output format
- ✅ Detailed results with processing times
- ✅ Error handling and fallbacks
- ✅ Timestamped output files

## Requirements

- Python 3.7+
- Google Gemini API key in `.env` file
- Required packages: `google-generativeai`, `python-dotenv`

## Output

Each run generates a detailed text file containing:
- Individual image classifications
- Processing statistics
- Material breakdown summary
- Technical details and timestamps