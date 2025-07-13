document.addEventListener("DOMContentLoaded", () => {
    const search = document.getElementById("search");
    const suggestions = document.getElementById("suggestions");

    search.addEventListener("input", () => {
        const query = search.value;
        if (query.length < 2) {
            suggestions.innerHTML = "";
            return;
        }

        fetch(`/search?q=${query}`)
            .then(res => res.json())
            .then(data => {
                suggestions.innerHTML = "";
                data.forEach(coin => {
                    const div = document.createElement("div");
                    div.textContent = `${coin.name} (${coin.symbol.toUpperCase()})`;
                    div.onclick = () => {
                        window.location.href = `/coin/${coin.id}`;
                    };
                    suggestions.appendChild(div);
                });
            });
    });

    document.addEventListener("click", (e) => {
        if (!suggestions.contains(e.target)) {
            suggestions.innerHTML = "";
        }
    });
});
