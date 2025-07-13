// static/script.js
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const coinDetails = document.getElementById('coin-details');
    let sparklineChart = null;
    
    // Debounce function to limit API calls
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
    
    // Format currency
    function formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            maximumFractionDigits: value < 1 ? 4 : 2
        }).format(value);
    }
    
    // Format large numbers
    function formatNumber(num) {
        if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
        if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
        if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
        return num.toFixed(2);
    }
    
    // Format percentage
    function formatPercent(value) {
        return value ? value.toFixed(2) + '%' : 'N/A';
    }
    
    // Search coins
    const searchCoins = debounce(async function(query) {
        if (query.length < 2) {
            searchResults.style.display = 'none';
            return;
        }
        
        try {
            const response = await fetch(`/search?query=${encodeURIComponent(query)}`);
            const results = await response.json();
            
            if (results.error) {
                throw new Error(results.error);
            }
            
            if (results.length === 0) {
                searchResults.innerHTML = '<div class="search-item p-3">No coins found</div>';
                searchResults.style.display = 'block';
                return;
            }
            
            searchResults.innerHTML = results.map(coin => `
                <div class="search-item" data-id="${coin.id}">
                    ${coin.label}
                </div>
            `).join('');
            
            searchResults.style.display = 'block';
            
            // Add click event listeners
            document.querySelectorAll('.search-item').forEach(item => {
                item.addEventListener('click', () => {
                    loadCoinDetails(item.dataset.id);
                    searchInput.value = '';
                    searchResults.style.display = 'none';
                });
            });
        } catch (error) {
            searchResults.innerHTML = `<div class="search-item p-3 text-danger">Error: ${error.message}</div>`;
            searchResults.style.display = 'block';
        }
    }, 300);
    
    // Load coin details
    async function loadCoinDetails(coinId) {
        try {
            const response = await fetch(`/coin/${coinId}`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Update DOM elements
            document.getElementById('coin-name').textContent = data.name;
            document.getElementById('coin-symbol').textContent = data.symbol;
            document.getElementById('current-price').textContent = formatCurrency(data.current_price);
            document.getElementById('market-cap').textContent = formatNumber(data.market_cap);
            document.getElementById('volume-24h').textContent = formatNumber(data.volume_24h);
            document.getElementById('market-cap-rank').textContent = '#' + data.market_cap_rank;
            document.getElementById('volume-mc-ratio').textContent = formatPercent(data.volume_mc_ratio);
            document.getElementById('ath-gap').textContent = formatPercent(data.ath_gap);
            document.getElementById('circulating-percent').textContent = formatPercent(data.circulating_percent);
            
            // Handle price changes
            const priceChange24h = document.getElementById('price-change-24h');
            priceChange24h.textContent = formatPercent(data.price_change_24h);
            priceChange24h.className = 'metric-value ' + 
                (data.price_change_24h >= 0 ? 'positive' : 'negative');
            
            const priceChange7d = document.getElementById('price-change-7d');
            priceChange7d.textContent = formatPercent(data.price_change_7d);
            priceChange7d.className = 'metric-value ' + 
                (data.price_change_7d >= 0 ? 'positive' : 'negative');
            
            // Create sparkline chart
            if (sparklineChart) {
                sparklineChart.destroy();
            }
            
            const ctx = document.getElementById('sparkline-chart').getContext('2d');
            sparklineChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: Array(data.sparkline.length).fill(''),
                    datasets: [{
                        data: data.sparkline,
                        borderColor: '#6f42c1',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: false,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            enabled: true,
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    return formatCurrency(context.parsed.y);
                                }
                            }
                        }
                    },
                    scales: {
                        x: { display: false },
                        y: { display: false }
                    }
                }
            });
            
            // Show coin details section
            coinDetails.style.display = 'block';
            
            // Scroll to results
            coinDetails.scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            alert(`Error loading coin data: ${error.message}`);
        }
    }
    
    // Event listeners
    searchInput.addEventListener('input', function() {
        searchCoins(this.value.trim());
    });
    
    // Close search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchResults.contains(e.target) {
            searchResults.style.display = 'none';
        }
    });
});
