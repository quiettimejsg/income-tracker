// Enhanced Income Tracker Frontend
class IncomeTrackerApp {
    constructor() {
        this.currentUser = null;
        this.currentLanguage = 'zh';
        this.translations = {};
        this.categories = [];
        this.transactions = [];
        this.currentPage = 'login';
        this.isLoggedIn = false;
        
        this.init();
    }
    
    async init() {
        await this.loadTranslations();
        this.setupEventListeners();
        this.checkAuthStatus();
        this.updateLanguage();
    }
    
    async loadTranslations() {
        // 加载所有语言包
        const languages = ['zh', 'en', 'fr', 'es', 'de', 'ja', 'it', 'pt', 'ru', 'ar', 'ko', 'hi', 'id', 'tr', 'nl', 'pl', 'sv', 'vi', 'th', 'uk'];
        
        // 添加基础翻译作为后备
        this.translations = {
            zh: {
                app_title: '增强收入追踪器',
                auth: {
                    login: '登录',
                    register: '注册',
                    username: '用户名',
                    password: '密码',
                    email: '邮箱',
                    no_account: '没有账户？',
                    have_account: '已有账户？',
                    logout: '登出'
                },
                nav: {
                    dashboard: '仪表板',
                    transactions: '交易记录',
                    categories: '类别管理',
                    analytics: '数据分析'
                },
                dashboard: {
                    total_income: '总收入',
                    total_expense: '总支出',
                    net_income: '净收入',
                    quick_add: '快速添加',
                    recent_transactions: '最近交易',
                    no_transactions: '暂无交易记录'
                },
                transaction: {
                    income: '收入',
                    expense: '支出',
                    select_category: '选择类别'
                },
                common: {
                    add: '添加',
                    loading: '加载中...'
                }
            },
            en: {
                app_title: 'Enhanced Income Tracker',
                auth: {
                    login: 'Login',
                    register: 'Register',
                    username: 'Username',
                    password: 'Password',
                    email: 'Email',
                    no_account: 'No account?',
                    have_account: 'Have account?',
                    logout: 'Logout'
                },
                nav: {
                    dashboard: 'Dashboard',
                    transactions: 'Transactions',
                    categories: 'Categories',
                    analytics: 'Analytics'
                },
                dashboard: {
                    total_income: 'Total Income',
                    total_expense: 'Total Expense',
                    net_income: 'Net Income',
                    quick_add: 'Quick Add',
                    recent_transactions: 'Recent Transactions',
                    no_transactions: 'No transactions'
                },
                transaction: {
                    income: 'Income',
                    expense: 'Expense',
                    select_category: 'Select Category'
                },
                common: {
                    add: 'Add',
                    loading: 'Loading...'
                }
            }
        };
        
        // 尝试加载外部翻译文件
        for (const lang of languages) {
            try {
                const response = await fetch(`locales/${lang}.json`);
                if (response.ok) {
                    const translations = await response.json();
                    // 合并翻译
                    this.translations[lang] = { ...this.translations[lang], ...translations };
                }
            } catch (error) {
                console.warn(`Failed to load ${lang} translations:`, error);
            }
        }
        
        // 为没有翻译的语言使用英文作为后备
        for (const lang of languages) {
            if (!this.translations[lang]) {
                this.translations[lang] = this.translations.en;
            }
        }
    }
    
