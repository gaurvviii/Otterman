import React from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export const showError = (error) => {
  const message = error.response?.data?.detail || error.message || 'An error occurred';
  toast.error(message, {
    position: "top-right",
    autoClose: 5000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true
  });
};

export const ErrorHandler = () => {
  return <ToastContainer />;
};

export const handleApiError = (error, navigate) => {
  if (error.response) {
    switch (error.response.status) {
      case 404:
        showError({ message: 'Resource not found. Please check your request.' });
        break;
      case 401:
        showError({ message: 'Session expired. Please login again.' });
        navigate('/login');
        break;
      case 403:
        showError({ message: 'Access denied. You don\'t have permission to perform this action.' });
        break;
      default:
        showError(error);
    }
  } else {
    showError(error);
  }
};