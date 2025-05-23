import React from 'react';
import { Container } from '@mui/material';
import styles from './SignIn.module.css'; 
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';

const SignIn = () => {
  return (
    <Container maxWidth="xlg" className={styles.container}>
        <Typography variant="h5" component="h5">
            Sign In
        </Typography>
        <Button variant="contained">Sign in with Google</Button>
    </Container>
  )
}

export default SignIn;
