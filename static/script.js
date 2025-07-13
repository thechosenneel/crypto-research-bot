// static/script.js
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const suggestionList = document.getElementById('suggestion-list');
    const coinDetails = document.getElementById('coin-details');
    const searchButton = document.getElementById('search-button');
    let sparklineChart = null;
    let currentSuggestions = [];
    
    // ... (existing helper functions remain the same) ...
    
    // Highlight matching text in suggestions
    function highlightMatch(text, query) {
        if (!query) return text;
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<span class="suggestion-highlight">$1</span>');
    }
    
    // Show suggestions
    function showSuggestions(suggestions, query) {
        if (suggestions.length === 0 || !query) {
            suggestionList.style.display = 'none';
            return;
        }
        
        suggestionList.innerHTML = suggestions.map(coin => `
            <div class="suggestion-item" data-id="${coin.id}">
                ${highlightMatch(coin.name, query)}
                <span class="suggestion-symbol">${coin.symbol.toUpperCase()}</span>
            </div>
        `).join('');
        
        suggestionList.style.display = 'block';
        currentSuggestions = suggestions;
        
        // Add click event listeners to suggestions
        document.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                loadCoinDetails(item.dataset.id);
                searchInput.value = '';
                suggestionList.style.display = 'none';
            });
        });
    }
    
    // Search coins
    const searchCoins = debounce(async function(query) {
        if (query.length < 2) {
            suggestionList.style.display = 'none';
            return;
        }
        
        try {
            const response = await fetch(`/search?query=${encodeURIComponent(query)}`);
            const results = await response.json();
            
            if (results.error) {
                throw new Error(results.error);
            }
            
            showSuggestions(results, query);
        } catch (error) {
            suggestionList.innerHTML = `<div class="suggestion-item p-3 text-danger">Error: ${error.message}</div>`;
            suggestionList.style.display = 'block';
        }
    }, 300);
    
    // ... (loadCoinDetails remains the same) ...
    
    // Event listeners
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        searchCoins(query);
    });
    
    searchInput.addEventListener('focus', function() {
        if (this.value.trim().length >= 2 && currentSuggestions.length > 0) {
            suggestionList.style.display = 'block';
        }
    });
    
    searchInput.addEventListener('keydown', function(e) {
        // Arrow down to select first suggestion
        if (e.key === 'ArrowDown' && suggestionList.style.display === 'block') {
            const firstItem = suggestionList.querySelector('.suggestion-item');
            if (firstItem) firstItem.focus();
        }
        
        // Enter to search
        if (e.key === 'Enter') {
            if (currentSuggestions.length > 0) {
                loadCoinDetails(currentSuggestions[0].id);
            }
        }
    });
    
    // Close suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!suggestionList.contains(e.target) && 
            e.target !== searchInput && 
            e.target !== searchButton) {
            suggestionList.style.display = 'none';
        }
    });
    
    // Search button click
    searchButton.addEventListener('click', function() {
        if (currentSuggestions.length > 0) {
            loadCoinDetails(currentSuggestions[0].id);
        }
    });
    
    // Keyboard navigation for suggestions
    suggestionList.addEventListener('keydown', function(e) {
        const items = this.querySelectorAll('.suggestion-item');
        const currentItem = document.activeElement;
        const currentIndex = Array.from(items).indexOf(currentItem);
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            const nextIndex = (currentIndex + 1) % items.length;
            items[nextIndex].focus();
        }
        
        if (e.key === 'ArrowUp') {
            e.preventDefault();
            const prevIndex = (currentIndex - 1 + items.length) % items.length;
            if (prevIndex === items.length - 1) {
                searchInput.focus();
            } else {
                items[prevIndex].focus();
            }
        }
        
        if (e.key === 'Enter' && currentItem) {
            currentItem.click();
        }
        
        if (e.key === 'Escape') {
            suggestionList.style.display = 'none';
            searchInput.focus();
        }
    });
});
