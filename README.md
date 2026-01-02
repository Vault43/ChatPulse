# ChatPulse - AI Auto-reply SaaS Platform

A comprehensive AI-powered auto-reply platform for businesses, built with FastAPI backend and React frontend.

## 🚀 Features

- **AI-Powered Responses**: Integration with OpenAI GPT and Google Gemini for intelligent auto-replies
- **Custom AI Rules**: Define custom trigger keywords and response templates
- **Multi-Platform Support**: Works across websites, WhatsApp, and other messaging platforms
- **User Management**: Secure authentication with JWT tokens
- **Subscription Plans**: Free, Basic, Pro, and Enterprise tiers with Flutterwave payments
- **Real-time Analytics**: Track chat performance and user engagement
- **Responsive Design**: Mobile-first design with Tailwind CSS

## 🏗️ Architecture

### Backend (FastAPI)
- **Authentication**: JWT-based secure login system
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Integration**: OpenAI and Google Gemini APIs
- **Payment Processing**: Flutterwave integration
- **API Documentation**: Auto-generated with FastAPI Swagger UI

### Frontend (React + Vite)
- **Modern Stack**: React 18, Vite, Tailwind CSS
- **State Management**: React Query for server state
- **Routing**: React Router v6
- **Forms**: React Hook Form
- **UI Components**: Headless UI + Heroicons

## 📋 Prerequisites

- Node.js 18+
- Python 3.9+
- PostgreSQL 12+
- Redis (optional, for caching)

## 🛠️ Installation

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/chatpulse.git
cd chatpulse
```

2. **Set up Python environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Set up database**
```bash
# Create PostgreSQL database
createdb chatpulse

# Run migrations (if using Alembic)
alembic upgrade head
```

5. **Start the backend server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Configure environment variables**
```bash
cp .env.example .env.local
# Edit .env.local with your API URL
```

3. **Start the development server**
```bash
npm run dev
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/chatpulse

# Security
SECRET_KEY=your-super-secret-key-here

# AI Services
OPENAI_API_KEY=sk-your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key

# Payment (Flutterwave)
FLUTTERWAVE_SECRET_KEY=FLWSECK-your-secret-key
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK-your-public-key

# Other services
REDIS_URL=redis://localhost:6379
```

#### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:8000
```

## 🚀 Deployment

### Backend Deployment Options

#### 1. Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### 2. Render
- Connect your GitHub repository to Render
- Set environment variables in Render dashboard
- Deploy automatically on push

#### 3. Vercel (for frontend only)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
cd frontend
vercel --prod
```

### Docker Deployment

1. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

2. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 💳 Subscription Plans

| Plan | Price | Features |
|------|-------|----------|
| Free | $0 | 100 messages/month, 5 AI rules |
| Basic | $29.99 | 1,000 messages/month, 25 AI rules |
| Pro | $99.99 | 10,000 messages/month, 100 AI rules |
| Enterprise | $299.99 | Unlimited messages & rules |

## 🔒 Security Features

- JWT authentication with secure token handling
- Password hashing with bcrypt
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CORS configuration
- Rate limiting support

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Monitoring & Analytics

- Built-in analytics dashboard
- Chat performance metrics
- User engagement tracking
- Subscription usage statistics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@chatpulse.com
- 💬 Discord: [Join our community](https://discord.gg/chatpulse)
- 📖 Documentation: [docs.chatpulse.com](https://docs.chatpulse.com)

## 🌟 Roadmap

- [ ] Multi-language support
- [ ] Advanced AI model selection
- [ ] WhatsApp Business API integration
- [ ] Mobile app (React Native)
- [ ] Advanced analytics with ML insights
- [ ] White-label solutions
- [ ] API rate limiting and quotas
- [ ] Webhook integrations

---

**Built with ❤️ by the ChatPulse Team**
