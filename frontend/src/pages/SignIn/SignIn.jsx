import React from 'react';
import { Container, Typography, Button, CircularProgress } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import styles from './SignIn.module.css'; 

const SignIn = () => {
  const { user, loading, signInWithGoogle } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  if (loading) {
    return (
      <Container maxWidth="xlg" className={styles.container}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="xlg" className={styles.container}>
      <Typography variant="h5" component="h5">
        Sign In
      </Typography>
      <Button 
        variant="contained" 
        onClick={signInWithGoogle}
        disabled={loading}
      >
        Sign in with Google
      </Button>
    </Container>
  )
}

export default SignIn;