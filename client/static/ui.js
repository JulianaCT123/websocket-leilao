export function showScreen(screenId) {
  const screens = ["screen-home", "screen-waiting", "screen-auction", "screen-results"];
  
  screens.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.classList.add("hidden"); // Esconde
      if (id === "screen-waiting" || id === "screen-auction" || id === "screen-results") {
        el.classList.remove("flex"); 
      }
    }
  });

  const target = document.getElementById(screenId);
  if (target) {
    target.classList.remove("hidden");
    if (screenId !== "screen-home") {
      target.classList.add("flex"); 
    }
  }
}


export function setupRoleUI(role) {
  const hostControls = document.getElementById("host-controls");
  const clientControls = document.getElementById("client-controls");
  const bidControls = document.getElementById("bid-controls");
  const btnHome = document.getElementById("btn-home");

  if (role === "host") {
    hostControls.classList.remove("hidden");
    hostControls.classList.add("flex");
    clientControls.classList.add("hidden");
    bidControls.classList.add("hidden"); 
    btnHome.classList.remove("hidden"); 
  } else {
    hostControls.classList.add("hidden");
    clientControls.classList.remove("hidden");
    clientControls.classList.add("flex");
    bidControls.classList.remove("hidden");
    bidControls.classList.add("flex"); 
    btnHome.classList.add("hidden");
  }
}


export function updateAuctionItem(item) {
  if (!item) return;
  document.getElementById("item-image").src = item.image_url;
  document.getElementById("item-name").textContent = item.name;
  document.getElementById("item-initial-bid").textContent = item.initial_bid.toFixed(2);
}

export function updateHighestBid(amount, bidderName) {
  document.getElementById("current-highest-bid").textContent = amount.toFixed(2);
  document.getElementById("current-bidder").textContent = bidderName || "Ninguém";
}

export function updateTimer(seconds) {
  document.getElementById("timer").textContent = seconds;
}

export function renderPlayersList(players) {
  const container = document.getElementById("players-list");
  container.innerHTML = ""; 

  if (players.length === 0) {
    container.innerHTML = '<span class="text-slate-500 italic">Ninguém entrou ainda.</span>';
    return;
  }

  players.forEach(name => {
    const badge = document.createElement("span");
    badge.className = "px-3 py-1 bg-slate-700 rounded-full text-sm font-semibold";
    badge.textContent = name;
    container.appendChild(badge);
  });
}

export function renderWinners(winners) {
  const container = document.getElementById("winners-list");
  container.innerHTML = "";

  if (winners.length === 0) {
    container.innerHTML = '<p class="text-center text-slate-400">Nenhum item foi arrematado.</p>';
    return;
  }

  winners.forEach(w => {
    const div = document.createElement("div");
    // Mudamos para flex-col no celular e flex-row no computador, adicionando um gap (espaço)
    div.className = "p-4 bg-slate-800 rounded-xl border border-slate-700 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3";
    
    div.innerHTML = `
      <div class="w-full sm:w-auto">
        <p class="text-sm text-slate-400">Lote ${w.auction_number}: ${w.item_name}</p>
        <p class="text-xl font-bold text-emerald-400 break-all">${w.winner_name}</p>
      </div>
      <div class="text-2xl font-bold break-all w-full sm:w-auto sm:text-right text-emerald-100">
        R$ ${w.amount.toFixed(2)}
      </div>
    `;
    container.appendChild(div);
  });
}


export function showError(message) {
  const alertBox = document.getElementById("alert-box");
  alertBox.textContent = message;
  alertBox.classList.remove("hidden");

  setTimeout(() => {
    alertBox.classList.add("hidden");
  }, 4000);
}

export function setRoomLinkAndQRCode(link) {
  const linkEl = document.getElementById("room-link");
  linkEl.href = link;
  linkEl.textContent = link;

  const qrContainer = document.getElementById("qrcode");
  qrContainer.innerHTML = "";
  new QRCode(qrContainer, {
    text: link,
    width: 150,
    height: 150,
    colorDark: "#020617", 
    colorLight: "#ffffff",
  });
}