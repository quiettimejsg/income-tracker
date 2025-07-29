// Analytics Page Module
class AnalyticsPage {
    constructor(app) {
        this.app = app;
        this.currentPeriod = 'month';
        this.currentType = 'expense';
        this.analyticsData = {};
    }
    
    render() {
        const content = `
            <div class="analytics-page">
                <header class="page-header">
                    <h1 data-i18n="nav.analytics">数据分析</h1>
                    <div class="period-selector">
                        <select id="period-select">
                            <option value="week" data-i18n="analytics.week">本周</option>
                            <option value="month" selected data-i18n="analytics.month">本月</option>
                            <option value="quarter" data-i18n="analytics.quarter">本季度</option>
                            <option value="year" data-i18n="analytics.year">本年</option>
                            <option value="custom" data-i18n="analytics.custom">自定义</option>
                        </select>
                        <div id="custom-date-range" class="custom-date-range" style="display: none;">
                            <input type="date" id="start-date" placeholder="开始日期">
                            <input type="date" id="end-date" placeholder="结束日期">
                            <button id="apply-custom-range" data-i18n="common.apply">应用</button>
                        </div>
                    </div>
                </header>
                
                <div class="analytics-content">
                    <!-- 概览统计 -->
                    <section class="overview-section">
                        <h2 data-i18n="analytics.overview">概览统计</h2>
                        <div class="overview-stats">
                            <div id="income-stat" class="stat-card income">
                                <h3 data-i18n="dashboard.total_income">总收入</h3>
                                <div class="stat-value">¥0.00</div>
                                <div class="stat-change"></div>
                            </div>
                            <div id="expense-stat" class="stat-card expense">
                                <h3 data-i18n="dashboard.total_expense">总支出</h3>
                                <div class="stat-value">¥0.00</div>
                                <div class="stat-change"></div>
                            </div>
                            <div id="net-stat" class="stat-card net">
                                <h3 data-i18n="dashboard.net_income">净收入</h3>
                                <div class="stat-value">¥0.00</div>
                                <div class="stat-change"></div>
                            </div>
                            <div id="transaction-count-stat" class="stat-card count">
                                <h3 data-i18n="analytics.transaction_count">交易笔数</h3>
                                <div class="stat-value">0</div>
                                <div class="stat-change"></div>
                            </div>
                        </div>
                    </section>
                    
                    <!-- 趋势分析 -->
                    <section class="trends-section">
                        <h2 data-i18n="analytics.trends">趋势分析</h2>
                        <div class="chart-container">
                            <canvas id="trends-chart"></canvas>
                        </div>
                    </section>
                    
                    <!-- 类别分析 -->
                    <section class="categories-section">
                        <h2 data-i18n="analytics.category_analysis">类别分析</h2>
                        <div class="category-controls">
                            <div class="type-selector">
                                <button id="income-type-btn" class="type-btn" data-type="income" data-i18n="transaction.income">收入</button>
                                <button id="expense-type-btn" class="type-btn active" data-type="expense" data-i18n="transaction.expense">支出</button>
                            </div>
                        </div>
                        <div class="category-analysis-content">
                            <div class="chart-container">
                                <canvas id="category-chart"></canvas>
                            </div>
                            <div class="category-details">
                                <h3 data-i18n="analytics.category_details">类别详情</h3>
                                <div id="category-list" class="category-list"></div>
                            </div>
                        </div>
                    </section>
                    
                    <!-- 月度对比 -->
                    <section class="monthly-comparison-section">
                        <h2 data-i18n="analytics.monthly_comparison">月度对比</h2>
                        <div class="chart-container">
                            <canvas id="monthly-chart"></canvas>
                        </div>
                    </section>
                    
                    <!-- 收支平衡 -->
                    <section class="balance-section">
                        <h2 data-i18n="analytics.balance">收支平衡</h2>
                        <div class="balance-content">
                            <div class="chart-container">
                                <canvas id="balance-chart"></canvas>
                            </div>
                            <div class="balance-insights">
                                <h3 data-i18n="analytics.insights">财务洞察</h3>
                                <div id="insights-list" class="insights-list"></div>
                            </div>
                        </div>
                    </section>
                    
                    <!-- 导出功能 -->
                    <section class="export-section">
                        <h2 data-i18n="analytics.export">数据导出</h2>
                        <div class="export-controls">
                            <button id="export-csv-btn" class="export-btn" data-i18n="analytics.export_csv">导出CSV</button>
                            <button id="export-json-btn" class="export-btn" data-i18n="analytics.export_json">导出JSON</button>
                            <button id="export-charts-btn" class="export-btn" data-i18n="analytics.export_charts">导出图表</button>
                        </div>
                    </section>
                </div>
            </div>
        `;
        
        return content;
    }
    
