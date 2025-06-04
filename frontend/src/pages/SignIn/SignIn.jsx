import React from 'react';
import { Container, Typography, Button, CircularProgress, Box } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import styles from './SignIn.module.css'; 
import logo from '../../assets/logo.png';

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
        <Box component="img" src={logo} alt="Glance" sx={{width: {xs:'200px', md:'250px'}, mx:1}} />
        <Typography variant="h6" component="h5" color="text.secondary" sx={{ mb: 2, textAlign: 'center' }}>
             Sign in to take a glance at your Venmo history.
        </Typography>
        <Button
            variant="outlined"
            onClick={signInWithGoogle}
            disabled={loading}
            startIcon={
                <Box
                    component="img"
                    src="https://developers.google.com/identity/images/g-logo.png"
                    alt="Google"
                    sx={{ width: 20, height: 20 }}
                />
            }
            sx={{
                textTransform: 'none',
                color: 'rgba(0, 0, 0, 0.54)',
                borderColor: '#ddd',
                backgroundColor: '#fff',
                '&:hover': {
                backgroundColor: '#f7f7f7',
                borderColor: '#ccc',
                },
                fontWeight: 500,
                fontSize: '14px',
                px: 2,
                py: 1,
                boxShadow: 1,
            }}
        >
            Sign in with Google
        </Button>
    </Container>
  )
}

export default SignIn;