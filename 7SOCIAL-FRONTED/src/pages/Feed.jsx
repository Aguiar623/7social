import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import { useNavigate } from "react-router-dom";
import "./Feed.css";
import { FaEdit, FaHotjar, FaInbox, FaTrashAlt } from "react-icons/fa";
import { useAuth } from "../context/AuthContext";
import ChatbotWidget from '../components/ChatbotWidget';
import { toast } from 'react-toastify';
import Swal from 'sweetalert2';

export const Feed = () => {
  const [feedData, setFeedData] = useState([]); // Publicaciones existentes
  const [loading, setLoading] = useState(true); // Estado de carga
  const [newPost, setNewPost] = useState({ title: "", content: "" }); // Nueva publicación o edición
  const [editPost, setEditPost] = useState(null); // Publicación en edición
  const [userData, setUserData] = useState(null);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("userData"));
    if (!user && !isAuthenticated) {
      toast.error("Por favor, inicia sesión primero.");
      navigate("/");
    } else {
      setUserData(user);
    }
  }, [isAuthenticated, navigate]);
    
  // Cargar publicaciones al inicio
  useEffect(() => {
    fetchFeed();
  }, []);
  
  const fetchFeed = () => {
    api.get("/feed")
      .then((response) => {
        console.log("Datos recibidos:", response.data);
        setFeedData(response.data);
        setLoading(false);
      })
      .catch((error) => {
        toast.error("Error al obtener el feed:", error);
        setLoading(false);
      });
  };

  // Manejar envío de una nueva publicación o edición
  const handlePostSubmit = (e) => {
    e.preventDefault();
    if (!newPost.title.trim() || !newPost.content.trim()) {
      toast.error("El título y el contenido no pueden estar vacíos.");
      return;
    }
  
    const postData = {
      title: newPost.title,
      content: newPost.content,
      user_id: userData.id,
    };
  
    const userId = userData.id; // Obtener el ID del usuario actual
  
    if (editPost) {
      // Actualizar publicación existente
      api.put(`/feed/${editPost.id}`, postData, {
        params: { user_id: userId }  // Pasar el user_id como parámetro de consulta
      })
        .then((response) => {
          setFeedData(
            feedData.map((post) =>
              post.id === editPost.id ? response.data : post
            )
          );
          setEditPost(null); // Limpiar estado de edición
          setNewPost({ title: "", content: "" }); // Limpiar formulario
        })
        .catch((error) => {
          toast.error("No puedes editar publicaciones de otros usuarios", error);
        });
    } else {
      // Crear nueva publicación
      api.post("/feed", postData)
        .then((response) => {
          setFeedData([response.data, ...feedData]); // Agregar nueva publicación al feed
          setNewPost({ title: "", content: "" }); // Limpiar formulario
        })
        .catch((error) => {
          toast.error("Error al crear la publicación:", error);
        });
    }
  };

  // Manejar eliminación de una publicación
  const handleDelete = (postId) => {
    const userId = localStorage.getItem("user_id"); // Obtener el user_id del localStorage
  
    Swal.fire({
      title: '¿Estás Seguro?',
      text: 'Esta acción no se puede deshacer.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Eliminar',
      cancelButtonText: 'Cancelar',
    }).then((result) => {
      if (result.isConfirmed) {
        // Enviar la solicitud DELETE con el user_id en la URL
        api.delete(`/feed/${postId}?user_id=${userId}`)
          .then(() => {
            setFeedData(feedData.filter((post) => post.id !== postId)); // Actualizar el feed local
            Swal.fire('Eliminado', 'El Post ha sido Eliminado', 'success');
          })
          .catch((error) => {
            console.error("Error al eliminar la publicación:", error);
            Swal.fire('Error', 'No puedes eliminar Publicaciones de otros usuarios', 'error');
          });
      }
    });
  };
  
  // Manejar edición de una publicación
  const handleEdit = (post) => {
    setEditPost(post); // Establecer publicación en edición
    setNewPost({ title: post.title, content: post.content }); // Rellenar formulario con datos existentes
  };

  if (loading) {
    return <div>Cargando el feed...</div>;
  }

  return (
    <div className="feed-container">
      {/* Barra lateral del usuario */}
      <div className="sidebar">
        <div className="profile">
          <img
            src={"/images/default-avatar.jpg"}
            alt="Avatar"
            className="profile-image"
          />
          <h3>{userData?.name}</h3>
          <p>Edad: {userData?.age}</p>
        </div>
      </div>
  
      {/* Contenedor principal */}
      <div className="main-content">
        {/* Cuadro para crear o editar publicaciones */}
        <div className="create-post-box">
          <h2>
            <FaHotjar /> {editPost ? "Editar Publicación" : "Crear Publicación"}
          </h2>
          <form onSubmit={handlePostSubmit}>
            <input
              type="text"
              placeholder="Título de la publicación"
              value={newPost.title}
              onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
              className="post-input"
            />
            <textarea
              placeholder="Escribe lo que piensas hoy..."
              value={newPost.content}
              onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
              className="post-textarea"
            ></textarea>
            <button type="submit" className="post-button">
              {editPost ? (
                <>
                  <FaEdit /> Guardar Cambios
                </>
              ) : (
                <>
                  <FaEdit /> Publicar
                </>
              )}
            </button>
          </form>
        </div>
  
        {/* Lista de publicaciones */}
        <div className="feed-posts">
          <h1 className="feed-header">
            <FaInbox /> Feed
          </h1>
          {feedData.length === 0 ? (
            <p>No hay publicaciones disponibles.</p>
          ) : (
            feedData.map((post) => (
              <div key={post.id} className="post">
                <h2>{post.title}</h2>
                <p>{post.content}</p>
                <p className="post-user">Publicado por: {post.username}</p> {/* Mostrar el usuario */}
                <div className="post-actions">
                  <button className="edit-button" onClick={() => handleEdit(post)}>
                    <FaEdit /> Editar
                  </button>
                  <button
                    className="delete-button"
                    onClick={() => handleDelete(post.id)}
                  >
                    <FaTrashAlt /> Eliminar
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      <ChatbotWidget />
  </div>
  );
};