    setupEventListeners() {
        // 时间段选择
        document.getElementById('period-select')?.addEventListener('change', (e) => {
            this.currentPeriod = e.target.value;
            this.toggleCustomDateRange();
            if (this.currentPeriod !== 'custom') {
                this.loadAnalyticsData();
            }
        });
        
        // 自定义日期范围
        document.getElementById('apply-custom-range')?.addEventListener('click', () => {
            this.loadAnalyticsData();
        });
        
        // 类别类型切换
        document.querySelectorAll('.type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentType = e.target.getAttribute('data-type');
                this.loadCategoryAnalysis();
            });
        });
        
        // 导出功能
        document.getElementById('export-csv-btn')?.addEventListener('click', () => {
            this.exportData('csv');
        });
        
        document.getElementById('export-json-btn')?.addEventListener('click', () => {
            this.exportData('json');
        });
        
        document.getElementById('export-charts-btn')?.addEventListener('click', () => {
            this.exportCharts();
        });
    }
    
    toggleCustomDateRange() {
        const customRange = document.getElementById('custom-date-range');
        if (customRange) {
            customRange.style.display = this.currentPeriod === 'custom' ? 'flex' : 'none';
        }
    }
    
    async loadAnalyticsData() {
        try {
            // 显示加载状态
            this.showLoading();
            
            // 并行加载所有数据
            await Promise.all([
                this.loadOverviewData(),
                this.loadTrendsData(),
                this.loadCategoryAnalysis(),
                this.loadMonthlyComparison(),
                this.loadBalanceData()
            ]);
            
            // 隐藏加载状态
            this.hideLoading();
            
        } catch (error) {
            console.error('Load analytics data error:', error);
            this.app.showMessage('加载分析数据失败', 'error');
        }
    }
    
    async loadOverviewData() {
        const params = this.getDateParams();
        const response = await fetch(`/api/analytics/overview?${params}`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            this.analyticsData.overview = data;
            this.updateOverviewStats(data.summary, data.changes);
        }
    }
    
    async loadTrendsData() {
        const params = this.getDateParams();
        const response = await fetch(`/api/analytics/trends?${params}&group_by=day`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            this.analyticsData.trends = data;
            this.updateTrendsChart(data);
        }
    }
    
    async loadCategoryAnalysis() {
        const params = this.getDateParams();
        const response = await fetch(`/api/analytics/categories?${params}&type=${this.currentType}`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            this.analyticsData.categories = data;
            this.updateCategoryChart(data);
            this.updateCategoryDetails(data.categories);
        }
    }
    
    async loadMonthlyComparison() {
        const response = await fetch('/api/analytics/monthly-comparison?months=6', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            this.analyticsData.monthly = data;
            this.updateMonthlyChart(data.monthly_comparison);
        }
    }
    
    async loadBalanceData() {
        const params = this.getDateParams();
        const response = await fetch(`/api/analytics/overview?${params}`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            this.updateBalanceChart(data.summary);
            this.generateInsights(data.summary);
        }
    }
    
    getDateParams() {
        const params = new URLSearchParams();
        params.append('period', this.currentPeriod);
        
        if (this.currentPeriod === 'custom') {
            const startDate = document.getElementById('start-date')?.value;
            const endDate = document.getElementById('end-date')?.value;
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);
        }
        
        return params.toString();
    }
    
    updateOverviewStats(summary, changes) {
        // 更新收入统计
        const incomeCard = document.getElementById('income-stat');
        if (incomeCard) {
            incomeCard.querySelector('.stat-value').textContent = `¥${summary.total_income.toFixed(2)}`;
            this.updateChangeIndicator(incomeCard, changes.income_change);
        }
        
        // 更新支出统计
        const expenseCard = document.getElementById('expense-stat');
        if (expenseCard) {
            expenseCard.querySelector('.stat-value').textContent = `¥${summary.total_expense.toFixed(2)}`;
            this.updateChangeIndicator(expenseCard, changes.expense_change);
        }
        
        // 更新净收入统计
        const netCard = document.getElementById('net-stat');
        if (netCard) {
            netCard.querySelector('.stat-value').textContent = `¥${summary.net_income.toFixed(2)}`;
            const netChange = changes.income_change - changes.expense_change;
            this.updateChangeIndicator(netCard, netChange);
        }
        
        // 更新交易笔数统计
        const countCard = document.getElementById('transaction-count-stat');
        if (countCard) {
            countCard.querySelector('.stat-value').textContent = summary.total_transactions;
        }
    }
    
    updateChangeIndicator(card, change) {
        const changeEl = card.querySelector('.stat-change');
        if (changeEl && change !== undefined) {
            const isPositive = change > 0;
            const isNegative = change < 0;
            
            changeEl.textContent = `${isPositive ? '↗' : isNegative ? '↘' : '→'} ${Math.abs(change).toFixed(1)}%`;
            changeEl.className = `stat-change ${isPositive ? 'positive' : isNegative ? 'negative' : 'neutral'}`;
        }
    }
    
    updateTrendsChart(data) {
        const chartData = {
            labels: data.income_trends.map(item => item.date),
            income: data.income_trends.map(item => item.amount),
            expense: data.expense_trends.map(item => item.amount)
        };
        
        window.chartsManager.createTrendChart('trends-chart', chartData);
    }
    
    updateCategoryChart(data) {
        window.chartsManager.createCategoryPieChart('category-chart', data.categories, this.currentType);
    }
    
    updateCategoryDetails(categories) {
        const container = document.getElementById('category-list');
        if (!container) return;
        
        const html = categories.map(category => `
            <div class="category-item">
                <div class="category-info">
                    <div class="category-color" style="background-color: ${category.color}"></div>
                    <span class="category-name">${category.name}</span>
                </div>
                <div class="category-stats">
                    <span class="category-amount">¥${category.amount.toFixed(2)}</span>
                    <span class="category-percentage">${category.percentage}%</span>
                    <span class="category-count">${category.transaction_count}笔</span>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }
    
    updateMonthlyChart(data) {
        window.chartsManager.createMonthlyComparisonChart('monthly-chart', data);
    }
    
    updateBalanceChart(summary) {
        window.chartsManager.createBalanceChart('balance-chart', {
            income: summary.total_income,
            expense: summary.total_expense
        });
    }
    
    generateInsights(summary) {
        const container = document.getElementById('insights-list');
        if (!container) return;
        
        const insights = [];
        
        // 收支比例分析
        const savingsRate = ((summary.net_income / summary.total_income) * 100).toFixed(1);
        if (summary.net_income > 0) {
            insights.push(`您的储蓄率为 ${savingsRate}%，表现良好！`);
        } else {
            insights.push(`本期支出超过收入，建议控制支出。`);
        }
        
        // 支出分析
        if (summary.total_expense > summary.total_income * 0.8) {
            insights.push('支出占收入比例较高，建议优化支出结构。');
        }
        
        // 交易频率分析
        if (summary.total_transactions > 50) {
            insights.push('交易频率较高，建议定期整理和分析消费习惯。');
        }
        
        const html = insights.map(insight => `
            <div class="insight-item">
                <span class="insight-icon">💡</span>
                <span class="insight-text">${insight}</span>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }
    
    async exportData(format) {
        try {
            const params = this.getDateParams();
            const response = await fetch(`/api/analytics/export?${params}&format=${format}`, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (format === 'csv') {
                    this.downloadFile(data.csv_data, data.filename, 'text/csv');
                } else {
                    this.downloadFile(JSON.stringify(data, null, 2), 'analytics_data.json', 'application/json');
                }
                
                this.app.showMessage('数据导出成功', 'success');
            } else {
                throw new Error('导出失败');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.app.showMessage('数据导出失败', 'error');
        }
    }
    
    exportCharts() {
        // 导出所有图表
        const charts = ['trends-chart', 'category-chart', 'monthly-chart', 'balance-chart'];
        
        charts.forEach(chartId => {
            window.chartsManager.exportChart(chartId, `${chartId}_${Date.now()}.png`);
        });
        
        this.app.showMessage('图表导出成功', 'success');
    }
    
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(url);
    }
    
    showLoading() {
        // 显示加载状态
        document.querySelectorAll('.chart-container').forEach(container => {
            container.classList.add('loading');
        });
    }
    
    hideLoading() {
        // 隐藏加载状态
        document.querySelectorAll('.chart-container').forEach(container => {
            container.classList.remove('loading');
        });
    }
    
    destroy() {
        // 销毁所有图表
        window.chartsManager.destroyAllCharts();
    }
}

