import React from "react";
import { AiFillAliwangwang  } from "react-icons/ai";
import { IoIosHome,IoIosPerson,IoIosRocket} from "react-icons/io";
import { FaRegTimesCircle } from "react-icons/fa";
import "./Navbar.css";
import { useAuth } from "../context/AuthContext";
import { toast } from 'react-toastify';

const logoutFunction = () => {
  // Aquí podrías eliminar datos de la sesión, por ejemplo:
  localStorage.removeItem("userToken"); // Elimina un token de autenticación si lo usas
  toast.success("Has cerrado sesión exitosamente.");
  setTimeout(() => {
  window.location.href = "/"; // Redirige al inicio
  }, 1500);
};

const Navbar = () => {
  const { isAuthenticated, logout } = useAuth();

  if (!isAuthenticated) {
    return null; // No muestra el Navbar si no está autenticado
  }
  
  return (
    <nav className="navbar">
      <div className="navbar-logo"><AiFillAliwangwang size={35}/> 7Social</div>
      <ul className="navbar-links">
        <li><a href="/"><IoIosHome size={22}/> Inicio</a></li>
        <li><a href="/feed"><IoIosRocket size={22}/> Feed</a></li>
        <li><a href="/profile"><IoIosPerson size={22}/> Perfil</a></li>
        <li><a onClick={logoutFunction}><FaRegTimesCircle size={22}/> Cerrar Sesión</a></li>
      </ul>
    </nav>
  );
};

export default Navbar;