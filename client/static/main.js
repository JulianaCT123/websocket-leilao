// main.js
import { 
  showScreen, setupRoleUI, updateAuctionItem, updateHighestBid, 
  updateTimer, renderPlayersList, renderWinners, showError, setRoomLinkAndQRCode 
} from "./ui.js";
import { createSocket } from "./ws.js";

// Variáveis de estado global do cliente
let socket = null;
let currentRoom = null;
let isHost = false;
let myName = null;

// --- FUNÇÕES DE APOIO ---

function getRoomFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get("sala");
}

function handleServerMessage(data) {
  if (data.type === "init") {
    // O servidor confirmou a entrada
    setupRoleUI(data.role);
    if (data.role === "client") {
      showScreen("screen-waiting");
    }
  } 
  else if (data.type === "update") {
    const state = data.state;
    
    // Atualiza a lista de jogadores no lobby
    renderPlayersList(state.players);

    // Troca de ecrã conforme o status do leilão no Python
    if (state.status === "waiting") {
      showScreen("screen-waiting");
    } 
    else if (state.status === "running") {
      showScreen("screen-auction");
      updateAuctionItem(state.current_item);
      updateHighestBid(state.highest_bid, state.highest_bidder);
      updateTimer(state.time_remaining);
    } 
    else if (state.status === "finished") {
      showScreen("screen-results");
      renderWinners(state.winners);
    }
  } 
  else if (data.type === "error") {
    showError(data.message);
  }
}

// --- AÇÕES DO UTILIZADOR ---

async function createRoom() {
  try {
    const response = await fetch("/api/create-room");
    const data = await response.json();
    
    // Ao criar, recarregamos a página com ?sala=ID e um aviso que somos o Host
    window.location.href = `/?sala=${data.room_id}&isHost=true`;
  } catch (error) {
    showError("Falha ao criar sala.");
  }
}

function connect(roomId, hostMode, playerName) {
  currentRoom = roomId;
  isHost = hostMode;
  myName = playerName;

  socket = createSocket(
    roomId, 
    isHost, 
    myName,
    (data) => handleServerMessage(data),
    () => console.log("Conectado ao servidor!"),
    () => console.log("Conexão fechada."),
    () => showError("Erro na ligação ao servidor.")
  );
}

// --- INICIALIZAÇÃO ---

document.addEventListener("DOMContentLoaded", () => {
  const roomId = getRoomFromUrl();
  const params = new URLSearchParams(window.location.search);
  const hostParam = params.get("isHost") === "true";

  // 1. Configuração de Botões
  document.getElementById("btn-create-room").addEventListener("click", createRoom);

  document.getElementById("btn-join").addEventListener("click", () => {
    const nameInput = document.getElementById("input-name");
    if (nameInput.value.trim()) {
      connect(roomId, false, nameInput.value.trim());
    } else {
      showError("Por favor, introduz o teu nome.");
    }
  });

  document.getElementById("btn-start-auction").addEventListener("click", () => {
    if (socket) socket.send(JSON.stringify({ action: "start_auction" }));
  });

  document.getElementById("btn-bid").addEventListener("click", () => {
    const bidInput = document.getElementById("input-bid");
    const amount = parseFloat(bidInput.value);
    if (amount > 0) {
      socket.send(JSON.stringify({ action: "bid", amount: amount }));
      bidInput.value = ""; // Limpa o campo após dar o lance
    }
  });

  document.getElementById("btn-home").addEventListener("click", () => {
    window.location.href = "/";
  });

  // 2. Lógica de entrada automática
  if (roomId) {
    if (hostParam) {
      // Se sou o Host, conecto-me logo e gero o QR Code
      const fullLink = window.location.origin + "/?sala=" + roomId;
      setRoomLinkAndQRCode(fullLink);
      showScreen("screen-waiting");
      connect(roomId, true, null);
    } else {
      // Se sou Cliente, mostro a tela para pôr o nome
      showScreen("screen-waiting");
      setupRoleUI("client");
    }
  } else {
    showScreen("screen-home");
  }
});