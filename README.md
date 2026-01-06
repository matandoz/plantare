# 🌱 PlantCare - AI Watering Assistant

A gamified plant care app powered by Google Gemini AI that generates personalized watering schedules for your plants.

## Features

- 🤖 AI-generated watering tasks based on your plants and conditions
- 🎮 Gamification system with XP, levels, and badges
- 🏆 Leaderboard and achievements
- 🛒 Virtual shop for customization
- 🌓 Dark mode support

## Setup

### Local Development

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```

### Deployment on Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add your `GEMINI_API_KEY` in the Secrets section

## Get a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Copy and use in the app

## License

MIT
