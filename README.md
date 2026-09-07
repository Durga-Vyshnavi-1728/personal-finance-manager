# 💰 Personal Finance Manager

A comprehensive personal finance management application with AI-powered insights, built with React + Flask + MySQL.

## 🚀 Features

### 👤 Module 1 — User Authentication
- Secure registration with name, email, and password
- Login/logout functionality
- Profile management with photo upload

### 📊 Module 2 — Dashboard
- Total Income, Expense, Savings & Balance overview
- Monthly budget tracking with progress bar
- Recent transactions list
- Savings goals progress tracking
- Budget warning at 80% and 90% thresholds

### 💵 Module 3 — Income Management
- Add income with categories: Salary, Freelancing, Scholarship, Gift, Other
- Date tracking and description notes

### 💸 Module 4 — Expense Management
- 8 expense categories: Food, Transport, Entertainment, Rent, Shopping, Bills, Education, Others
- Detailed transaction recording

### 📈 Module 5 — Analytics
- Pie chart for expense category breakdown
- Bar chart for monthly income vs expense vs savings comparison
- Visual percentage distribution

### 🎯 Module 6 — Budget Planner
- Set monthly budget limit
- Real-time tracking with color-coded progress bar
- Warning alerts at 80% and 90% usage

### 🤖 Module 7 — AI Insights (Gemini API)
- "Analyze My Spending" button for AI-powered analysis
- Optional Gemini API key for advanced insights
- Local smart analysis fallback when offline
- Actionable tips to improve savings

### 🎯 Module 8 — Savings Goals
- Create custom savings goals with target amounts
- Track progress with visual progress bars
- Add funds to goals incrementally
- Overall progress summary

### 📄 Module 9 — Reports
- Monthly report generation
- Export to PDF
- Print-friendly layout
- Transaction history table

### 🌙 Module 10 — Profile
- Update name, email, and password
- Profile photo upload
- Account information display

## 🛠 Tech Stack

### Frontend (React SPA)
- **React 19** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS 4** for styling
- **Chart.js** + react-chartjs-2 for visualizations
- **React Router** for navigation
- **Lucide React** for icons
- **jsPDF** + html2canvas for PDF export
- **Google Generative AI** SDK for Gemini API

### Backend (Flask API)
- **Python 3** with Flask
- **MySQL** database with mysql-connector-python
- **Gemini API** for AI-powered financial insights
- RESTful API architecture
- Session-based authentication

## 📁 Project Structure

```
Finance_Manager/
├── src/                          # React frontend
│   ├── App.tsx                   # Main app with routing
│   ├── main.tsx                  # Entry point
│   ├── index.css                 # Tailwind imports
│   ├── contexts/
│   │   ├── AuthContext.tsx       # Authentication state
│   │   └── FinanceContext.tsx    # Finance data & operations
│   ├── components/
│   │   ├── Layout.tsx            # Sidebar + main layout
│   │   └── Charts.tsx            # Pie & Bar chart components
│   └── pages/
│       ├── Login.tsx
│       ├── Register.tsx
│       ├── Dashboard.tsx
│       ├── AddIncome.tsx
│       ├── AddExpense.tsx
│       ├── Reports.tsx
│       ├── AIInsights.tsx
│       ├── SavingsGoal.tsx
│       └── Profile.tsx
├── app.py                        # Flask backend server
├── config.py                     # Backend configuration
├── requirements.txt              # Python dependencies
├── templates/                    # Flask HTML templates
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_income.html
│   ├── add_expense.html
│   ├── reports.html
│   ├── profile.html
│   └── includes/
│       └── sidebar.html
├── static/
│   ├── css/style.css            # Flask template styles
│   └── js/charts.js             # Chart.js for templates
├── database/
│   └── finance.sql              # MySQL schema + sample data
└── README.md
```

## 🚦 Getting Started

### React Frontend (SPA)

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

The React SPA uses **localStorage** for data persistence and works standalone without the backend.

### Flask Backend (Optional)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up MySQL database
mysql -u root -p < database/finance.sql

# Configure environment variables
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=finance_manager
export GEMINI_API_KEY=your_gemini_api_key

# Run Flask server
python app.py
```

## 📊 Database Schema

- **users** — User accounts with authentication
- **transactions** — All income and expense records
- **budgets** — Monthly budget per user
- **savings_goals** — Savings targets with progress tracking

## 🤖 Gemini API Integration

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/)
2. Enter it in the AI Insights page of the app
3. Click "Analyze My Spending" for personalized financial advice

Without an API key, the app provides smart local analysis based on your spending patterns.

## 📝 License

MIT License — Feel free to use and modify for personal or educational purposes.
