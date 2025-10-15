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
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 to-gray-700 text-white p-4">
      {/* Título */}
      <h1 className="flex items-center gap-2 text-3xl md:text-4xl font-bold mb-6">
        <AiFillAliwangwang size={40} />
        7social
      </h1>

      {/* Contenedor principal responsive */}
      <div className="flex flex-col md:flex-row w-full max-w-5xl bg-gray-800 rounded-2xl shadow-lg overflow-hidden">
        {/* Carrete de imágenes */}
        <div className="w-full md:w-1/2 relative">
          <div className="flex overflow-x-auto snap-x snap-mandatory scrollbar-hide">
            {["/images/social-1.jpg", "/images/social-2.jpg", "/images/social-3.png", "/images/social-4.png"].map(
              (src, i) => (
                <img
                  key={i}
                  src={src}
                  alt={`Imagen ${i + 1}`}
                  className="w-full h-64 md:h-full object-cover snap-center"
                />
              )
            )}
          </div>
        </div>

        {/* Panel de login / registro */}
        <div className="w-full md:w-1/2 p-6 md:p-10 flex flex-col justify-center bg-gray-900">
          {loading && <div className="text-center mb-4 animate-pulse">Cargando...</div>}

          {isRegistering ? (
            <>
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <FaRegIdCard /> Registrarse
              </h2>
              <form onSubmit={handleLoginSubmit} className="flex flex-col gap-3">
                <input
                  type="text"
                  id="register-name"
                  placeholder="Nombre"
                  className="p-2 rounded bg-gray-700 focus:ring-2 focus:ring-indigo-400"
                />
                <input
                  type="text"
                  id="register-username"
                  placeholder="Usuario"
                  className="p-2 rounded bg-gray-700 focus:ring-2 focus:ring-indigo-400"
                />
                <input
                  type="email"
                  id="register-email"
                  placeholder="Correo"
                  className="p-2 rounded bg-gray-700 focus:ring-2 focus:ring-indigo-400"
                />
                <input
                  type="text"
                  id="register-age"
                  placeholder={age ? `${age} años` : "Edad"}
                  readOnly
                  onClick={() => hiddenDateRef.current.showPicker()}
                  className="p-2 rounded bg-gray-700 focus:ring-2 focus:ring-indigo-400"
                />
                <input
                  type="date"
                  ref={hiddenDateRef}
                  className="hidden"
                  onChange={handleDateChange}
                />
                <div className="relative">
                  <input
                    type={showRegisterPassword ? "text" : "password"}
                    id="register-password"
                    placeholder="Contraseña"
                    className="p-2 rounded bg-gray-700 focus:ring-2 focus:ring-indigo-400 w-full"
                  />
                  <span
                    onClick={() => setShowRegisterPassword(!showRegisterPassword)}
                    className="absolute right-3 top-2 cursor-pointer"
                  >
                    {showRegisterPassword ? "🙈" : "👁️"}
                  </span>
                </div>
                <button type="submit" className="bg-indigo-600 hover:bg-indigo-700 p-2 rounded mt-2">
                  <FaPaperPlane className="inline-block mr-2" /> Registrarse
                </button>
                <button
                  type="button"
                  onClick={() => setIsRegistering(false)}
                  className="bg-gray-600 hover:bg-gray-700 p-2 rounded mt-2"
                >
                  <FaMeteor className="inline-block mr-2" /> Volver a Iniciar Sesión
                </button>
              </form>
            </>
          ) : (
            <>
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <FaMeteor /> Iniciar Sesión
              </h2>
              <form onSubmit={handleLoginSubmit} className="flex flex-col gap-3">
                <input
                  type="text"
                  id="username"
                  placeholder="Usuario"
                  className="p-2 rounded bg-gray-700 focus:ring-2 focus:ring-indigo-400"
                />
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    id="password"
                    placeholder="Contraseña"
                    className="p-2 rounded bg-gray-700 focus:ring-2 focus:ring-indigo-400 w-full"
                  />
                  <span
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-2 cursor-pointer"
                  >
                    {showPassword ? "🙈" : "👁️"}
                  </span>
                </div>
                <button type="submit" className="bg-indigo-600 hover:bg-indigo-700 p-2 rounded mt-2">
                  <FaPaperPlane className="inline-block mr-2" /> Iniciar Sesión
                </button>
                <button
                  type="button"
                  onClick={() => setIsRegistering(true)}
                  className="bg-gray-600 hover:bg-gray-700 p-2 rounded mt-2"
                >
                  <FaRegIdCard className="inline-block mr-2" /> Registrarme
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;
