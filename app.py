"""
Personal Finance Manager - Flask Backend
========================================
This is the backend server for the Personal Finance Manager application.
It provides REST API endpoints for user authentication, transaction management,
budget tracking, savings goals, and AI-powered financial insights.

Tech Stack: Python, Flask, MySQL, Gemini API
"""

from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
from config import Config
import mysql.connector
from datetime import datetime
from functools import wraps
import google.generativeai as genai

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, supports_credentials=True)

# ============================================
# Database Connection
# ============================================

def get_db():
    """Get MySQL database connection."""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )

# ============================================
# Authentication Decorator
# ============================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# Page Routes (serve HTML templates)
# ============================================

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/add-income')
def add_income_page():
    return render_template('add_income.html')

@app.route('/add-expense')
def add_expense_page():
    return render_template('add_expense.html')

@app.route('/reports')
def reports_page():
    return render_template('reports.html')

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

# ============================================
# Module 1: User Authentication API
# ============================================

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    db = get_db()
    cursor = db.cursor()

    # Check if email already exists
    cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
    if cursor.fetchone():
        cursor.close()
        db.close()
        return jsonify({'error': 'Email already registered'}), 409

    # Insert user
    cursor.execute(
        'INSERT INTO users (name, email, password) VALUES (%s, %s, %s)',
        (name, email, password)
    )
    db.commit()
    user_id = cursor.lastrowid
    cursor.close()
    db.close()

    session['user_id'] = user_id
    return jsonify({'message': 'Registration successful', 'user': {'id': user_id, 'name': name, 'email': email}}), 201


@app.route('/api/login', methods=['POST'])
def login():
    """Login user."""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    session['user_id'] = user['id']
    return jsonify({'message': 'Login successful', 'user': {
        'id': user['id'], 'name': user['name'], 'email': user['email']
    }}), 200


@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user."""
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    """Get or update user profile."""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute('SELECT id, name, email, photo, created_at FROM users WHERE id = %s', (session['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        return jsonify(user), 200

    # PUT: Update profile
    data = request.get_json()
    updates = []
    params = []

    if 'name' in data:
        updates.append('name = %s')
        params.append(data['name'])
    if 'email' in data:
        updates.append('email = %s')
        params.append(data['email'])
    if 'password' in data:
        updates.append('password = %s')
        params.append(data['password'])
    if 'photo' in data:
        updates.append('photo = %s')
        params.append(data['photo'])

    if updates:
        params.append(session['user_id'])
        cursor.execute(f'UPDATE users SET {", ".join(updates)} WHERE id = %s', params)
        db.commit()

    cursor.close()
    db.close()
    return jsonify({'message': 'Profile updated successfully'}), 200


# ============================================
# Module 2 & 3: Income & Expense Transactions
# ============================================

@app.route('/api/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    """Get all transactions or add a new one."""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'GET':
        month = request.args.get('month', '')  # Format: YYYY-MM
        query = 'SELECT * FROM transactions WHERE user_id = %s'
        params = [session['user_id']]

        if month:
            query += ' AND DATE_FORMAT(date, "%Y-%m") = %s'
            params.append(month)

        query += ' ORDER BY date DESC'
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(transactions), 200

    # POST: Add transaction
    data = request.get_json()
    trans_type = data.get('type')  # 'income' or 'expense'
    category = data.get('category', '')
    amount = data.get('amount', 0)
    description = data.get('description', '')
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))

    if trans_type not in ('income', 'expense'):
        return jsonify({'error': 'Type must be income or expense'}), 400
    if not category or float(amount) <= 0:
        return jsonify({'error': 'Category and valid amount are required'}), 400

    cursor.execute(
        'INSERT INTO transactions (user_id, type, category, amount, description, date) VALUES (%s, %s, %s, %s, %s, %s)',
        (session['user_id'], trans_type, category, float(amount), description, date)
    )
    db.commit()
    tx_id = cursor.lastrowid
    cursor.close()
    db.close()

    return jsonify({'message': 'Transaction added', 'id': tx_id}), 201


@app.route('/api/transactions/<int:tx_id>', methods=['DELETE'])
@login_required
def delete_transaction(tx_id):
    """Delete a transaction."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = %s AND user_id = %s', (tx_id, session['user_id']))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'message': 'Transaction deleted'}), 200


# ============================================
# Module 4: Dashboard Summary
# ============================================