    setupEventListeners() {
        // 语言切换
        document.querySelectorAll('[id^="lang-"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const lang = e.target.id.replace('lang-', '');
                this.switchLanguage(lang);
            });
        });
        
        // 样式切换
        document.getElementById('style-old')?.addEventListener('click', () => {
            this.switchStyle('old');
        });
        
        document.getElementById('style-new')?.addEventListener('click', () => {
            this.switchStyle('new');
        });
        
        // 表单提交
        document.getElementById('income-form')?.addEventListener('submit', (e) => {
            this.handleFormSubmit(e);
        });
        
        // 导航事件
        this.setupNavigation();
    }
    
    setupNavigation() {
        // 添加导航按钮事件监听器
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-nav]')) {
                e.preventDefault();
                const page = e.target.getAttribute('data-nav');
                this.navigateTo(page);
            }
        });
    }
    
    async checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/me', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.currentUser = data.user;
                this.isLoggedIn = true;
                this.navigateTo('dashboard');
            } else {
                this.isLoggedIn = false;
                this.navigateTo('login');
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            this.isLoggedIn = false;
            this.navigateTo('login');
        }
    }
    
    switchLanguage(lang) {
        this.currentLanguage = lang;
        this.updateLanguage();
        
        // 更新活跃状态
        document.querySelectorAll('.language-switcher button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.getElementById(`lang-${lang}`)?.classList.add('active');
        
        // 保存语言偏好
        localStorage.setItem('preferredLanguage', lang);
        
        // 重新加载数据
        if (this.isLoggedIn) {
            this.loadTransactions();
            this.loadCategories();
        }
    }
    
    switchStyle(style) {
        const styleLink = document.getElementById('style-link');
        if (style === 'new') {
            styleLink.href = 'modernui.css';
        } else {
            styleLink.href = 'styles.css';
        }
        
        // 更新活跃状态
        document.querySelectorAll('.style-switcher button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.getElementById(`style-${style}`)?.classList.add('active');
        
        // 保存样式偏好
        localStorage.setItem('preferredStyle', style);
    }
    
    updateLanguage() {
        const translations = this.translations[this.currentLanguage] || this.translations['en'];
        
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const keyPath = el.getAttribute('data-i18n').split('.');
            let translation = translations;
            
            for (const key of keyPath) {
                if (translation && typeof translation === 'object' && key in translation) {
                    translation = translation[key];
                } else {
                    translation = `[[${keyPath.join('.')}]]`;
                    break;
                }
            }
            
            if (typeof translation === 'string') {
                el.textContent = translation;
            }
        });
        
        // 设置HTML语言属性
        document.documentElement.lang = this.currentLanguage;
        document.documentElement.dir = this.currentLanguage === 'ar' ? 'rtl' : 'ltr';
    }
    
    navigateTo(page) {
        this.currentPage = page;
        this.renderPage();
    }
    
    renderPage() {
        const app = document.getElementById('app') || document.body;
        
        switch (this.currentPage) {
            case 'login':
                this.renderLoginPage();
                break;
            case 'register':
                this.renderRegisterPage();
                break;
            case 'dashboard':
                this.renderDashboard();
                break;
            case 'transactions':
                this.renderTransactionsPage();
                break;
            case 'analytics':
                this.renderAnalyticsPage();
                break;
            default:
                this.renderDashboard();
        }
    }
    
    renderLoginPage() {
        const content = `
            <div class="auth-container">
                <div class="auth-form">
                    <h2 data-i18n="auth.login">登录</h2>
                    <form id="login-form">
                        <div class="form-group">
                            <label for="username" data-i18n="auth.username">用户名</label>
                            <input type="text" id="username" name="username" required>
                        </div>
                        <div class="form-group">
                            <label for="password" data-i18n="auth.password">密码</label>
                            <input type="password" id="password" name="password" required>
                        </div>
                        <button type="submit" data-i18n="auth.login">登录</button>
                    </form>
                    <p>
                        <span data-i18n="auth.no_account">没有账户？</span>
                        <a href="#" data-nav="register" data-i18n="auth.register">注册</a>
                    </p>
                </div>
            </div>
        `;
        
        this.updatePageContent(content);
        this.setupLoginForm();
    }
    
    renderRegisterPage() {
        const content = `
            <div class="auth-container">
                <div class="auth-form">
                    <h2 data-i18n="auth.register">注册</h2>
                    <form id="register-form">
                        <div class="form-group">
                            <label for="reg-username" data-i18n="auth.username">用户名</label>
                            <input type="text" id="reg-username" name="username" required>
                        </div>
                        <div class="form-group">
                            <label for="reg-email" data-i18n="auth.email">邮箱</label>
                            <input type="email" id="reg-email" name="email" required>
                        </div>
                        <div class="form-group">
                            <label for="reg-password" data-i18n="auth.password">密码</label>
                            <input type="password" id="reg-password" name="password" required>
                        </div>
                        <button type="submit" data-i18n="auth.register">注册</button>
                    </form>
                    <p>
                        <span data-i18n="auth.have_account">已有账户？</span>
                        <a href="#" data-nav="login" data-i18n="auth.login">登录</a>
                    </p>
                </div>
            </div>
        `;
        
        this.updatePageContent(content);
        this.setupRegisterForm();
    }
    
    renderAnalyticsPage() {
        if (!this.isLoggedIn) {
            this.navigateTo('login');
            return;
        }
        
        // 创建分析页面实例
        if (!this.analyticsPage) {
            this.analyticsPage = new AnalyticsPage(this);
        }
        
        const content = this.analyticsPage.render();
        this.updatePageContent(content);
        
        // 设置事件监听器
        this.analyticsPage.setupEventListeners();
        
        // 加载数据
        this.analyticsPage.loadAnalyticsData();
    }
    
    renderDashboard() {
        if (!this.isLoggedIn) {
            this.navigateTo('login');
            return;
        }
        
        const content = `
            <div class="dashboard">
                <header class="dashboard-header">
                    <h1 data-i18n="app_title">收入追踪器</h1>
                             <nav class="main-nav">
                        <a href="#" data-page="dashboard" class="nav-link active" data-i18n="nav.dashboard">仪表板</a>
                        <a href="#" data-page="transactions" class="nav-link" data-i18n="nav.transactions">交易记录</a>
                        <a href="#" data-page="categories" class="nav-link" data-i18n="nav.categories">类别管理</a>
                        <a href="#" data-page="analytics" class="nav-link" data-i18n="nav.analytics">数据分析</a>
                        <button id="logout-btn" class="logout-btn" data-i18n="auth.logout">登出</button>
                    </nav>av>
                </header>
                
                <main class="dashboard-main">
                    <div class="quick-stats">
                        <div class="stat-card">
                            <h3 data-i18n="dashboard.total_income">总收入</h3>
                            <div class="stat-value" id="total-income">¥0.00</div>
                        </div>
                        <div class="stat-card">
                            <h3 data-i18n="dashboard.total_expense">总支出</h3>
                            <div class="stat-value" id="total-expense">¥0.00</div>
                        </div>
                        <div class="stat-card">
                            <h3 data-i18n="dashboard.net_income">净收入</h3>
                            <div class="stat-value" id="net-income">¥0.00</div>
                        </div>
                    </div>
                    
                    <div class="quick-actions">
                        <h3 data-i18n="dashboard.quick_add">快速添加</h3>
                        <form id="quick-transaction-form">
                            <div class="form-row">
                                <select id="quick-type" name="type" required>
                                    <option value="income" data-i18n="transaction.income">收入</option>
                                    <option value="expense" data-i18n="transaction.expense">支出</option>
                                </select>
                                <input type="number" id="quick-amount" name="amount" placeholder="金额" step="0.01" required>
                                <select id="quick-category" name="category_id" required>
                                    <option value="" data-i18n="transaction.select_category">选择类别</option>
                                </select>
                                <input type="date" id="quick-date" name="date" required>
                                <input type="text" id="quick-description" name="description" placeholder="描述（可选）">
                                <button type="submit" data-i18n="common.add">添加</button>
                            </div>
                        </form>
                    </div>
                    
                    <div class="recent-transactions">
                        <h3 data-i18n="dashboard.recent_transactions">最近交易</h3>
                        <div id="recent-transactions-list"></div>
                    </div>
                </main>
            </div>
        `;
        
        this.updatePageContent(content);
        this.setupDashboard();
    }
    
    updatePageContent(content) {
        // 保留语言和样式切换器
        const languageSwitcher = document.querySelector('.language-switcher')?.outerHTML || '';
        const styleSwitcher = document.querySelector('.style-switcher')?.outerHTML || '';
        
        document.body.innerHTML = `
            ${languageSwitcher}
            ${styleSwitcher}
            ${content}
        `;
        
        // 重新设置事件监听器
        this.setupEventListeners();
        this.updateLanguage();
    }
    
    setupLoginForm() {
        const form = document.getElementById('login-form');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleLogin(new FormData(form));
            });
        }
    }
    
    setupRegisterForm() {
        const form = document.getElementById('register-form');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleRegister(new FormData(form));
            });
        }
    }
    
    setupDashboard() {
        // 设置登出按钮
        document.getElementById('logout-btn')?.addEventListener('click', () => {
            this.handleLogout();
        });
        
        // 设置快速交易表单
        const quickForm = document.getElementById('quick-transaction-form');
        if (quickForm) {
            quickForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleQuickTransaction(new FormData(quickForm));
            });
        }
        
        // 设置类型切换
        document.getElementById('quick-type')?.addEventListener('change', (e) => {
            this.updateCategoryOptions(e.target.value);
        });
        
        // 设置默认日期
        const dateInput = document.getElementById('quick-date');
        if (dateInput) {
            dateInput.value = new Date().toISOString().split('T')[0];
        }
        
        // 加载数据
        this.loadDashboardData();
    }
    
    async handleLogin(formData) {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept-Language': this.currentLanguage
                },
                credentials: 'include',
                body: JSON.stringify({
                    username: formData.get('username'),
                    password: formData.get('password')
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.currentUser = data.user;
                this.isLoggedIn = true;
                this.showMessage(data.message, 'success');
                this.navigateTo('dashboard');
            } else {
                this.showMessage(data.error, 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showMessage('登录失败，请重试', 'error');
        }
    }
    
    async handleRegister(formData) {
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept-Language': this.currentLanguage
                },
                credentials: 'include',
                body: JSON.stringify({
                    username: formData.get('username'),
                    email: formData.get('email'),
                    password: formData.get('password')
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showMessage(data.message, 'success');
                this.navigateTo('login');
            } else {
                this.showMessage(data.error, 'error');
            }
        } catch (error) {
            console.error('Register error:', error);
            this.showMessage('注册失败，请重试', 'error');
        }
    }
    
    async handleLogout() {
        try {
            const response = await fetch('/api/auth/logout', {
                method: 'POST',
                credentials: 'include'
            });
            
            if (response.ok) {
                this.currentUser = null;
                this.isLoggedIn = false;
                this.navigateTo('login');
            }
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
    
    async loadDashboardData() {
        await Promise.all([
            this.loadCategories(),
            this.loadOverviewStats(),
            this.loadRecentTransactions()
        ]);
    }
    
    async loadCategories() {
        try {
            const response = await fetch('/api/categories', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.categories = data.categories;
                this.updateCategoryOptions('income'); // 默认显示收入类别
            }
        } catch (error) {
            console.error('Load categories error:', error);
        }
    }
    
    updateCategoryOptions(type) {
        const select = document.getElementById('quick-category');
        if (!select) return;
        
        const filteredCategories = this.categories.filter(cat => cat.type === type);
        
        select.innerHTML = '<option value="" data-i18n="transaction.select_category">选择类别</option>';
        
        filteredCategories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.name;
            select.appendChild(option);
        });
    }
    
    async loadOverviewStats() {
        try {
            const response = await fetch('/api/analytics/overview?period=month', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateOverviewStats(data.summary);
            }
        } catch (error) {
            console.error('Load overview stats error:', error);
        }
    }
    
    updateOverviewStats(summary) {
        document.getElementById('total-income').textContent = `¥${summary.total_income.toFixed(2)}`;
        document.getElementById('total-expense').textContent = `¥${summary.total_expense.toFixed(2)}`;
        document.getElementById('net-income').textContent = `¥${summary.net_income.toFixed(2)}`;
    }
    
    async loadRecentTransactions() {
        try {
            const response = await fetch('/api/transactions?per_page=5&sort_by=created_at&sort_order=desc', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.renderRecentTransactions(data.transactions);
            }
        } catch (error) {
            console.error('Load recent transactions error:', error);
        }
    }
    
    renderRecentTransactions(transactions) {
        const container = document.getElementById('recent-transactions-list');
        if (!container) return;
        
        if (transactions.length === 0) {
            container.innerHTML = '<p data-i18n="dashboard.no_transactions">暂无交易记录</p>';
            return;
        }
        
        const html = transactions.map(transaction => `
            <div class="transaction-item ${transaction.type}">
                <div class="transaction-info">
                    <span class="transaction-category">${transaction.category?.name || ''}</span>
                    <span class="transaction-description">${transaction.description || ''}</span>
                </div>
                <div class="transaction-amount ${transaction.type}">
                    ${transaction.type === 'income' ? '+' : '-'}¥${transaction.amount.toFixed(2)}
                </div>
                <div class="transaction-date">${transaction.date}</div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }
    
    async handleQuickTransaction(formData) {
        try {
            const response = await fetch('/api/transactions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept-Language': this.currentLanguage
                },
                credentials: 'include',
                body: JSON.stringify({
                    type: formData.get('type'),
                    amount: parseFloat(formData.get('amount')),
                    category_id: parseInt(formData.get('category_id')),
                    date: formData.get('date'),
                    description: formData.get('description')
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showMessage(data.message, 'success');
                document.getElementById('quick-transaction-form').reset();
                document.getElementById('quick-date').value = new Date().toISOString().split('T')[0];
                
                // 重新加载数据
                this.loadDashboardData();
            } else {
                this.showMessage(data.error, 'error');
            }
        } catch (error) {
            console.error('Quick transaction error:', error);
            this.showMessage('添加交易失败，请重试', 'error');
        }
    }
    
    showMessage(message, type = 'info') {
        // 创建消息元素
        const messageEl = document.createElement('div');
        messageEl.className = `message message-${type}`;
        messageEl.textContent = message;
        
        // 添加到页面
        document.body.appendChild(messageEl);
        
        // 自动移除
        setTimeout(() => {
            messageEl.remove();
        }, 3000);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new IncomeTrackerApp();
});

