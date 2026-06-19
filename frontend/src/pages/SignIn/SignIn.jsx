import React, { useState } from 'react';
import { Container, Typography, Button, CircularProgress, Box, TextField, Divider, Alert } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import styles from './SignIn.module.css';
import logo from '../../assets/logo.png';
import { API_URL } from '../../config';

const SignIn = () => {
  const { user, loading, signInWithGoogle } = useAuth();
  const navigate = useNavigate();

  // State + handler below power the request-access waitlist, which is currently
  // commented out in the JSX (see note there). Kept so it's easy to re-enable.
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('idle'); // idle | submitting | success | error
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (user) {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  const requestAccess = async (e) => {
    e.preventDefault();
    setStatus('submitting');
    setErrorMsg('');
    try {
      const res = await fetch(`${API_URL}/waitlist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || 'Something went wrong. Please try again.');
      }
      setStatus('success');
      setEmail('');
    } catch (err) {
      setErrorMsg(err.message);
      setStatus('error');
    }
  };

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

        {/*
          Request-access waitlist — hidden for now. The app is in Google
          "Production" mode, so anyone can sign in until the 100-user cap; a
          waitlist only makes sense once we approach that cap. To bring it back,
          uncomment this block (it posts to the backend /waitlist endpoint).

        <Box
            sx={{
                width: '100%',
                maxWidth: 380,
                backgroundColor: '#fff',
                borderRadius: 3,
                boxShadow: 1,
                p: 3,
                textAlign: 'center',
            }}
        >
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 0.5 }}>
                Not on the list yet?
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Glance is invite-only for now. Drop your Gmail and we'll email you once you're added.
            </Typography>

            {status === 'success' ? (
                <Alert severity="success" sx={{ textAlign: 'left' }}>
                    You're on the list! We'll reach out at that email once you're added.
                </Alert>
            ) : (
                <Box
                    component="form"
                    onSubmit={requestAccess}
                    sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}
                >
                    <TextField
                        type="email"
                        required
                        fullWidth
                        size="small"
                        placeholder="you@gmail.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        disabled={status === 'submitting'}
                    />
                    <Button
                        type="submit"
                        variant="contained"
                        disabled={status === 'submitting'}
                        sx={{ textTransform: 'none', fontWeight: 600 }}
                    >
                        {status === 'submitting' ? 'Sending…' : 'Request access'}
                    </Button>
                    {status === 'error' && (
                        <Typography variant="caption" color="error">
                            {errorMsg}
                        </Typography>
                    )}
                </Box>
            )}
        </Box>
        */}
    </Container>
  )
}

export default SignIn;
