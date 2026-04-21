// ws.js
export function createSocket(roomId, isHost, playerName, onMessage, onOpen, onClose, onError) {
  const url = new URL(`ws://${window.location.host}/ws`);
  
  // Adicionamos os parâmetros que o nosso handlers.py espera receber
  url.searchParams.set("sala", roomId);
  url.searchParams.set("host", isHost);
  if (playerName) {
    url.searchParams.set("nome", playerName);
  }

  const socket = new WebSocket(url.toString());

  socket.addEventListener("open", () => onOpen());
  socket.addEventListener("message", (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error("JSON inválido do servidor", error);
    }
  });
  
  socket.addEventListener("close", () => onClose());
  socket.addEventListener("error", (event) => onError(event));

  return socket;
}