const searchInput = document.getElementById("coin-search");
const suggestions = document.getElementById("suggestions");

searchInput.addEventListener("input", async () => {
  const query = searchInput.value;
  if (query.length < 2) {
    suggestions.innerHTML = "";
    return;
  }

  const res = await fetch(`/search?q=${query}`);
  const data = await res.json();

  suggestions.innerHTML = data.map(coin => `
    <li class="list-group-item list-group-item-action" onclick="selectCoin('${coin.id}')">
      ${coin.name} (${coin.symbol.toUpperCase()})
    </li>
  `).join('');
});

function selectCoin(coinId) {
  window.location.href = `/coin/${coinId}`;
}
