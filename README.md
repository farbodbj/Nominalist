# Username Recommendation System

A multi-agent AI-powered system that generates intelligent username recommendations based on input names. The system combines traditional rule-based generation with AI creativity to produce unique, available usernames.

## 🚀 Features

- **Multi-Agent Architecture**: Uses specialized agents for creation and review processes
- **AI-Powered Generation**: Leverages GPT models for creative username suggestions
- **Multi-Language Support**: Converts names from various languages (e.g., Persian) to English equivalents
- **Availability Checking**: Verifies username availability against a MariaDB database
- **Smart Ranking**: Combines AI evaluation with traditional scoring metrics
- **RESTful API**: Easy-to-use HTTP endpoints for integration

## 🏗️ Architecture

The system is built using a **multi-agent workflow** pattern with LangGraph:

### Core Components

1. **Creator Agent**: Generates 10-12 username candidates using:
   - AI-powered creative generation (GPT-4)
   - Traditional rule-based methods (underscores, numbers, prefixes, etc.)

2. **Reviewer Agent**: Evaluates and ranks usernames based on:
   - AI scoring for memorability, professionalism, and creativity
   - Traditional metrics (length, character composition, readability)
   - Database availability checks

3. **Name Service**: Handles name translation and normalization:
   - Fuzzy matching using Levenshtein, Damerau-Levenshtein, and Jaro-Winkler algorithms
   - Persian-to-English name conversion using a comprehensive dataset

4. **Database Service**: Manages username storage and availability:
   - MariaDB/MySQL integration
   - Efficient batch checking for multiple usernames

### Workflow

```
Input Name → Name Service (Translation) → Creator Agent (Generation) → Reviewer Agent (Ranking) → Top 3 Recommendations
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11
- **AI/ML**: OpenAI GPT, LangGraph workflow orchestration
- **Database**: MariaDB/MySQL
- **Similarity Matching**: RapidFuzz, Pandas
- **Containerization**: Docker, Docker Compose

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (or compatible endpoint)

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd username-recommendation-system
```

2. Create a `.env` file in the root directory:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Database Configuration
DB_HOST=db
DB_USER=username_user
DB_PASSWORD=secure_password_123
DB_NAME=usernames_db
DB_ROOT_PASSWORD=root_password_123
DB_PORT=3307
```

### Launch the System

1. Build and start all services:
```bash
docker-compose up --build
```

2. The API will be available at `http://localhost:8000`

3. Check system health:
```bash
curl http://localhost:8000/health
```

### Usage Example

Generate username recommendations:

```bash
curl -X POST "http://localhost:8000/generate-usernames" \
     -H "Content-Type: application/json" \
     -d '{"name": "محمد علی"}'
```

Response:
```json
{
  "input_name": "محمد علی",
  "recommended_usernames": [
    "mohammad_ali",
    "mali_pro",
    "mohammad_dev"
  ],
  "count": 3
}
```

### API Endpoints

- `GET /` - System information
- `GET /health` - Health check
- `POST /generate-usernames` - Generate username recommendations

#### Request Format:
```json
{
  "name": "John Doe"
}
```

#### Response Format:
```json
{
  "input_name": "John Doe",
  "recommended_usernames": ["john_doe", "johndoe_pro", "jdoe_dev"],
  "count": 3
}
```

### Citation
```
@misc{bijary2025agenticusernamesuggestionmultimodal,
      title={Agentic Username Suggestion and Multimodal Gender Detection in Online Platforms: Introducing the PNGT-26K Dataset}, 
      author={Farbod Bijary and Mohsen Ebadpour and Amirhosein Tajbakhsh},
      year={2025},
      eprint={2509.11136},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2509.11136}, 
}
```