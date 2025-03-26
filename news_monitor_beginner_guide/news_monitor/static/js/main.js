// 主要JavaScript功能
document.addEventListener('DOMContentLoaded', function() {
    // 初始化提示框
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // 初始化图表（如果页面上有图表容器）
    initCharts();
});

// 初始化图表
function initCharts() {
    // 趋势图表
    const trendChartEl = document.getElementById('trendChart');
    if (trendChartEl) {
        const ctx = trendChartEl.getContext('2d');
        const trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: trendChartData.dates,
                datasets: [{
                    label: '新闻数量',
                    data: trendChartData.counts,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: '新闻趋势'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // 情感分析图表
    const sentimentChartEl = document.getElementById('sentimentChart');
    if (sentimentChartEl) {
        const ctx = sentimentChartEl.getContext('2d');
        const sentimentChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['正面', '中性', '负面'],
                datasets: [{
                    data: [
                        sentimentData.positive || 0,
                        sentimentData.neutral || 0,
                        sentimentData.negative || 0
                    ],
                    backgroundColor: [
                        '#28a745',
                        '#6c757d',
                        '#dc3545'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    title: {
                        display: true,
                        text: '情感分析'
                    }
                }
            }
        });
    }

    // 平台分布图表
    const platformChartEl = document.getElementById('platformChart');
    if (platformChartEl) {
        const ctx = platformChartEl.getContext('2d');
        const platformChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: platformData.labels,
                datasets: [{
                    data: platformData.values,
                    backgroundColor: [
                        '#007bff',
                        '#fd7e14',
                        '#20c997',
                        '#dc3545'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    title: {
                        display: true,
                        text: '平台分布'
                    }
                }
            }
        });
    }

    // 互动数据图表
    const interactionChartEl = document.getElementById('interactionChart');
    if (interactionChartEl) {
        const ctx = interactionChartEl.getContext('2d');
        const interactionChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: interactionData.labels,
                datasets: [{
                    label: '互动数据',
                    data: interactionData.values,
                    backgroundColor: [
                        '#007bff',
                        '#28a745',
                        '#fd7e14',
                        '#dc3545',
                        '#6f42c1'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: '互动数据'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// 关键词管理相关函数
function addKeyword() {
    const keywordInput = document.getElementById('newKeyword');
    const categoryInput = document.getElementById('keywordCategory');
    
    if (!keywordInput.value.trim()) {
        alert('请输入关键词');
        return;
    }
    
    // 提交表单
    document.getElementById('addKeywordForm').submit();
}

function deleteKeyword(keywordId) {
    if (confirm('确定要删除这个关键词吗？')) {
        document.getElementById(`deleteKeywordForm_${keywordId}`).submit();
    }
}

// 平台管理相关函数
function addPlatform() {
    const platformNameInput = document.getElementById('platformName');
    const platformTypeInput = document.getElementById('platformType');
    
    if (!platformNameInput.value.trim()) {
        alert('请输入平台名称');
        return;
    }
    
    // 提交表单
    document.getElementById('addPlatformForm').submit();
}

function deletePlatform(platformId) {
    if (confirm('确定要删除这个平台吗？')) {
        document.getElementById(`deletePlatformForm_${platformId}`).submit();
    }
}

// 新闻抓取相关函数
function startCrawling() {
    // 检查是否选择了关键词和平台
    const keywordSelect = document.getElementById('keywordSelect');
    const platformChecks = document.querySelectorAll('input[name="platforms"]:checked');
    
    if (keywordSelect.value === '') {
        alert('请选择关键词');
        return;
    }
    
    if (platformChecks.length === 0) {
        alert('请至少选择一个平台');
        return;
    }
    
    // 显示加载提示
    document.getElementById('loadingIndicator').style.display = 'block';
    
    // 提交表单
    document.getElementById('crawlForm').submit();
}

// 日期范围选择器初始化
function initDateRangePicker() {
    const dateRangeEl = document.getElementById('dateRange');
    if (dateRangeEl) {
        // 这里可以添加日期选择器的初始化代码
        // 由于我们使用的是简单的HTML日期选择器，这里不需要特殊初始化
    }
}
