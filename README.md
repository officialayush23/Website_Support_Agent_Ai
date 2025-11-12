# Website Support Agent AI (Daksha.ai)




make an environment first 
then go to Backend and install django , supabase python client, drf , corsheader, pyjwt etc etc 
then python manage.py runserver


go to Chatbot_Ui 


npm rundev



An AI-powered customer support chatbot built with Django backend and React frontend, integrated with Supabase for authentication and database, and Google Gemini AI for intelligent conversation handling.

## 🎯 Project Overview

Daksha.ai is a full-stack customer support chatbot application that enables users to:
- **Chat with an AI assistant** powered by Google Gemini AI
- **Manage their profile** and account information
- **View products** and add items to cart
- **Check orders** and order history
- **File complaints** and track complaint status
- **Schedule returns** for products
- **Create orders** from cart items

The chatbot intelligently detects user intent, retrieves relevant context from the database, and performs actions based on natural language requests.

## 🛠️ Tech Stack

### Backend
- **Django 5.2.7** - Python web framework
- **Django REST Framework** - RESTful API endpoints
- **Supabase** - Backend-as-a-Service for authentication and database
- **Google Gemini AI** - AI model for chatbot responses
- **SQLite** - Local database (for Django models, Supabase is primary DB)

### Frontend
- **React 19** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling framework
- **React Router** - Client-side routing
- **Supabase JS Client** - Authentication and database client
- **Lucide React** - Icons
- **Sonner** - Toast notifications

## 📁 Project Structure

```
Website_Support_Agent_Ai/
├── Backend/                    # Django backend application
│   ├── api/                    # Main API app
│   │   ├── views.py           # API endpoints (chatbot, auth, profile)
│   │   ├── chatbot_logic.py   # Intent detection and context retrieval
│   │   ├── urls.py            # API URL routing
│   │   └── supabase_client.py # Supabase client configuration
│   ├── chatbot/               # Chatbot app (Django app)
│   ├── core/                  # Django project settings
│   │   ├── settings.py        # Django configuration
│   │   └── urls.py            # Main URL configuration
│   ├── manage.py              # Django management script
│   └── requirements.txt       # Python dependencies
│
├── Chatbot_Ui/                # React frontend application
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/          # Authentication components (login, signup, etc.)
│   │   │   ├── pages/         # Main pages (Chatbot, Profile)
│   │   │   └── ui/            # Reusable UI components
│   │   ├── supabaseclient.js  # Supabase client initialization
│   │   └── App.jsx            # Main React app component
│   ├── package.json           # Node.js dependencies
│   └── vite.config.js         # Vite configuration
│
└── Resources/
    └── dbms mockdata/         # CSV files with sample database schema
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** (for Django backend)
- **Node.js 16+** and **npm** (for React frontend)
- **Supabase Account** - Sign up at [supabase.com](https://supabase.com)
- **Google Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Website_Support_Agent_Ai
```

### Step 2: Backend Setup

#### 2.1 Navigate to Backend Directory

```bash
cd Backend
```

#### 2.2 Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2.3 Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2.4 Create `.env` File

Create a `.env` file in the `Backend/` directory with the following variables:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key
```

**How to get Supabase credentials:**
1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **API**
3. Copy the **Project URL** (`SUPABASE_URL`)
4. Copy the **anon/public key** (`SUPABASE_ANON_KEY`)
5. Copy the **service_role key** (`SUPABASE_SERVICE_KEY`) - Keep this secret!
6. Navigate to **Settings** → **Auth** → **JWT Settings** to get `SUPABASE_JWT_SECRET`

#### 2.5 Set Up Database Schema in Supabase

You need to create the following tables in your Supabase database. You can use the CSV files in `Resources/dbms mockdata/` as reference for the schema:

**Required Tables:**
- `users` - User profiles (columns: user_id, name, email, password_hash, phone, address, city, state, pincode)
- `products` - Product catalog (columns: product_id, name, price, description, stock, image_url)
- `orders` - Order records (columns: order_id, user_id, status, total_amount, shipping_address, payment_method, order_date)
- `order_items` - Order line items (columns: order_item_id, order_id, product_id, quantity, price_at_order)
- `cart_items` - Shopping cart (columns: cart_item_id, user_id, product_id, quantity)
- `complaints_updated` - Customer complaints (columns: complaint_id, user_id, order_id, description, status, created_at)
- `returns` - Return requests (columns: return_id, user_id, order_id, product_id, reason, status, requested_date)
- `meeting` - Scheduled meetings (columns: meeting_id, user_id, support_person, scheduled_time, status)
- `chat_logs_updated` - Chat history (columns: log_id, user_id, user_message, bot_response, intent_detected, timestamp)

**Quick Setup using Supabase SQL Editor:**

1. Go to your Supabase project → **SQL Editor**
2. Create tables (example for `users` table):

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

Repeat for all tables with appropriate columns based on your CSV files.

#### 2.6 Run Database Migrations

```bash
python manage.py migrate
```

#### 2.7 Start Django Development Server

```bash
python manage.py runserver
```

The backend will be available at `http://127.0.0.1:8000`

