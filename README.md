# Tixly - AI Customer Support Copilot

AI-powered customer support ticket management system with automated classification, smart routing, and knowledge base integration.

**Video Demo**: https://drive.google.com/file/d/1fyeg-WjjwA7B6Ue7DKvUjaqdglc-gSj5/view?usp=sharing

## Features

- Automatic ticket categorization using Groq LLaMA 3.1
- AI-generated reply suggestions for support agents
- RAG knowledge base with semantic search
- LSTM neural network for ticket volume forecasting
- Real-time analytics dashboard

## Tech Stack

**Frontend**
- Next.js 14
- TypeScript
- Tailwind CSS

**Backend**
- FastAPI
- Python 3.11
- Groq API (LLaMA 3.1 70B)
- ChromaDB (Vector Database)
- TensorFlow (LSTM)

## Prerequisites

- Node.js 18+
- Python 3.11+
- Anaconda/Miniconda
- Groq API key (get it free at https://console.groq.com/keys)

## Installation

### Backend Setup

```bash
cd backend

# Create conda environment
conda create -n ticket_copliot python=3.11 -y
conda activate ticket_copliot

# Install dependencies
pip install -r requirements.txt

# Add your Groq API key to .env
echo "GROQ_API_KEY=your_key_here" > .env

# Initialize knowledge base
python data/sample_kb_articles.py

# Train forecasting model
python train_forecast_model.py

# Start backend server
cd ..
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at http://localhost:3000

## Usage

1. Open http://localhost:3000/submit-ticket to create tickets
2. Navigate to http://localhost:3000/agent to view and manage tickets
3. Go to http://localhost:3000/manager for analytics and forecasting

## API Documentation

Interactive API documentation available at http://localhost:8000/docs

## Author

**Parth CJ**
- GitHub: [@parthCJ](https://github.com/parthCJ)
- Repository: [Tixly-Customer_support_agent](https://github.com/parthCJ/Tixly-Customer_support_agent)

## License

MIT License - see LICENSE file for details