@app.route('/api/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Get dashboard summary data."""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Total income
    cursor.execute('SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = %s AND type = %s',
                   (session['user_id'], 'income'))
    total_income = float(cursor.fetchone()['total'])

    # Total expense
    cursor.execute('SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = %s AND type = %s',
                   (session['user_id'], 'expense'))
    total_expense = float(cursor.fetchone()['total'])

    # Current month's budget
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('SELECT monthly_budget FROM budgets WHERE user_id = %s AND month = %s',
                   (session['user_id'], current_month))
    budget_row = cursor.fetchone()
    monthly_budget = float(budget_row['monthly_budget']) if budget_row else 0

    # Category breakdown for expenses
    cursor.execute(
        'SELECT category, SUM(amount) as total FROM transactions WHERE user_id = %s AND type = %s GROUP BY category',
        (session['user_id'], 'expense')
    )
    categories = cursor.fetchall()

    # Recent transactions
    cursor.execute('SELECT * FROM transactions WHERE user_id = %s ORDER BY date DESC LIMIT 10',
                   (session['user_id'],))
    recent = cursor.fetchall()

    # Savings goals
    cursor.execute('SELECT * FROM savings_goals WHERE user_id = %s', (session['user_id'],))
    goals = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify({
        'total_income': total_income,
        'total_expense': total_expense,
        'savings': total_income - total_expense,
        'current_balance': total_income - total_expense,
        'monthly_budget': monthly_budget,
        'budget_used_percent': round((total_expense / monthly_budget) * 100, 1) if monthly_budget > 0 else 0,
        'category_breakdown': categories,
        'recent_transactions': recent,
        'savings_goals': goals,
    }), 200


# ============================================
# Module 5: Budget Planner
# ============================================

@app.route('/api/budget', methods=['GET', 'POST'])
@login_required
def budget():
    """Get or set monthly budget."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    current_month = datetime.now().strftime('%Y-%m')

    if request.method == 'GET':
        cursor.execute('SELECT * FROM budgets WHERE user_id = %s AND month = %s',
                       (session['user_id'], current_month))
        budget_data = cursor.fetchone()
        cursor.close()
        db.close()
        return jsonify(budget_data or {'monthly_budget': 0}), 200

    # POST: Set budget
    data = request.get_json()
    amount = float(data.get('monthly_budget', 0))

    if amount <= 0:
        return jsonify({'error': 'Budget must be greater than 0'}), 400

    # Upsert
    cursor.execute(
        'INSERT INTO budgets (user_id, month, monthly_budget) VALUES (%s, %s, %s) '
        'ON DUPLICATE KEY UPDATE monthly_budget = %s',
        (session['user_id'], current_month, amount, amount)
    )
    db.commit()
    cursor.close()
    db.close()

    return jsonify({'message': 'Budget updated', 'monthly_budget': amount}), 200


# ============================================
# Module 6: Savings Goals
# ============================================

@app.route('/api/savings-goals', methods=['GET', 'POST'])
@login_required
def savings_goals():
    """Get all savings goals or create a new one."""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute('SELECT * FROM savings_goals WHERE user_id = %s ORDER BY created_at DESC',
                       (session['user_id'],))
        goals = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(goals), 200

    # POST: Create goal
    data = request.get_json()
    name = data.get('name', '').strip()
    target_amount = float(data.get('target_amount', 0))

    if not name or target_amount <= 0:
        return jsonify({'error': 'Name and valid target amount are required'}), 400

    cursor.execute(
        'INSERT INTO savings_goals (user_id, name, target_amount, current_amount) VALUES (%s, %s, %s, 0)',
        (session['user_id'], name, target_amount)
    )
    db.commit()
    goal_id = cursor.lastrowid
    cursor.close()
    db.close()

    return jsonify({'message': 'Savings goal created', 'id': goal_id}), 201


@app.route('/api/savings-goals/<int:goal_id>/contribute', methods=['POST'])
@login_required
def contribute_to_goal(goal_id):
    """Add funds to a savings goal."""
    data = request.get_json()
    amount = float(data.get('amount', 0))

    if amount <= 0:
        return jsonify({'error': 'Amount must be greater than 0'}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute('SELECT * FROM savings_goals WHERE id = %s AND user_id = %s', (goal_id, session['user_id']))
    goal = cursor.fetchone()

    if not goal:
        cursor.close()
        db.close()
        return jsonify({'error': 'Goal not found'}), 404

    new_amount = min(goal['target_amount'], float(goal['current_amount']) + amount)
    cursor.execute('UPDATE savings_goals SET current_amount = %s WHERE id = %s', (new_amount, goal_id))
    db.commit()
    cursor.close()
    db.close()

    return jsonify({'message': 'Contribution added', 'current_amount': new_amount}), 200


@app.route('/api/savings-goals/<int:goal_id>', methods=['DELETE'])
@login_required
def delete_savings_goal(goal_id):
    """Delete a savings goal."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM savings_goals WHERE id = %s AND user_id = %s', (goal_id, session['user_id']))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'message': 'Savings goal deleted'}), 200


# ============================================
# Module 7: AI Insights (Gemini API)
# ============================================

@app.route('/api/ai-insights', methods=['GET'])
@login_required
def ai_insights():
    """Generate AI-powered financial insights using Gemini API."""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Gather financial data
    cursor.execute('SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = %s AND type = %s',
                   (session['user_id'], 'income'))
    total_income = float(cursor.fetchone()['total'])

    cursor.execute('SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = %s AND type = %s',
                   (session['user_id'], 'expense'))
    total_expense = float(cursor.fetchone()['total'])

    cursor.execute(
        'SELECT category, SUM(amount) as total FROM transactions WHERE user_id = %s AND type = %s GROUP BY category',
        (session['user_id'], 'expense')
    )
    categories = cursor.fetchall()
    cursor.close()
    db.close()

    savings = total_income - total_expense

    # Build spending summary
    total_exp = total_expense if total_expense > 0 else 1
    spending_summary = ', '.join([
        f"{c['category']}: ₹{float(c['total']):,.2f} ({round(float(c['total'])/total_exp*100)}%)"
        for c in categories
    ])

    prompt = f"""Act as a friendly financial advisor. Here is the user's financial data:
Total Income: ₹{total_income:,.2f}
Total Expenses: ₹{total_expense:,.2f}
Savings: ₹{savings:,.2f}
Expense Breakdown: {spending_summary}

Please provide:
1. A brief analysis of spending patterns (2-3 sentences)
2. 2-3 specific, actionable tips to improve savings
3. One positive observation about their financial habits
Keep it friendly and encouraging. Use ₹ (Indian Rupees) for currency."""

    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        insights = response.text
    except Exception as e:
        # Fallback: Local smart analysis
        insights = generate_local_insights(total_income, total_expense, savings, categories)

    return jsonify({'insights': insights}), 200


def generate_local_insights(total_income, total_expense, savings, categories):
    """Generate insights locally if Gemini API is unavailable."""
    lines = ['📊 **Spending Analysis**']

    if total_income == 0:
        lines.append('Add some income and expense data first for insights!')
        return '\n'.join(lines)

    savings_rate = round((savings / total_income) * 100) if total_income > 0 else 0
    lines.append(f'Your savings rate is {savings_rate}% of your income.')

    if categories:
        top = categories[0]
        pct = round(float(top['total']) / (total_expense or 1) * 100)
        lines.append(f'Your top spending category is **{top["category"]}** at {pct}%.')

        if pct > 30:
            reduction = round(float(top['total']) * 0.1, 2)
            lines.append(f'💡 Reducing {top["category"]} by 10% could save ₹{reduction:,.2f} monthly.')

    if savings_rate < 20:
        lines.append('💡 Aim to save at least 20% of income per financial experts.')
    else:
        lines.append('🌟 Great job saving above the recommended 20%!')

    lines.append('💡 Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings.')
    return '\n'.join(lines)


# ============================================
# Module 8: Monthly Reports
# ============================================

@app.route('/api/reports/monthly', methods=['GET'])
@login_required
def monthly_report():
    """Generate monthly report data for the last 6 months."""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    monthly_data = []
    for i in range(5, -1, -1):
        month_date = datetime(datetime.now().year, datetime.now().month - i, 1)
        month_str = month_date.strftime('%Y-%m')

        cursor.execute(
            'SELECT type, COALESCE(SUM(amount), 0) as total FROM transactions '
            'WHERE user_id = %s AND DATE_FORMAT(date, "%Y-%m") = %s GROUP BY type',
            (session['user_id'], month_str)
        )
        rows = cursor.fetchall()

        income = 0.0
        expense = 0.0
        for row in rows:
            if row['type'] == 'income':
                income = float(row['total'])
            else:
                expense = float(row['total'])

        monthly_data.append({
            'month': month_date.strftime('%b %Y'),
            'month_key': month_str,
            'income': income,
            'expense': expense,
            'savings': income - expense,
        })

    cursor.close()
    db.close()
    return jsonify(monthly_data), 200


# ============================================
# Main Entry Point
# ============================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)
