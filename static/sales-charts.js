/**
 * Sales Charts JavaScript
 * Creates charts for the sales analytics page using Chart.js
 */

// Function to initialize sales charts
function initializeSalesCharts(chartData) {
    // Create weekly chart if data is available
    if (chartData.weeks && chartData.weeks.length > 0 && 
        chartData.weeklyValues && chartData.weeklyValues.length > 0) {
        createWeeklyChart(chartData.weeks, chartData.weeklyValues);
    }
    
    // Create monthly chart if data is available
    if (chartData.months && chartData.months.length > 0 && 
        chartData.monthlyValues && chartData.monthlyValues.length > 0) {
        createMonthlyChart(chartData.months, chartData.monthlyValues);
    }
}

// Create weekly sales bar chart
function createWeeklyChart(weeks, weeklyValues) {
    const weeklyCtx = document.getElementById('weeklyChart').getContext('2d');
    const weeklyChart = new Chart(weeklyCtx, {
        type: 'bar',
        data: {
            labels: weeks,
            datasets: [{
                label: 'Revenue ($)',
                data: weeklyValues,
                backgroundColor: 'rgba(141, 28, 61, 0.8)',
                borderColor: 'rgba(141, 28, 61, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            }
        }
    });
}

// Create monthly sales line chart
function createMonthlyChart(months, monthlyValues) {
    const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
    const monthlyChart = new Chart(monthlyCtx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Revenue ($)',
                data: monthlyValues,
                backgroundColor: 'rgba(60, 141, 47, 0.2)',
                borderColor: 'rgba(60, 141, 47, 1)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            }
        }
    });
}

// Initialize charts when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // The chartData variable will be defined in the HTML template
    if (typeof chartData !== 'undefined') {
        initializeSalesCharts(chartData);
    }
});