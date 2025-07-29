// Charts and Data Visualization Module
class ChartsManager {
    constructor() {
        this.charts = {};
        this.colors = {
            income: '#28a745',
            expense: '#dc3545',
            primary: '#007bff',
            secondary: '#6c757d',
            success: '#28a745',
            danger: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        
        // 预定义的类别颜色
        this.categoryColors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
            '#4BC0C0', '#FF6384', '#36A2EB', '#FFCE56'
        ];
    }
    
    // 创建收支趋势图
    createTrendChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;
        
        // 销毁现有图表
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }
        
        const chartData = {
            labels: data.labels,
            datasets: [
                {
                    label: '收入',
                    data: data.income,
                    borderColor: this.colors.income,
                    backgroundColor: this.colors.income + '20',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: '支出',
                    data: data.expense,
                    borderColor: this.colors.expense,
                    backgroundColor: this.colors.expense + '20',
                    fill: true,
                    tension: 0.4
                }
            ]
        };
        
        this.charts[containerId] = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '收支趋势图'
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '¥' + value.toFixed(2);
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
        
        return this.charts[containerId];
    }
    
    // 创建类别饼图
    createCategoryPieChart(containerId, data, type = 'expense') {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;
        
        // 销毁现有图表
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }
        
        const chartData = {
            labels: data.map(item => item.name),
            datasets: [{
                data: data.map(item => item.amount),
                backgroundColor: data.map((item, index) => 
                    item.color || this.categoryColors[index % this.categoryColors.length]
                ),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        };
        
        this.charts[containerId] = new Chart(ctx, {
            type: 'doughnut',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: type === 'income' ? '收入类别分布' : '支出类别分布'
                    },
                    legend: {
                        position: 'right',
                        labels: {
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => {
                                        const dataset = data.datasets[0];
                                        const value = dataset.data[i];
                                        const total = dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        
                                        return {
                                            text: `${label} (${percentage}%)`,
                                            fillStyle: dataset.backgroundColor[i],
                                            strokeStyle: dataset.borderColor,
                                            lineWidth: dataset.borderWidth,
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ¥${value.toFixed(2)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
        
        return this.charts[containerId];
    }
    
    // 创建月度对比柱状图
    createMonthlyComparisonChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;
        
        // 销毁现有图表
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }
        
        const chartData = {
            labels: data.map(item => item.month),
            datasets: [
                {
                    label: '收入',
                    data: data.map(item => item.income),
                    backgroundColor: this.colors.income,
                    borderColor: this.colors.income,
                    borderWidth: 1
                },
                {
                    label: '支出',
                    data: data.map(item => item.expense),
                    backgroundColor: this.colors.expense,
                    borderColor: this.colors.expense,
                    borderWidth: 1
                },
                {
                    label: '净收入',
                    data: data.map(item => item.net),
                    backgroundColor: this.colors.info,
                    borderColor: this.colors.info,
                    borderWidth: 1,
                    type: 'line',
                    fill: false,
                    tension: 0.4
                }
            ]
        };
        
        this.charts[containerId] = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '月度收支对比'
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '¥' + value.toFixed(2);
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
        
        return this.charts[containerId];
    }
    
    // 创建收支平衡图
    createBalanceChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;
        
        // 销毁现有图表
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }
        
        const chartData = {
            labels: ['收入', '支出'],
            datasets: [{
                data: [data.income, data.expense],
                backgroundColor: [this.colors.income, this.colors.expense],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        };
        
        this.charts[containerId] = new Chart(ctx, {
            type: 'pie',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '收支平衡图'
                    },
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ¥${value.toFixed(2)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
        
        return this.charts[containerId];
    }
    
    // 创建简单的统计卡片
    createStatCard(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const { title, value, change, changeType } = data;
        
        const changeClass = changeType === 'increase' ? 'text-success' : 
                           changeType === 'decrease' ? 'text-danger' : 'text-muted';
        
        const changeIcon = changeType === 'increase' ? '↗' : 
                          changeType === 'decrease' ? '↘' : '→';
        
        container.innerHTML = `
            <div class="stat-card">
                <h3>${title}</h3>
                <div class="stat-value">¥${value.toFixed(2)}</div>
                ${change !== undefined ? `
                    <div class="stat-change ${changeClass}">
                        ${changeIcon} ${Math.abs(change).toFixed(1)}%
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // 销毁所有图表
    destroyAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
        this.charts = {};
    }
    
    // 销毁特定图表
    destroyChart(containerId) {
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
            delete this.charts[containerId];
        }
    }
    
    // 更新图表数据
    updateChart(containerId, newData) {
        const chart = this.charts[containerId];
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }
    
    // 导出图表为图片
    exportChart(containerId, filename = 'chart.png') {
        const chart = this.charts[containerId];
        if (chart) {
            const url = chart.toBase64Image();
            const link = document.createElement('a');
            link.download = filename;
            link.href = url;
            link.click();
        }
    }
}

// 全局图表管理器实例
window.chartsManager = new ChartsManager();

