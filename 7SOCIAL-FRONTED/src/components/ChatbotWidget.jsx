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
     <div className="fixed bottom-6 right-6 flex flex-col items-end z-50">
      {isOpen && userData && (
        <div className="mb-2 bg-white rounded-xl shadow-xl overflow-hidden w-[350px] h-[500px] border border-gray-200">
          <iframe
            title="Chatbot"
            src={`${STREAMLIT_URL}/?user_id=${userData?.id}`}
            frameBorder="0"
            className="w-full h-full"
          />
        </div>
      )}
      <button
        onClick={handleToggle}
        className="bg-blue-600 text-white text-3xl p-3 rounded-full shadow-lg hover:bg-blue-700 transition"
      >
        {isOpen ? "✖️" : "💬"}
      </button>
    </div>
  );
};


export default ChatbotWidget;