### Step 3: Frontend Setup

#### 3.1 Navigate to Frontend Directory

Open a new terminal window and navigate to:

```bash
cd Chatbot_Ui
```

#### 3.2 Install Dependencies

```bash
npm install
```

#### 3.3 Create `.env` File

Create a `.env` file in the `Chatbot_Ui/` directory:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=http://127.0.0.1:8000/api
```

**Note:** Use the same Supabase credentials from the backend `.env` file.

#### 3.4 Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` (default Vite port)

### Step 4: Access the Application

1. Open your browser and navigate to `http://localhost:5173`
2. You'll be redirected to the login page
3. **Create a new account** using the Signup page
4. After login, you'll be redirected to the chatbot interface

## 🎮 How to Use

### Authentication Flow

1. **Sign Up**: Create a new account via `/signup`
2. **Login**: Authenticate via Supabase Auth at `/login`
3. **Chatbot**: Access the main chatbot interface at `/chatbot`
4. **Profile**: View/edit profile at `/profile`

### Chatbot Features

The chatbot supports natural language queries. Here are some example interactions:

**Profile Management:**
- "Show my profile"
- "Update my address to 123 Main St, New York"
- "Change my phone number to 555-1234"

**Products & Cart:**
- "Show me products"
- "Add product 1 to my cart"
- "What's in my cart?"
- "I want to checkout" or "Order my cart"

**Orders:**
- "Show my orders"
- "What's the status of order 123?"

**Complaints:**
- "I want to file a complaint"
- "My order 123 was damaged"

**Returns:**
- "I want to return order 123"
- "Schedule a return for product 5"

**General:**
- "What can I do?"
- "Help me"

## 🔧 API Endpoints

### Authentication Endpoints

- `POST /api/register/` - Register a new user
- `POST /api/login/` - Login user (returns JWT token)
- `GET /api/profile/` - Get user profile (requires authentication)

### Chatbot Endpoint

- `POST /api/chatbot/` - Send message to chatbot (requires authentication)
  - **Headers:** `Authorization: Bearer <token>`
  - **Body:** `{"message": "your message here"}`
  - **Response:** `{"type": "text|profile_data|product_list|...", "payload": {...}}`

## 📊 Database Schema

The application uses Supabase (PostgreSQL) for data storage. Key tables include:

- **users** - User accounts and profiles
- **products** - Product catalog
- **orders** - Order records
- **order_items** - Order line items
- **cart_items** - Shopping cart items
- **complaints_updated** - Customer complaints
- **returns** - Return requests
- **meeting** - Scheduled support meetings
- **chat_logs_updated** - Chat conversation history

Refer to CSV files in `Resources/dbms mockdata/` for sample data structure.

## 🔐 Security Notes

1. **Never commit `.env` files** - They contain sensitive credentials
2. **Use environment variables** for all secrets
3. **Supabase Service Key** should only be used server-side
4. **JWT tokens** are validated on both frontend and backend
5. **CORS** is configured for development - restrict in production

## 🐛 Troubleshooting

### Backend Issues

**Import Errors:**
```bash
# Ensure virtual environment is activated
pip install -r requirements.txt
```

**Supabase Connection Errors:**
- Verify your `.env` file has correct Supabase credentials
- Check Supabase project is active and API keys are valid

**Gemini API Errors:**
- Verify `GEMINI_API_KEY` is set correctly
- Check API quota/limits in Google AI Studio

### Frontend Issues

**Build Errors:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API Connection Errors:**
- Verify `VITE_API_URL` points to `http://127.0.0.1:8000/api`
- Ensure Django backend is running
- Check browser console for CORS errors

**Authentication Errors:**
- Verify Supabase credentials in `.env`
- Check if user exists in Supabase Auth dashboard
- Clear browser localStorage and try again

## 🚢 Production Deployment

### Backend Deployment

1. Set `DEBUG=False` in production
2. Set proper `ALLOWED_HOSTS`
3. Use a production WSGI server (Gunicorn)
4. Configure proper database (PostgreSQL recommended)
5. Set up environment variables securely

### Frontend Deployment

1. Build the production bundle:
```bash
npm run build
```

2. Deploy the `dist/` folder to a static hosting service (Vercel, Netlify, etc.)
3. Update `VITE_API_URL` to your production backend URL

## 📝 Development Notes

- The chatbot uses **intent detection** to route queries to appropriate handlers
- **Google Gemini AI** generates JSON responses based on user queries
- **Context-aware** responses pull data from Supabase based on detected intent
- **Multi-turn conversations** are supported via chat history tracking
- **JWT tokens** from Supabase Auth are used for authentication

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is for educational/demonstration purposes.

## 🔗 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [React Documentation](https://react.dev/)
- [Supabase Documentation](https://supabase.com/docs)
- [Google Gemini AI](https://ai.google.dev/)
- [Vite Documentation](https://vitejs.dev/)

---

**Note:** This is a development project. Ensure all security best practices are followed before deploying to production.
