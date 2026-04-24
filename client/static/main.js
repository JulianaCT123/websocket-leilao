import { 
  showScreen, setupRoleUI, updateAuctionItem, updateHighestBid, 
  updateTimer, renderPlayersList, renderWinners, showError, setRoomLinkAndQRCode 
} from "./ui.js";
import { createSocket } from "./ws.js";

let socket = null;
let currentRoom = null;
let isHost = false;
let myName = null;

function getRoomFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get("sala");
}

function handleServerMessage(data) {
  if (data.type === "init") {

    setupRoleUI(data.role);
    
    if (data.role === "client") {
      showScreen("screen-waiting");
      
      const clientControls = document.getElementById("client-controls");
      clientControls.classList.remove("flex");
      clientControls.classList.add("hidden");
    }
  } 
  else if (data.type === "update") {
    const state = data.state;
    
    renderPlayersList(state.players);

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

async function createRoom() {
  try {
    const response = await fetch("/api/create-room");
    const data = await response.json();
    
    window.location.href = `/?sala=${data.room_id}&isHost=true`;
  } catch (error) {
    showError("Falha ao criar sala.");
  }
}

function connect(roomId, hostMode, playerName) {
  currentRoom = roomId;
  isHost = hostMode;
  myName = playerName;

  if (playerName) {
    localStorage.setItem(`leilao_nome_${roomId}`, playerName);
  }
  if (hostMode) {
    localStorage.setItem(`leilao_host_${roomId}`, "true");
  }

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

document.addEventListener("DOMContentLoaded", () => {
  const roomId = getRoomFromUrl();
  const params = new URLSearchParams(window.location.search);
  const hostParam = params.get("isHost") === "true";

  document.getElementById("btn-create-room").addEventListener("click", createRoom);

  document.getElementById("btn-join").addEventListener("click", () => {
    const nameInput = document.getElementById("input-name");
    if (nameInput.value.trim()) {
      connect(roomId, false, nameInput.value.trim());
    } else {
      showError("Por favor, digite o seu nome.");
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
      bidInput.value = ""; 
    }
  });

  document.getElementById("btn-home").addEventListener("click", () => {
    window.location.href = "/";
  });

  if (roomId) {
    const savedName = localStorage.getItem(`leilao_nome_${roomId}`);
    const savedHost = localStorage.getItem(`leilao_host_${roomId}`) === "true";
    
    const amIHost = hostParam || savedHost;

    if (amIHost) {
      const fullLink = window.location.origin + "/?sala=" + roomId;
      setRoomLinkAndQRCode(fullLink);
      showScreen("screen-waiting");
      connect(roomId, true, null);
    } 
    else if (savedName) {
      showScreen("screen-waiting");
      setupRoleUI("client");
      connect(roomId, false, savedName);
    } 
    else {
      showScreen("screen-waiting");
      setupRoleUI("client");
    }
  } else {
    showScreen("screen-home");
  }
});