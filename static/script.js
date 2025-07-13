// Add this at the top of the file
const API_STATUS = document.querySelector('.badge');

// Update the loadCoinDetails function
async function loadCoinDetails(coinId) {
    try {
        showLoader(true);
        const response = await fetch(`/coin/${coinId}`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // ... existing code ...
        
    } catch (error) {
        showNotification(`Error loading coin data: ${error.message}`, 'danger');
    } finally {
        showLoader(false);
    }
}

// Add helper functions
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    notification.style.zIndex = '2000';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function showLoader(show) {
    const loader = document.getElementById('loader');
    if (!loader && show) {
        const loaderDiv = document.createElement('div');
        loaderDiv.id = 'loader';
        loaderDiv.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
        loaderDiv.style.background = 'rgba(0,0,0,0.5)';
        loaderDiv.style.zIndex = '2000';
        loaderDiv.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        document.body.appendChild(loaderDiv);
    } else if (loader && !show) {
        loader.remove();
    }
}

// Add this to the searchCoins function
async function searchCoins(query) {
    if (query.length < 2) {
        suggestionList.style.display = 'none';
        return;
    }
    
    try {
        // Show API status warning if public
        if (API_STATUS.classList.contains('bg-warning')) {
            showNotification('Using public API - searches limited to 10-30/min', 'warning');
        }
        
        // ... existing code ...
    } catch (error) {
        showNotification(`Search error: ${error.message}`, 'danger');
    }
}
