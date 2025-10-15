import React, { useState , useRef } from "react";
import { FaMeteor, FaPaperPlane, FaRegIdCard, FaUserFriends, FaKey, FaEnvelope, FaUserAlt, FaBirthdayCake } from "react-icons/fa";
import "./Home.css";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { toast } from 'react-toastify';
import { AiFillAliwangwang  } from "react-icons/ai";

const Home = () => {
  const [isRegistering, setIsRegistering] = useState(false); // Estado para alternar entre login y registro
  const [loading, setLoading] = useState(false); // Estado para mostrar indicador de carga
  const { login } = useAuth();
  const [age, setAge] = useState("");
  const hiddenDateRef = useRef(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showRegisterPassword, setShowRegisterPassword] = useState(false);

  const handleDateChange = (e) => {
    const selectedDate = new Date(e.target.value);

    // calcular edad
    const today = new Date();
    let years = today.getFullYear() - selectedDate.getFullYear();
    const m = today.getMonth() - selectedDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < selectedDate.getDate())) {
      years--;
    }
    setAge(years);
  };
  
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const loginData = {
      username: document.getElementById("username").value,
      password: document.getElementById("password").value,
    };

    try {
      const response = await api.post("/login", loginData);
      login(response.data.token);
      localStorage.setItem("userData", JSON.stringify(response.data.user));
      toast.success("Inicio de sesión exitoso");
      
      const userData = JSON.parse(localStorage.getItem("userData"));
      const userId = userData?.id;  // Obtener el 'id' del usuario
      const username = userData?.username;
      localStorage.setItem("user_id", userId);
      localStorage.setItem("username", username);
      
      setTimeout(() => {
        window.location.href = "/feed"; // Redirige al feed
      },1500);   
    } catch (error) {
      console.error("Error al iniciar sesión:", error.response?.data);
      toast.error(error.response?.data?.detail || "Credenciales inválidas.");
    } finally {
      setLoading(false); // Desactiva el indicador de carga
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const userData = {
      name: document.getElementById("register-name").value,
      username: document.getElementById("register-username").value,
      email: document.getElementById("register-email").value,
      age: parseInt(document.getElementById("register-age").value, 10),
      password: document.getElementById("register-password").value,
    };

    console.log("Datos enviados al backend:", userData); // Imprime los datos enviados

    try {
      const response = await api.post("/register", userData);
      console.log("Respuesta del servidor:", response.data);
      toast.success("Usuario registrado exitosamente");
      setIsRegistering(false); // Regresa al inicio de sesión
    } catch (error) {
      toast.error("Error al registrar el usuario:", error.response?.data || error);
      alert(error.response?.data?.detail || "Hubo un error al registrar el usuario.");
    } finally {
      setLoading(false);
    }
  };

  return (
  <>  
    <div className="titulo-home">
      <h1><AiFillAliwangwang size={40}/>7social</h1>
      </div>
    <div className="home-container">
      {/* Carrete de imágenes */}
      <div className="carousel">
        <div className="carousel-track">
          <img src="/images/social-1.jpg" alt="Imagen 1" className="carousel-image" />
          <img src="/images/social-2.jpg" alt="Imagen 2" className="carousel-image" />
          <img src="/images/social-3.png" alt="Imagen 3" className="carousel-image" />
          <img src="/images/social-4.png" alt="Imagen 4" className="carousel-image" />
        
          <img src="/images/social-1.jpg" alt="Imagen 1" className="carousel-image" />
          <img src="/images/social-2.jpg" alt="Imagen 2" className="carousel-image" />
          <img src="/images/social-3.png" alt="Imagen 3" className="carousel-image" />
          <img src="/images/social-4.png" alt="Imagen 4" className="carousel-image" />
        
        </div>
      </div>
      {/* Barra de inicio de sesión o registro */}
      <div className="login-bar">
        {loading && <div className="loading-spinner">Cargando...</div>} {/* Indicador de carga */}
        {isRegistering ? (
          <>
            <h2><FaRegIdCard /> Registrarse</h2>
            <form onSubmit={handleRegisterSubmit}>
              <div className="form-group">
                <label htmlFor="name"><FaUserAlt /> Nombre</label>
                <input type="text" id="register-name" placeholder="Ingresa tu nombre" />
              </div>
              <div className="form-group">
                <label htmlFor="username"><FaUserFriends /> Usuario</label>
                <input type="text" id="register-username" placeholder="Ingresa tu usuario" />
              </div>
              <div className="form-group">
                <label htmlFor="email"><FaEnvelope /> Correo Electrónico</label>
                <input type="email" id="register-email" placeholder="Ingresa tu correo" />
              </div>
              <div className="form-group">
                <label htmlFor="age"><FaBirthdayCake /> Edad</label>
                <input type="text" id="register-age" placeholder="Selecciona fecha" value={age ?`${age} años` : ""}
                readOnly onClick={() => hiddenDateRef.current.showPicker()}
                />
                <input type="date" ref={hiddenDateRef} style={{ position: "absolute", opacity: 0, pointerEvents: "none"  }} onChange={handleDateChange}
              />
              </div>
              <div className="form-group">
                <label htmlFor="password"><FaKey /> Contraseña</label>
                <input type={showRegisterPassword ? "text" : "password"} id="register-password" placeholder="Ingresa tu contraseña" />
                <span className="toggle-eye1" onClick={ ()=> setShowRegisterPassword(!showRegisterPassword)}>{showRegisterPassword ? "🙈" : "👁️"}</span>
              </div>
              <button type="submit" className="login-button"><FaPaperPlane /> Registrarse</button>
              <button
                type="button"
                className="login-button"
                onClick={() => setIsRegistering(false)} // Volver al formulario de inicio de sesión
              >
                <FaMeteor /> Volver a Iniciar Sesión
              </button>
            </form>
          </>
        ) : (
          <>
            <h2><FaMeteor /> Iniciar Sesión</h2>
            <form onSubmit={handleLoginSubmit}>
              <div className="form-group">
                <label htmlFor="username"><FaUserFriends /> Usuario</label>
                <input type="text" id="username" placeholder="Ingresa tu usuario" />
              </div>
              <div className="form-group">
                <label htmlFor="password"><FaKey /> Contraseña</label>
                <input type={showPassword ? "text" : "password"} id="password" placeholder="Ingresa tu contraseña" />
                <span className="toggle-eye" onClick={ ()=> setShowPassword(!showPassword)}>{showPassword ? "🙈" : "👁️"}</span>
              </div>
              <button type="submit" className="login-button"><FaPaperPlane /> Iniciar Sesión</button>
              <button
                type="button"
                className="login-button"
                onClick={() => setIsRegistering(true)} // Cambiar al formulario de registro
              >
                <FaRegIdCard /> Registrarme
              </button> 
            </form>
          </>
        )}
      </div>
    </div>
</>
);
};

export default Home;
