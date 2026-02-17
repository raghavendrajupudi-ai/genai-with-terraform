# 🤖 Generative AI Chatbot with Google Gemini

A modern, interactive chatbot application built with **LangChain** ## How It Works

1. **Conversation Memory**: The app uses `ConversationBufferMemory` to maintain context across multiple turns
2. **LLM Chain**: `ConversationChain` from LangChain orchestrates the conversation with the Gemini model
3. **Session State**: Streamlit's session state manages messages and memory across reruns
4. **Modular Architecture**: Frontend and backend are separated for better code organization and testability

## Architecture Overview

The application follows a modular, three-layer architecture:

### Frontend Layer (`frontend.py`)
- Handles all Streamlit UI components
- Manages user input and display
- Pure presentation logic with no business logic

### Backend Layer (`backend.py`)
- Manages LangChain integration
- Handles Gemini API communication
- Maintains conversation state and memory
- Completely independent of Streamlit

### Configuration & Utilities
- **config.py**: Centralized constants for easy customization
- **utils.py**: Validation, formatting, and session management utilities
- **app.py**: Orchestrates frontend and backend interactions
treamlit**, powered by Google's Gemini AI models.

## Features

✨ **Key Features:**
- 💬 Real-time conversational AI powered by OpenAI's GPT models
- 🧠 Conversation memory - maintains context throughout the session
- ⚙️ Customizable AI parameters:
  - Model selection (GPT-3.5, GPT-4, GPT-4 Turbo)
  - Temperature control for creativity vs. consistency
  - Max tokens configuration for response length
- 🎨 Modern, responsive UI with chat-style interface
- 🗑️ Clear conversation history with one click
- 🔐 Secure API key input via sidebar
- 📝 Clean message display with user/assistant differentiation

## Prerequisites

Before you start, make sure you have:
- Python 3.8 or higher installed
- A Google API key for Gemini (get it at https://ai.google.dev/tutorials/setup)

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd /path/to/streamlit-langchain
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Set up environment variables:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your Google API key:
     ```
     GOOGLE_API_KEY=your_actual_api_key_here
     ```

## Running the Application

1. **Start the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **Access the application:**
   - Open your browser and go to `http://localhost:8501`
   - The app will automatically open in your default browser

3. **Configure and use:**
   - In the sidebar, enter your OpenAI API key
   - Adjust model settings if desired
   - Start chatting!

## Configuration Options

### Sidebar Settings

- **Google API Key**: Your API key for authentication with Gemini
- **Select Model**: Choose between:
  - gemini-pro (fast and efficient)
  - gemini-1.5-pro (most capable)
  - gemini-1.5-flash (fastest)
- **Temperature**: (0.0 - 2.0)
  - Lower values (0.0-0.7): More focused and deterministic
  - Higher values (0.7-2.0): More creative and random
- **Max Tokens**: (50 - 2000)
  - Controls maximum response length
- **Clear Conversation**: Resets chat history and memory

## Dependencies

- **streamlit**: Web app framework
- **langchain**: LLM orchestration framework
- **langchain-google-genai**: Google Gemini integration for LangChain
- **google-generativeai**: Google's Generative AI Python client
- **python-dotenv**: Environment variable management

## Project Structure

```
streamlit-langchain/
├── app.py              # Main application entry point
├── frontend.py         # Streamlit UI components and rendering
├── backend.py          # LangChain integration and AI logic
├── config.py           # Configuration constants and settings
├── utils.py            # Utility functions and helpers
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment configuration
└── README.md           # This file
```

### File Descriptions

- **app.py**: Main application file that orchestrates frontend and backend
- **frontend.py**: Contains the `ChatbotUI` class with all Streamlit UI components
- **backend.py**: Contains the `AIBackend` class handling LangChain and Gemini integration
- **config.py**: Centralized configuration constants for easy customization
- **utils.py**: Helper classes for input validation, message formatting, and session management

## How It Works

1. **Conversation Memory**: The app uses `ConversationBufferMemory` to maintain context across multiple turns
2. **LLM Chain**: `ConversationChain` from LangChain orchestrates the conversation with the OpenAI model
3. **Streaming Output**: The app is configured for streaming responses (prepared for future enhancement)
4. **Session State**: Streamlit's session state manages messages and memory across reruns

## Usage Examples

- 💡 "Explain quantum computing in simple terms"
- 📚 "What are the best practices for writing clean code?"
- 🎨 "Help me brainstorm ideas for a creative project"
- 🧮 "Solve this math problem: 2x + 5 = 15"
- 📝 "Write a professional email to..."

## Troubleshooting

### "Invalid API Key" Error
- Verify your Google API key is correct and valid
- Check if you have enabled Gemini API in Google Cloud Console
- Ensure the key has the necessary permissions

### "ModuleNotFoundError"
- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- Verify you're using the correct Python virtual environment

### Slow Responses
- Some models (like Gemini 1.5 Pro) may be slower. Try Gemini Flash for faster responses
- Reduce the Max Tokens value
- Check your internet connection

### Session/Memory Issues
- Click "Clear Conversation" to reset the chat
- Refresh the page if messages aren't displaying correctly

## API Costs

Google Gemini offers a free tier with generous limits:
- Gemini 1.5 Pro: Free tier available with rate limits
- Gemini 1.5 Flash: Fastest and most cost-effective
- Check pricing at https://ai.google.dev/pricing

## Future Enhancements

Potential improvements for future versions:
- 🔄 Support for multiple conversation threads
- 📊 Conversation history export (PDF, TXT)
- 🎯 Custom prompts and system instructions
- 🌐 Support for additional LLM providers (Anthropic, Cohere, etc.)
- 🗂️ Persistent storage of conversation history
- 🎤 Voice input/output support
- 🖼️ Image generation capabilities

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Review Google Gemini documentation: https://ai.google.dev/docs
3. Check LangChain documentation: https://python.langchain.com

## Credits

- Built with [Streamlit](https://streamlit.io/)
- Powered by [LangChain](https://python.langchain.com/)
- AI models by [Google Gemini](https://ai.google.dev/)

---

**Happy Chatting! 🚀**
