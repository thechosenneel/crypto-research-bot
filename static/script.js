const input = document.getElementById('searchInput');
const suggestions = document.getElementById('suggestions');

input.addEventListener('input', async () => {
    const query = input.value.trim();
    if (!query) {
        suggestions.innerHTML = '';
        return;
    }

    try {
        const res = await axios.get(`/search?q=${query}`);
        suggestions.innerHTML = '';
        res.data.forEach(coin => {
            const div = document.createElement('div');
            div.classList.add('suggestion');
            div.innerHTML = `<img src="${coin.thumb}" width="20"> ${coin.name} (${coin.symbol.toUpperCase()})`;
            div.onclick = () => {
                window.location.href = `/coin/${coin.id}`;
            };
            suggestions.appendChild(div);
        });
    } catch (err) {
        console.error('Search failed:', err);
    }
});
