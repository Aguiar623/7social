import React, { useState } from "react";
import "./ChatbotWidget.css";
import { toast } from 'react-toastify';

const ChatbotWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [userData, setUserData] = useState(null);
  const STREAMLIT_URL = "https://yeferson3256457-7chatbot.hf.space";

  const handleToggle = async () => {
    if (!isOpen) {
      // Obtener el user_id desde el localStorage
      const storeData = JSON.parse(localStorage.getItem("userData"));
      const userId = storeData ? storeData.id : null; // userData tenga el campo id

      if (!userId) {
        toast.error("Debes iniciar sesión para acceder al chatbot.");
        return;
      }

      try {
        const response = await fetch(`https://yeferson3256457-7social-back.hf.space/user/${userId}/posts_count`);
        if (response.ok) {
          const data = await response.json();
          if (data.count >= 3) {
            console.log("userData antes de abrir el iframe:", storeData);
            setUserData(storeData);
            setIsOpen(true); // Abrir el chatbot
          } else {
            toast.error("Debes escribir al menos 3 publicaciones para acceder al chatbot.");
          }
        } else {
          toast.error("Error al verificar el número de publicaciones.");
        }
      } catch (error) {
        console.error("Error al conectar con el backend:", error);
        toast.error("No se pudo conectar con el servidor.");
      }
    } else {
      setIsOpen(false); // Cierra si ya estaba abierto
    }
  };
  
  return (
    <div className="chatbot-container">
      {isOpen && userData && (
        <div className="chatbot-window">
          {/* Aquí pasamos el user_id como parámetro en la URL */}
          <iframe
            title="Chatbot"
            src={`${STREAMLIT_URL}/?user_id=${userData?.id}`} // Pasamos user_id aquí
            frameBorder="0"
            className="chatbot-iframe"
          />
        </div>
      )}
      <button className="chatbot-toggle" onClick={handleToggle}>
        {isOpen ? "✖️" : "💬"}
      </button>
    </div>
  );
};

export default ChatbotWidget;
