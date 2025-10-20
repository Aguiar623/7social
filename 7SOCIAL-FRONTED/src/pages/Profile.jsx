import React, { useEffect, useState } from "react";
import "./Profile.css";

const Profile = () => {
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("userData"));
    if (user) {
      setUserData(user);
      console.log("Datos del usuario desde localStorage:", user);
    } else {
      console.error("No se encontró información del usuario en localStorage.");
    }
  }, []);

  if (!userData) {
    return <div>Cargando datos del usuario...</div>;
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <img
          src="/images/default-avatar.jpg" // Imagen predeterminada
          alt="Avatar del usuario"
          className="profile-image"
        />
        <h2>{userData.name}</h2>
        <p>Id: {userData.id}</p>
        <p>Email: {userData.email}</p>
        <p>Edad: {userData.age}</p>
        <p>Username: {userData.username}</p>
      </div>
    </div>
  );
};

export default Profile;
